"""Reconciliation worker for automatic transaction status updates."""

import asyncio
from datetime import datetime, timezone
from sqlalchemy import select

from apps.api.core.database import get_db
from apps.api.models.transaction import Transaction, TransactionStatus
from apps.api.models.merchant import MerchantBalance, BalanceTransaction
from apps.api.providers.factory import get_provider
from apps.api.workers.webhook_dispatcher import send_charge_webhook


class ReconciliationWorker:
    """Worker for reconciling transactions with providers."""

    async def reconcile_pending_transactions(self) -> int:
        """
        Reconcile all pending transactions.

        Returns:
            Number of transactions reconciled
        """
        async with get_db() as db:
            result = await db.execute(
                select(Transaction).where(
                    Transaction.status == TransactionStatus.PENDING
                )
            )
            transactions = result.scalars().all()

            reconciled = 0

            for transaction in transactions:
                if transaction.mode == "test":
                    continue

                provider = get_provider(transaction.method)

                try:
                    response = await provider.check_charge_status(
                        transaction.provider_ref
                    )

                    if response.status == "succeeded":
                        transaction.status = TransactionStatus.SUCCEEDED
                        await self._update_balance(db, transaction)
                        await send_charge_webhook(
                            str(transaction.id),
                            str(transaction.merchant_id),
                            "charge.succeeded",
                        )
                        reconciled += 1

                    elif response.status == "failed":
                        transaction.status = TransactionStatus.FAILED
                        transaction.error_code = response.error_code
                        transaction.error_message = response.error_message
                        await send_charge_webhook(
                            str(transaction.id),
                            str(transaction.merchant_id),
                            "charge.failed",
                        )
                        reconciled += 1

                except Exception:
                    pass

            await db.commit()
            return reconciled

    async def _update_balance(self, db, transaction: Transaction) -> None:
        """Update merchant balance after successful transaction."""
        result = await db.execute(
            select(MerchantBalance).where(
                MerchantBalance.merchant_id == transaction.merchant_id
            )
        )
        balance = result.scalar_one_or_none()

        if balance:
            net_amount = transaction.amount - transaction.fee_amount
            balance.available_amount += net_amount

            balance_tx = BalanceTransaction(
                merchant_id=transaction.merchant_id,
                type="charge",
                amount=transaction.amount,
                fee=transaction.fee_amount,
                net=net_amount,
                related_id=transaction.id,
                description=f"Payment from {transaction.phone}",
            )
            db.add(balance_tx)


async def run_reconciliation():
    """Run reconciliation periodically."""
    worker = ReconciliationWorker()

    while True:
        try:
            reconciled = await worker.reconcile_pending_transactions()
            if reconciled > 0:
                print(f"Reconciled {reconciled} transactions")
        except Exception as e:
            print(f"Reconciliation error: {e}")

        await asyncio.sleep(3600)