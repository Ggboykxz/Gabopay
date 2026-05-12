"""Balance endpoints for merchant account balance."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func

from apps.api.core.database import get_db
from apps.api.models.merchant import Merchant, MerchantBalance, BalanceTransaction
from apps.api.api.v1.charges import get_api_key_merchant

router = APIRouter()


class BalanceResponse(BaseModel):
    """Balance response."""
    available: int
    pending: int
    currency: str
    updated_at: int


class BalanceTransactionResponse(BaseModel):
    """Balance transaction response."""
    id: str
    type: str
    amount: int
    fee: int
    net: int
    description: Optional[str]
    created: int


class BalanceTransactionListResponse(BaseModel):
    """List of balance transactions response."""
    data: List[BalanceTransactionResponse]
    has_more: bool
    total: int


@router.get("", response_model=BalanceResponse)
async def get_balance(
    merchant_and_key: tuple = Depends(get_api_key_merchant),
):
    """Get merchant balance."""
    merchant, _, _ = merchant_and_key

    async with get_db() as db:
        result = await db.execute(
            select(MerchantBalance).where(
                MerchantBalance.merchant_id == merchant.id
            )
        )
        balance = result.scalar_one_or_none()

        if not balance:
            balance = MerchantBalance(
                merchant_id=merchant.id,
                available_amount=0,
                pending_amount=0,
            )
            db.add(balance)

        return BalanceResponse(
            available=balance.available_amount,
            pending=balance.pending_amount,
            currency="XAF",
            updated_at=int(balance.updated_at.timestamp()),
        )


@router.get("/transactions", response_model=BalanceTransactionListResponse)
async def list_balance_transactions(
    merchant_and_key: tuple = Depends(get_api_key_merchant),
    limit: int = 20,
    type_filter: Optional[str] = None,
):
    """List balance transactions for the merchant."""
    merchant, _, _ = merchant_and_key

    async with get_db() as db:
        count_query = select(func.count()).select_from(BalanceTransaction).where(
            BalanceTransaction.merchant_id == merchant.id
        )
        if type_filter:
            count_query = count_query.where(BalanceTransaction.type == type_filter)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = select(BalanceTransaction).where(
            BalanceTransaction.merchant_id == merchant.id
        )

        if type_filter:
            query = query.where(BalanceTransaction.type == type_filter)

        query = query.order_by(BalanceTransaction.created_at.desc()).limit(limit + 1)

        result = await db.execute(query)
        transactions = result.scalars().all()
        has_more = len(transactions) > limit
        transactions = transactions[:limit]

        return BalanceTransactionListResponse(
            data=[
                BalanceTransactionResponse(
                    id=str(t.id),
                    type=t.type,
                    amount=t.amount,
                    fee=t.fee,
                    net=t.net,
                    description=t.description,
                    created=int(t.created_at.timestamp()),
                )
                for t in transactions
            ],
            has_more=has_more,
            total=total,
        )