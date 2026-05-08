"""Transaction, Refund, and Payout models."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from apps.api.core.database import Base


class TransactionMethod(str):
    """Payment method constants."""
    AIRTEL_MONEY = "airtel_money"
    MOOV_MONEY = "moov_money"
    CARD = "card"
    CASH = "cash"


class TransactionStatus(str):
    """Transaction status constants."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class TransactionMode(str):
    """Transaction mode (test or live)."""
    TEST = "test"
    LIVE = "live"


class RefundStatus(str):
    """Refund status constants."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PayoutStatus(str):
    """Payout status constants."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Transaction(Base):
    """Transaction model representing a payment."""

    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="XAF")
    method: Mapped[str] = mapped_column(
        SQLEnum(TransactionMethod), nullable=False
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(TransactionStatus), default=TransactionStatus.PENDING
    )
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    provider_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mode: Mapped[str] = mapped_column(
        SQLEnum(TransactionMode), default=TransactionMode.TEST
    )
    fee_amount: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    merchant: Mapped["Merchant"] = Relationship("Merchant", back_populates="transactions")
    refunds: Mapped[list["Refund"]] = Relationship(
        "Refund", back_populates="transaction", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_transactions_merchant_id", "merchant_id"),
        Index("ix_transactions_status", "status"),
        Index("ix_transactions_created_at", "created_at"),
        Index("ix_transactions_idempotency_key", "idempotency_key"),
    )


class Refund(Base):
    """Refund model."""

    __tablename__ = "refunds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(RefundStatus), default=RefundStatus.PENDING
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    transaction: Mapped["Transaction"] = Relationship("Transaction", back_populates="refunds")


class Payout(Base):
    """Payout model for merchant withdrawals."""

    __tablename__ = "payouts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(PayoutStatus), default=PayoutStatus.PENDING
    )
    provider_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    merchant: Mapped["Merchant"] = Relationship("Merchant", back_populates="payouts")

    __table_args__ = (
        Index("ix_payouts_merchant_id", "merchant_id"),
        Index("ix_payouts_status", "status"),
    )