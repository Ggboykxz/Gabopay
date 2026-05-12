"""Card payment provider integration (CinetPay/Stripe)."""

import logging
import httpx
import asyncio
from typing import Optional
import uuid
import hashlib
import hmac

from apps.api.providers.base import (
    BaseProvider,
    PaymentRequest,
    PaymentResponse,
    RefundRequest,
    RefundResponse,
)
from apps.api.core.config import get_settings

logger = logging.getLogger(__name__)


class CardProvider(BaseProvider):
    """Card payment provider (CinetPay for Africa)."""

    def __init__(self, config: dict = None):
        settings = get_settings()
        self.api_key = config.get("api_key", settings.CINETPAY_API_KEY) if config else settings.CINETPAY_API_KEY
        self.site_id = config.get("site_id", settings.CINETPAY_SITE_ID) if config else settings.CINETPAY_SITE_ID
        self.base_url = "https://api.cinetpay.com/v1"
        self._client = httpx.AsyncClient(timeout=30.0)

    def get_provider_type(self) -> str:
        return "card"

    def _generate_signature(self, data: dict) -> str:
        """Generate HMAC-SHA256 signature for CinetPay."""
        sign_data = f"{self.site_id}{data.get('transaction_id')}{data.get('amount')}"
        return hmac.new(
            self.api_key.encode(),
            sign_data.encode(),
            hashlib.sha256
        ).hexdigest()

    async def create_charge(
        self,
        request: PaymentRequest,
        idempotency_key: Optional[str] = None
    ) -> PaymentResponse:
        """Create a card payment."""
        try:
            transaction_id = idempotency_key or str(uuid.uuid4())

            payload = {
                "site_id": self.site_id,
                "transaction_id": transaction_id,
                "amount": request.amount,
                "currency": request.currency,
                "description": request.description or "Payment",
                "return_url": request.metadata.get("return_url") if request.metadata else None,
                "notify_url": request.metadata.get("notify_url") if request.metadata else None,
                "metadata": request.metadata or {},
            }

            payload["signature"] = self._generate_signature(payload)

            for attempt in range(3):
                    try:
                        response = await self._client.post(
                            f"{self.base_url}/payment/init",
                            json=payload,
                        )

                        if response.status_code in (200, 201):
                            data = response.json()
                            if data.get("code") == "201":
                                return PaymentResponse(
                                    success=True,
                                    provider_ref=data.get("transaction_id"),
                                    status="pending",
                                )
                            else:
                                return PaymentResponse(
                                    success=False,
                                    error_code=data.get("code", "api_error"),
                                    error_message=data.get("message", "Payment failed"),
                                    status="failed",
                                )

                    except httpx.TimeoutException:
                        if attempt == 2:
                            return PaymentResponse(
                                success=False,
                                error_code="timeout",
                                error_message="Request timed out",
                                status="failed",
                            )
                        await asyncio.sleep(2 ** attempt)
                    except httpx.HTTPError as e:
                        if attempt == 2:
                            return PaymentResponse(
                                success=False,
                                error_code="network_error",
                                error_message=str(e),
                                status="failed",
                            )
                        await asyncio.sleep(2 ** attempt)

        except Exception as e:
            return PaymentResponse(
                success=False,
                error_code="internal_error",
                error_message=str(e),
                status="failed",
            )

    async def check_charge_status(self, provider_ref: str) -> PaymentResponse:
        """Check card payment status."""
        try:
            payload = {
                "site_id": self.site_id,
                "transaction_id": provider_ref,
            }
            payload["signature"] = self._generate_signature(payload)

            response = await self._client.post(
                f"{self.base_url}/payment/check",
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                status_map = {
                    "00": "succeeded",
                    "pending": "pending",
                    "failed": "failed",
                }
                return PaymentResponse(
                    success=data.get("code") == "00",
                    provider_ref=provider_ref,
                    status=status_map.get(str(data.get("code")), "unknown"),
                )

        except Exception as e:
            logger.error(f"Card check_charge_status error: {e}")

        return PaymentResponse(success=False, status="unknown")

    async def create_refund(self, request: RefundRequest) -> RefundResponse:
        """Create a refund for card payment."""
        try:
            payload = {
                "site_id": self.site_id,
                "transaction_id": request.provider_ref,
                "amount": request.amount,
                "reason": request.reason,
            }
            payload["signature"] = self._generate_signature(payload)

            response = await self._client.post(
                f"{self.base_url}/payment/refund",
                json=payload,
            )

            if response.status_code in (200, 201):
                data = response.json()
                return RefundResponse(
                    success=data.get("code") == "00",
                    provider_ref=f"refund_{request.provider_ref}",
                )

        except Exception as e:
            logger.error(f"Card refund error: {e}")
            return RefundResponse(
                success=False,
                error_message=str(e),
            )

        return RefundResponse(success=False)

    async def create_payout(
        self,
        amount: int,
        phone: str,
        reference: str
    ) -> PaymentResponse:
        """Card providers don't support direct payouts to phone."""
        return PaymentResponse(
            success=False,
            error_code="not_supported",
            error_message="Card payouts not supported. Use mobile money provider.",
            status="failed",
        )


def get_card_provider() -> CardProvider:
    """Get card provider instance."""
    return CardProvider()