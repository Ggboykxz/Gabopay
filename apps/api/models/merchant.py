"""Merchant, API Key, and Webhook models."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from apps.api.core.database import Base


class MerchantStatus(str):
    """Merchant status constants."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class KYCStatus(str):
    """KYC verification status constants."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Merchant(Base):
    """Merchant account model."""

    __tablename__ = "merchants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(2), default="GA")
    status: Mapped[str] = mapped_column(
        SQLEnum(MerchantStatus),
        default=MerchantStatus.PENDING,
    )
    kyc_status: Mapped[str] = mapped_column(
        SQLEnum(KYCStatus),
        default=KYCStatus.PENDING,
    )
    kyc_documents: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    two_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    api_keys: Mapped[list["ApiKey"]] = Relationship(
        "ApiKey", back_populates="merchant", cascade="all, delete-orphan"
    )
    webhook_endpoints: Mapped[list["WebhookEndpoint"]] = Relationship(
        "WebhookEndpoint", back_populates="merchant", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = Relationship(
        "Transaction", back_populates="merchant"
    )
    payouts: Mapped[list["Payout"]] = Relationship(
        "Payout", back_populates="merchant"
    )
    balance: Mapped[Optional["MerchantBalance"]] = Relationship(
        "MerchantBalance", back_populates="merchant", uselist=False
    )


class ApiKey(Base):
    """API Key model."""

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    prefix: Mapped[str] = mapped_column(String(20), nullable=False)
    mode: Mapped[str] = mapped_column(String(10), nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    merchant: Mapped["Merchant"] = Relationship("Merchant", back_populates="api_keys")


class WebhookEndpoint(Base):
    """Webhook endpoint configuration."""

    __tablename__ = "webhook_endpoints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    events: Mapped[list] = mapped_column(JSONB, default=list)
    secret_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    merchant: Mapped["Merchant"] = Relationship("Merchant", back_populates="webhook_endpoints")
    deliveries: Mapped[list["WebhookDelivery"]] = Relationship(
        "WebhookDelivery", back_populates="endpoint", cascade="all, delete-orphan"
    )


class MerchantBalance(Base):
    """Merchant balance tracking."""

    __tablename__ = "merchant_balances"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id"), primary_key=True
    )
    available_amount: Mapped[int] = mapped_column(default=0)
    pending_amount: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    merchant: Mapped["Merchant"] = Relationship("Merchant", back_populates="balance")


class BalanceTransaction(Base):
    """Balance transaction history."""

    __tablename__ = "balance_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    fee: Mapped[int] = mapped_column(default=0)
    net: Mapped[int] = mapped_column(nullable=False)
    related_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class WebhookDelivery(Base):
    """Webhook delivery attempt logging."""

    __tablename__ = "webhook_deliveries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("webhook_endpoints.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    response_status: Mapped[Optional[int]] = mapped_column(nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attempt: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    endpoint: Mapped["WebhookEndpoint"] = Relationship("WebhookEndpoint", back_populates="deliveries")