"""Payout endpoints for merchant withdrawals."""

import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from apps.api.core.database import get_db
from apps.api.models.merchant import Merchant, MerchantBalance, BalanceTransaction
from apps.api.models.transaction import Payout, PayoutStatus
from apps.api.providers.factory import get_provider
from apps.api.providers.base import PaymentRequest
from apps.api.api.v1.charges import get_api_key_merchant
from apps.api.providers.factory import calculate_fee

router = APIRouter()


class PayoutCreateRequest(BaseModel):
    """Request to create a payout."""
    amount: int = Field(..., gt=0, description="Amount to withdraw in XAF")
    method: str = Field(..., description="Payout method: airtel_money, moov_money")
    phone: str = Field(..., description="Phone number for payout")


class PayoutResponse(BaseModel):
    """Payout response."""
    id: str
    object: str = "payout"
    amount: int
    method: str
    phone: str
    status: str
    created: int


class PayoutListResponse(BaseModel):
    """List of payouts response."""
    data: List[PayoutResponse]
    has_more: bool
    total: int


@router.post("", response_model=PayoutResponse, status_code=status.HTTP_201_CREATED)
async def create_payout(
    request: PayoutCreateRequest,
    merchant_and_key: tuple = Depends(get_api_key_merchant),
):
    """Create a payout request."""
    merchant, _, _ = merchant_and_key

    if request.method not in ["airtel_money", "moov_money"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payout method. Use airtel_money or moov_money",
        )

    async with get_db() as db:
        result = await db.execute(
            select(MerchantBalance).where(
                MerchantBalance.merchant_id == merchant.id
            )
        )
        balance = result.scalar_one_or_none()

        if not balance or balance.available_amount < request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance",
            )

        provider = get_provider(request.method)

        payout = Payout(
            merchant_id=merchant.id,
            amount=request.amount,
            method=request.method,
            phone=request.phone,
            status=PayoutStatus.PENDING,
        )
        db.add(payout)
        await db.flush()

        balance.available_amount -= request.amount

        fee = calculate_fee(request.amount, request.method)
        net_amount = request.amount - fee

        balance_tx = BalanceTransaction(
            merchant_id=merchant.id,
            type="payout",
            amount=request.amount,
            fee=fee,
            net=-net_amount,
            related_id=payout.id,
            description=f"Payout to {request.phone}",
        )
        db.add(balance_tx)

        try:
            response = await provider.create_payout(
                amount=request.amount,
                phone=request.phone,
                reference=str(payout.id),
            )

            if response.success:
                payout.status = PayoutStatus.SUCCEEDED
                payout.provider_ref = response.provider_ref
            else:
                payout.status = PayoutStatus.FAILED
                payout.error_message = response.error_message
                balance.available_amount += request.amount

        except Exception as e:
            payout.status = PayoutStatus.FAILED
            payout.error_message = str(e)
            balance.available_amount += request.amount

        await db.commit()

        return PayoutResponse(
            id=str(payout.id),
            object="payout",
            amount=payout.amount,
            method=payout.method,
            phone=payout.phone[-4:].rjust(len(payout.phone), "*"),
            status=payout.status,
            created=int(payout.created_at.timestamp()),
        )


@router.get("", response_model=PayoutListResponse)
async def list_payouts(
    merchant_and_key: tuple = Depends(get_api_key_merchant),
    limit: int = 20,
):
    """List payouts for the merchant."""
    merchant, _, _ = merchant_and_key

    async with get_db() as db:
        result = await db.execute(
            select(Payout)
            .where(Payout.merchant_id == merchant.id)
            .order_by(Payout.created_at.desc())
            .limit(limit)
        )
        payouts = result.scalars().all()

        return PayoutListResponse(
            data=[
                PayoutResponse(
                    id=str(p.id),
                    object="payout",
                    amount=p.amount,
                    method=p.method,
                    phone=p.phone[-4:].rjust(len(p.phone), "*"),
                    status=p.status,
                    created=int(p.created_at.timestamp()),
                )
                for p in payouts
            ],
            has_more=len(payouts) == limit,
            total=len(payouts),
        )


@router.get("/{payout_id}", response_model=PayoutResponse)
async def get_payout(
    payout_id: uuid.UUID,
    merchant_and_key: tuple = Depends(get_api_key_merchant),
):
    """Get a payout by ID."""
    merchant, _, _ = merchant_and_key

    async with get_db() as db:
        result = await db.execute(
            select(Payout).where(
                Payout.id == payout_id,
                Payout.merchant_id == merchant.id,
            )
        )
        payout = result.scalar_one_or_none()

        if not payout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payout not found",
            )

        return PayoutResponse(
            id=str(payout.id),
            object="payout",
            amount=payout.amount,
            method=payout.method,
            phone=payout.phone[-4:].rjust(len(payout.phone), "*"),
            status=payout.status,
            created=int(payout.created_at.timestamp()),
        )