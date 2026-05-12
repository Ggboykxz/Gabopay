"""Base provider interface for payment integrations."""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import uuid


@dataclass
class PaymentRequest:
    """Payment request data."""
    amount: int
    currency: str
    phone: str
    description: Optional[str] = None
    metadata: Optional[dict] = None
    external_ref: Optional[str] = None


@dataclass
class PaymentResponse:
    """Payment response from provider."""
    success: bool
    provider_ref: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    status: str = "pending"


@dataclass
class RefundRequest:
    """Refund request data."""
    amount: int
    provider_ref: str
    reason: Optional[str] = None


@dataclass
class RefundResponse:
    """Refund response from provider."""
    success: bool
    provider_ref: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class BaseProvider(ABC):
    """Abstract base class for payment providers."""

    def __init__(self, config: dict):
        """
        Initialize provider with configuration.

        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config

    @abstractmethod
    async def create_charge(
        self,
        request: PaymentRequest,
        idempotency_key: Optional[str] = None
    ) -> PaymentResponse:
        """
        Create a payment charge.

        Args:
            request: Payment request details
            idempotency_key: Optional idempotency key

        Returns:
            PaymentResponse from the provider
        """
        pass

    @abstractmethod
    async def check_charge_status(self, provider_ref: str) -> PaymentResponse:
        """
        Check the status of an existing charge.

        Args:
            provider_ref: The provider's reference for the charge

        Returns:
            PaymentResponse with current status
        """
        pass

    @abstractmethod
    async def create_refund(self, request: RefundRequest) -> RefundResponse:
        """
        Create a refund.

        Args:
            request: Refund request details

        Returns:
            RefundResponse from the provider
        """
        pass

    @abstractmethod
    async def create_payout(
        self,
        amount: int,
        phone: str,
        reference: str
    ) -> PaymentResponse:
        """
        Create a payout to a phone number.

        Args:
            amount: Amount in smallest currency unit
            phone: Phone number for payout
            reference: External reference

        Returns:
            PaymentResponse from the provider
        """
        pass

    @abstractmethod
    def get_provider_type(self) -> str:
        """Get the provider type identifier."""
        pass


def simulate_test_payment(phone: str, amount: int) -> PaymentResponse:
    """
    Simulate test payments for gp_test keys.

    Test numbers:
    - +24100000001 -> Always SUCCESS
    - +24100000002 -> Always FAILED (insufficient_funds)
    - +24100000003 -> Timeout simulation (30s)
    """
    test_numbers = {
        "+24100000001": ("succeeded", None, None),
        "+24100000002": ("failed", "insufficient_funds", "Insufficient funds"),
        "+24100000003": ("pending", None, None),  # Timeout handled by caller
    }

    if phone in test_numbers:
        status, error_code, error_message = test_numbers[phone]
        return PaymentResponse(
            success=status == "succeeded",
            provider_ref=f"test_{uuid.uuid4().hex[:12]}",
            error_code=error_code,
            error_message=error_message,
            status=status,
        )

    # Default: random success/fail for other test numbers
    if random.random() > 0.1:
        return PaymentResponse(
            success=True,
            provider_ref=f"test_{uuid.uuid4().hex[:12]}",
            status="succeeded",
        )
    else:
        return PaymentResponse(
            success=False,
            provider_ref=f"test_{uuid.uuid4().hex[:12]}",
            error_code="insufficient_funds",
            error_message="Insufficient funds",
            status="failed",
        )