"""Refund endpoints."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field
from sqlalchemy import select

from apps.api.core.database import get_db
from apps.api.core.security import parse_api_key
from apps.api.models.merchant import Merchant, ApiKey
from apps.api.models.transaction import Transaction, Refund, TransactionStatus, RefundStatus
from apps.api.providers.factory import get_provider
from apps.api.providers.base import RefundRequest
from apps.api.api.v1.charges import get_api_key_merchant

router = APIRouter()


class RefundCreateRequest(BaseModel):
    """Request to create a refund."""
    amount: int = Field(..., gt=0, description="Amount to refund in XAF")
    reason: Optional[str] = Field(None, description="Reason for refund")


class RefundResponse(BaseModel):
    """Refund response."""
    id: str
    object: str = "refund"
    amount: int
    status: str
    reason: Optional[str]
    transaction_id: str
    created: int


class RefundListResponse(BaseModel):
    """List of refunds response."""
    data: List[RefundResponse]
    has_more: bool
    total: int


@router.post("", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
async def create_refund(
    transaction_id: uuid.UUID,
    request: RefundCreateRequest,
    merchant_and_key: tuple = Depends(get_api_key_merchant),
):
    """Create a refund for a transaction."""
    merchant, _, _ = merchant_and_key

    async with get_db() as db:
        result = await db.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.merchant_id == merchant.id,
            )
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )

        if transaction.status != TransactionStatus.SUCCEEDED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only refund successful transactions",
            )

        if request.amount > transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund amount exceeds transaction amount",
            )

        provider = get_provider(transaction.method)

        refund = Refund(
            transaction_id=transaction.id,
            amount=request.amount,
            status=RefundStatus.PENDING,
            reason=request.reason,
        )
        db.add(refund)
        await db.flush()

        try:
            response = await provider.create_refund(
                RefundRequest(
                    amount=request.amount,
                    provider_ref=transaction.provider_ref,
                    reason=request.reason,
                )
            )

            if response.success:
                refund.status = RefundStatus.SUCCEEDED
                refund.provider_ref = response.provider_ref
                transaction.status = TransactionStatus.REFUNDED
            else:
                refund.status = RefundStatus.FAILED
                refund.error_message = response.error_message

        except Exception as e:
            refund.status = RefundStatus.FAILED
            refund.error_message = str(e)

        await db.commit()

        return RefundResponse(
            id=str(refund.id),
            object="refund",
            amount=refund.amount,
            status=refund.status,
            reason=refund.reason,
            transaction_id=str(transaction.id),
            created=int(refund.created_at.timestamp()),
        )


@router.get("/{refund_id}", response_model=RefundResponse)
async def get_refund(
    refund_id: uuid.UUID,
    merchant_and_key: tuple = Depends(get_api_key_merchant),
):
    """Get a refund by ID."""
    merchant, _, _ = merchant_and_key

    async with get_db() as db:
        result = await db.execute(
            select(Refund).where(Refund.id == refund_id)
        )
        refund = result.scalar_one_or_none()

        if not refund:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refund not found",
            )

        result = await db.execute(
            select(Transaction).where(
                Transaction.id == refund.transaction_id,
                Transaction.merchant_id == merchant.id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refund not found",
            )

        return RefundResponse(
            id=str(refund.id),
            object="refund",
            amount=refund.amount,
            status=refund.status,
            reason=refund.reason,
            transaction_id=str(refund.transaction_id),
            created=int(refund.created_at.timestamp()),
        )