"""Airtel Money provider integration."""

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


class AirtelMoneyProvider(BaseProvider):
    """Airtel Money provider implementation for Gabon."""

    def __init__(self, config: dict = None):
        settings = get_settings()
        self.base_url = config.get("base_url", settings.AIRTEL_BASE_URL)
        self.client_id = config.get("client_id", settings.AIRTEL_CLIENT_ID)
        self.client_secret = config.get("client_secret", settings.AIRTEL_CLIENT_SECRET)
        self.callback_url = config.get("callback_url", settings.AIRTEL_CALLBACK_URL)
        self._token: Optional[str] = None
        self._token_expires_at: float = 0

    async def _get_token(self) -> str:
        """Get or refresh Airtel API token."""
        import time
        if self._token and time.time() < self._token_expires_at:
            return self._token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/oauth2/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            self._token = data["access_token"]
            self._token_expires_at = time.time() + data.get("expires_in", 3600) - 60
            return self._token

    def get_provider_type(self) -> str:
        return "airtel_money"

    async def create_charge(
        self,
        request: PaymentRequest,
        idempotency_key: Optional[str] = None
    ) -> PaymentResponse:
        """Create a payment charge via Airtel Money."""
        try:
            token = await self._get_token()

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            payload = {
                "reference": idempotency_key or str(uuid.uuid4()),
                "subscriber": {
                    "country": "GA",
                    "msisdn": request.phone.replace("+241", ""),
                },
                "transaction": {
                    "amount": str(request.amount),
                    "currency": request.currency,
                    "country": "GA",
                },
                "description": request.description or "Payment",
            }

            async with httpx.AsyncClient() as client:
                for attempt in range(3):
                    try:
                        response = await client.post(
                            f"{self.base_url}/merchant/v1/payments",
                            json=payload,
                            headers=headers,
                            timeout=30.0,
                        )

                        if response.status_code == 200:
                            data = response.json()
                            if data.get("status") == "SUCCESS":
                                return PaymentResponse(
                                    success=True,
                                    provider_ref=data.get("transaction_ref"),
                                    status="succeeded",
                                )
                            elif data.get("status") == "PENDING":
                                return PaymentResponse(
                                    success=True,
                                    provider_ref=data.get("transaction_ref"),
                                    status="pending",
                                )
                            else:
                                return PaymentResponse(
                                    success=False,
                                    error_code=data.get("error_code", "unknown"),
                                    error_message=data.get("message", "Payment failed"),
                                    status="failed",
                                )
                        else:
                            error_data = response.json() if response.text else {}
                            return PaymentResponse(
                                success=False,
                                error_code=error_data.get("error_code", "api_error"),
                                error_message=error_data.get("message", "API error"),
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
        """Check the status of an Airtel Money transaction."""
        try:
            token = await self._get_token()
            headers = {"Authorization": f"Bearer {token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/merchant/v1/payments/{provider_ref}",
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    status_map = {
                        "SUCCESS": "succeeded",
                        "PENDING": "pending",
                        "FAILED": "failed",
                    }
                    return PaymentResponse(
                        success=data.get("status") == "SUCCESS",
                        provider_ref=provider_ref,
                        status=status_map.get(data.get("status", ""), "unknown"),
                    )

        except Exception:
            pass

        return PaymentResponse(
            success=False,
            status="unknown",
        )

    async def create_refund(self, request: RefundRequest) -> RefundResponse:
        """Create a refund for an Airtel Money transaction."""
        try:
            token = await self._get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            payload = {
                "transaction_ref": request.provider_ref,
                "refund_amount": str(request.amount),
                "reason": request.reason or "Refund requested",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/merchant/v1/refunds",
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return RefundResponse(
                        success=data.get("status") == "SUCCESS",
                        provider_ref=data.get("refund_ref"),
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
        """Create a payout (disbursement) via Airtel Money."""
        try:
            token = await self._get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            payload = {
                "reference": reference,
                "subscriber": {
                    "country": "GA",
                    "msisdn": phone.replace("+241", ""),
                },
                "transaction": {
                    "amount": str(amount),
                    "currency": "XAF",
                    "country": "GA",
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/merchant/v1/disbursements",
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return PaymentResponse(
                        success=data.get("status") == "SUCCESS",
                        provider_ref=data.get("transaction_ref"),
                        status="succeeded" if data.get("status") == "SUCCESS" else "pending",
                    )

        except Exception as e:
            return PaymentResponse(
                success=False,
                error_message=str(e),
                status="failed",
            )

        return PaymentResponse(success=False, status="failed")


def get_airtel_provider(mode: str = "test", test_phone: str = None) -> AirtelMoneyProvider:
    """Get Airtel provider instance (with test mode support)."""
    if mode == "test" and test_phone:
        return _SimulatedAirtelProvider()

    return AirtelMoneyProvider()


class _SimulatedAirtelProvider(AirtelMoneyProvider):
    """Simulated Airtel provider for test mode."""

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