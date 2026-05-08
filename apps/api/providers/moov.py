"""Moov Money provider integration."""

import httpx
import asyncio
from typing import Optional
import uuid

from apps.api.providers.base import (
    BaseProvider,
    PaymentRequest,
    PaymentResponse,
    RefundRequest,
    RefundResponse,
    simulate_test_payment,
)
from apps.api.core.config import get_settings


class MoovMoneyProvider(BaseProvider):
    """Moov Money provider implementation for Gabon."""

    def __init__(self, config: dict = None):
        settings = get_settings()
        self.base_url = config.get("base_url", settings.MOOV_BASE_URL)
        self.api_key = config.get("api_key", settings.MOOV_API_KEY)
        self.callback_url = config.get("callback_url", settings.MOOV_CALLBACK_URL)

    def get_provider_type(self) -> str:
        return "moov_money"

    def _get_headers(self) -> dict:
        """Get headers for Moov API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_charge(
        self,
        request: PaymentRequest,
        idempotency_key: Optional[str] = None
    ) -> PaymentResponse:
        """Create a payment charge via Moov Money."""
        try:
            headers = self._get_headers()

            payload = {
                "amount": request.amount,
                "currency": request.currency,
                "phone": request.phone,
                "reference": idempotency_key or str(uuid.uuid4()),
                "description": request.description,
                "callback_url": self.callback_url,
                "metadata": request.metadata or {},
            }

            async with httpx.AsyncClient() as client:
                for attempt in range(3):
                    try:
                        response = await client.post(
                            f"{self.base_url}/collect",
                            json=payload,
                            headers=headers,
                            timeout=30.0,
                        )

                        if response.status_code in (200, 201):
                            data = response.json()
                            return PaymentResponse(
                                success=data.get("status") in ("success", "pending"),
                                provider_ref=data.get("transaction_id"),
                                status=data.get("status", "pending"),
                            )
                        else:
                            error_data = response.json() if response.text else {}
                            return PaymentResponse(
                                success=False,
                                error_code=error_data.get("code", "api_error"),
                                error_message=error_data.get("message", "Payment failed"),
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
        """Check the status of a Moov Money transaction."""
        try:
            headers = self._get_headers()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/status/{provider_ref}",
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    status_map = {
                        "success": "succeeded",
                        "pending": "pending",
                        "failed": "failed",
                    }
                    return PaymentResponse(
                        success=data.get("status") == "success",
                        provider_ref=provider_ref,
                        status=status_map.get(data.get("status", ""), "unknown"),
                    )

        except Exception:
            pass

        return PaymentResponse(success=False, status="unknown")

    async def create_refund(self, request: RefundRequest) -> RefundResponse:
        """Create a refund for a Moov Money transaction."""
        try:
            headers = self._get_headers()

            payload = {
                "transaction_id": request.provider_ref,
                "amount": request.amount,
                "reason": request.reason,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/refund",
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code in (200, 201):
                    data = response.json()
                    return RefundResponse(
                        success=data.get("status") == "success",
                        provider_ref=data.get("refund_id"),
                    )

        except Exception as e:
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
        """Create a payout via Moov Money."""
        try:
            headers = self._get_headers()

            payload = {
                "amount": amount,
                "phone": phone,
                "reference": reference,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/disburse",
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code in (200, 201):
                    data = response.json()
                    return PaymentResponse(
                        success=data.get("status") == "success",
                        provider_ref=data.get("transaction_id"),
                        status="succeeded",
                    )

        except Exception as e:
            return PaymentResponse(
                success=False,
                error_message=str(e),
                status="failed",
            )

        return PaymentResponse(success=False, status="failed")


def get_moov_provider(mode: str = "test", test_phone: str = None) -> MoovMoneyProvider:
    """Get Moov provider instance (with test mode support)."""
    if mode == "test" and test_phone:
        return _SimulatedMoovProvider()

    return MoovMoneyProvider()


class _SimulatedMoovProvider(MoovMoneyProvider):
    """Simulated Moov provider for test mode."""

    async def create_charge(
        self,
        request: PaymentRequest,
        idempotency_key: Optional[str] = None
    ) -> PaymentResponse:
        return simulate_test_payment(request.phone, request.amount)

    async def check_charge_status(self, provider_ref: str) -> PaymentResponse:
        return PaymentResponse(success=True, provider_ref=provider_ref, status="succeeded")

    async def create_refund(self, request: RefundRequest) -> RefundResponse:
        return RefundResponse(success=True, provider_ref=f"refund_{uuid.uuid4().hex[:12]}")

    async def create_payout(self, amount: int, phone: str, reference: str) -> PaymentResponse:
        return PaymentResponse(success=True, provider_ref=f"payout_{uuid.uuid4().hex[:12]}", status="succeeded")