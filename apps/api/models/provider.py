"""Provider account and configuration models."""

import uuid
from enum import Enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from apps.api.core.database import Base


class ProviderType(str, Enum):
    """Provider type constants."""
    AIRTEL_MONEY = "airtel_money"
    MOOV_MONEY = "moov_money"
    CARD = "card"


class ProviderAccount(Base):
    """Provider account credentials (encrypted)."""

    __tablename__ = "provider_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False)
    credentials_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    api_base_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    callback_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class FeeConfiguration(Base):
    """Fee configuration by payment method."""

    __tablename__ = "fee_configurations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False)
    percentage: Mapped[float] = mapped_column(default=1.5)
    fixed_amount: Mapped[int] = mapped_column(default=0)
    minimum_fee: Mapped[int] = mapped_column(default=50)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


# Import Merchant for relationship resolution
from apps.api.models.merchant import Merchant  # noqa: E402