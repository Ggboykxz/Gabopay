"""Charge endpoints for creating and managing payments."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field
from sqlalchemy import select

from apps.api.core.database import get_db
from apps.api.core.security import parse_api_key, verify_api_key, mask_sensitive_data
from apps.api.core.config import get_settings
from apps.api.models.merchant import Merchant, ApiKey
from apps.api.models.transaction import Transaction, TransactionStatus, TransactionMethod, TransactionMode
from apps.api.models.provider import FeeConfiguration
from apps.api.providers.factory import get_provider, calculate_fee
from apps.api.providers.base import PaymentRequest

router = APIRouter()


class ChargeCreateRequest(BaseModel):
    """Request to create a charge."""
    amount: int = Field(..., gt=0, description="Amount in XAF")
    currency: str = Field(default="XAF", description="Currency code")
    method: str = Field(..., description="Payment method: airtel_money, moov_money, card")
    phone: Optional[str] = Field(None, description="Phone number for mobile money")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[dict] = Field(default_factory=dict, description="Custom metadata")


class ChargeResponse(BaseModel):
    """Charge response."""
    id: str
    object: str = "charge"
    amount: int
    currency: str
    status: str
    method: str
    phone: Optional[str]
    description: Optional[str]
    metadata: Optional[dict]
    fee_amount: int
    created: int


class ChargeListResponse(BaseModel):
    """List of charges response."""
    data: List[ChargeResponse]
    has_more: bool
    total: int


async def get_api_key_merchant(
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> tuple[Merchant, ApiKey, str]:
    """Validate API key and get associated merchant."""
    settings = get_settings()

    key_info = parse_api_key(x_api_key)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
        )

    prefix, mode = key_info
    key_hash = uuid.uuid4().hex

    async with get_db() as db:
        result = await db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            for row in await db.execute(select(ApiKey)):
                if verify_api_key(x_api_key, row.key_hash):
                    api_key = row
                    break

        if not api_key or api_key.revoked_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked API key",
            )

        api_key.last_used_at = datetime.now(timezone.utc)

        result = await db.execute(
            select(Merchant).where(Merchant.id == api_key.merchant_id)
        )
        merchant = result.scalar_one_or_none()

        if not merchant or merchant.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Merchant not active",
            )

        return merchant, api_key, mode


@router.post("", response_model=ChargeResponse, status_code=status.HTTP_201_CREATED)
async def create_charge(
    request: ChargeCreateRequest,
    merchant_and_key: tuple = Depends(get_api_key_merchant),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """Create a new payment charge."""
    settings = get_settings()
    merchant, api_key, mode = merchant_and_key

    if request.amount < settings.MIN_CHARGE_AMOUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Amount must be at least {settings.MIN_CHARGE_AMOUNT} XAF",
        )

    if request.amount > settings.MAX_CHARGE_AMOUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Amount cannot exceed {settings.MAX_CHARGE_AMOUNT} XAF",
        )

    if request.method not in ["airtel_money", "moov_money", "card"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method",
        )

    if request.method in ["airtel_money", "moov_money"] and not request.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number required for mobile money payments",
        )

    if idempotency_key:
        async with get_db() as db:
            result = await db.execute(
                select(Transaction).where(
                    Transaction.idempotency_key == idempotency_key
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                return ChargeResponse(
                    id=str(existing.id),
                    object="charge",
                    amount=existing.amount,
                    currency=existing.currency,
                    status=existing.status,
                    method=existing.method,
                    phone=existing.phone,
                    description=existing.description,
                    metadata=existing.metadata,
                    fee_amount=existing.fee_amount,
                    created=int(existing.created_at.timestamp()),
                )

    fee_amount = calculate_fee(request.amount, request.method)

    async with get_db() as db:
        transaction = Transaction(
            merchant_id=merchant.id,
            amount=request.amount,
            currency=request.currency,
            method=request.method,
            status=TransactionStatus.PENDING,
            phone=request.phone,
            description=request.description,
            metadata=request.metadata,
            idempotency_key=idempotency_key,
            fee_amount=fee_amount,
            mode=TransactionMode.TEST if mode == "test" else TransactionMode.LIVE,
        )
        db.add(transaction)
        await db.flush()

        provider = get_provider(
            request.method,
            mode=mode,
            test_phone=request.phone,
        )

        payment_request = PaymentRequest(
            amount=request.amount,
            currency=request.currency,
            phone=request.phone,
            description=request.description,
            metadata=request.metadata,
            external_ref=str(transaction.id),
        )

        try:
            response = await provider.create_charge(
                payment_request,
                idempotency_key=idempotency_key,
            )

            transaction.provider_ref = response.provider_ref

            if response.success:
                if response.status == "succeeded":
                    transaction.status = TransactionStatus.SUCCEEDED
                else:
                    transaction.status = TransactionStatus.PENDING
            else:
                transaction.status = TransactionStatus.FAILED
                transaction.error_code = response.error_code
                transaction.error_message = response.error_message

        except Exception as e:
            transaction.status = TransactionStatus.FAILED
            transaction.error_code = "provider_error"
            transaction.error_message = str(e)

        await db.commit()

        return ChargeResponse(
            id=str(transaction.id),
            object="charge",
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            method=transaction.method,
            phone=mask_sensitive_data(transaction.phone) if transaction.phone else None,
            description=transaction.description,
            metadata=transaction.metadata,
            fee_amount=transaction.fee_amount,
            created=int(transaction.created_at.timestamp()),
        )


@router.get("/{charge_id}", response_model=ChargeResponse)
async def get_charge(
    charge_id: uuid.UUID,
    merchant_and_key: tuple = Depends(get_api_key_merchant),
):
    """Get a charge by ID."""
    merchant, _, _ = merchant_and_key

    async with get_db() as db:
        result = await db.execute(
            select(Transaction).where(
                Transaction.id == charge_id,
                Transaction.merchant_id == merchant.id,
            )
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Charge not found",
            )

        return ChargeResponse(
            id=str(transaction.id),
            object="charge",
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            method=transaction.method,
            phone=mask_sensitive_data(transaction.phone) if transaction.phone else None,
            description=transaction.description,
            metadata=transaction.metadata,
            fee_amount=transaction.fee_amount,
            created=int(transaction.created_at.timestamp()),
        )


@router.get("", response_model=ChargeListResponse)
async def list_charges(
    merchant_and_key: tuple = Depends(get_api_key_merchant),
    limit: int = 20,
    before: Optional[uuid.UUID] = None,
    after: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = None,
):
    """List charges for the merchant."""
    merchant, _, _ = merchant_and_key

    async with get_db() as db:
        query = select(Transaction).where(
            Transaction.merchant_id == merchant.id
        )

        if status_filter:
            query = query.where(Transaction.status == status_filter)

        query = query.order_by(Transaction.created_at.desc()).limit(limit)

        result = await db.execute(query)
        transactions = result.scalars().all()

        return ChargeListResponse(
            data=[
                ChargeResponse(
                    id=str(t.id),
                    object="charge",
                    amount=t.amount,
                    currency=t.currency,
                    status=t.status,
                    method=t.method,
                    phone=mask_sensitive_data(t.phone) if t.phone else None,
                    description=t.description,
                    metadata=t.metadata,
                    fee_amount=t.fee_amount,
                    created=int(t.created_at.timestamp()),
                )
                for t in transactions
            ],
            has_more=len(transactions) == limit,
            total=len(transactions),
        )