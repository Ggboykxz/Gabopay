"""GABOPAY SDK Types"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChargeCreateOptions:
    """Options for creating a charge."""
    amount: int
    method: str
    currency: str = "XAF"
    phone: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


@dataclass
class Charge:
    """Charge object."""
    id: str
    object: str
    amount: int
    currency: str
    status: str
    method: str
    phone: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None
    fee_amount: int = 0
    created: int = 0


@dataclass
class RefundCreateOptions:
    """Options for creating a refund."""
    amount: int
    reason: Optional[str] = None


@dataclass
class Refund:
    """Refund object."""
    id: str
    object: str
    amount: int
    status: str
    reason: Optional[str] = None
    transaction_id: str = ""
    created: int = 0


@dataclass
class PayoutCreateOptions:
    """Options for creating a payout."""
    amount: int
    method: str
    phone: str


@dataclass
class Payout:
    """Payout object."""
    id: str
    object: str
    amount: int
    method: str
    phone: str
    status: str
    created: int = 0


@dataclass
class Balance:
    """Balance object."""
    available: int
    pending: int
    currency: str
    updated_at: int


@dataclass
class WebhookEventData:
    """Webhook event data object."""
    id: str
    amount: int
    currency: str
    status: str
    method: str
    metadata: Optional[dict] = None


@dataclass
class WebhookEvent:
    """Webhook event object."""
    id: str
    object: str
    type: str
    data: WebhookEventData
    created: int