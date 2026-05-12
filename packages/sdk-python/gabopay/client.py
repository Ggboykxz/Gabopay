"""GABOPAY Python SDK Client"""

import json
import hmac
import hashlib
import time
from typing import Optional, cast
from dataclasses import dataclass, asdict

import httpx

from gabopay.errors import GabopayError, WebhookVerificationError
from gabopay.types import (
    ChargeCreateOptions,
    Charge,
    RefundCreateOptions,
    Refund,
    PayoutCreateOptions,
    Payout,
    Balance,
    WebhookEvent,
)


DEFAULT_BASE_URL = "https://api.gabopay.ga"
DEFAULT_TIMEOUT = 60.0


@dataclass
class Gabopay:
    """GABOPAY SDK Client"""

    secret_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = 3

    def __post_init__(self):
        if not self.secret_key:
            raise GabopayError("secret_key is required")
        self._client = httpx.Client(timeout=self.timeout)

    def _get_headers(self) -> dict:
        """Get request headers."""
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.secret_key,
        }

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
    ) -> dict:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}{path}"
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    json=body,
                    headers=self._get_headers(),
                )

                if response.status_code >= 500:
                    raise GabopayError(
                        message=f"HTTP {response.status_code}",
                        status_code=response.status_code,
                    )

                if response.status_code >= 400:
                    error_data = response.json() if response.text else {}
                    raise GabopayError(
                        message=error_data.get("error", {}).get("message", f"HTTP {response.status_code}"),
                        status_code=response.status_code,
                        code=error_data.get("error", {}).get("code"),
                    )

                return response.json()

            except GabopayError as e:
                if e.status_code and e.status_code < 500:
                    raise
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
            except httpx.TimeoutException:
                last_error = GabopayError("Request timed out")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
            except httpx.HTTPError as e:
                last_error = GabopayError(str(e))
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)

        raise last_error

    def charges_create(self, options: ChargeCreateOptions) -> Charge:
        """Create a new charge."""
        return cast(Charge, self._request("POST", "/v1/charges", asdict(options)))

    def charges_get(self, charge_id: str) -> Charge:
        """Get a charge by ID."""
        return cast(Charge, self._request("GET", f"/v1/charges/{charge_id}"))

    def charges_list(self, limit: int = 20, status: Optional[str] = None) -> dict:
        """List charges."""
        params = f"?limit={limit}" + (f"&status={status}" if status else "")
        return self._request("GET", f"/v1/charges{params}")

    def refunds_create(self, transaction_id: str, options: RefundCreateOptions) -> Refund:
        """Create a refund."""
        return cast(Refund, self._request("POST", f"/v1/refunds/{transaction_id}", asdict(options)))

    def refunds_get(self, refund_id: str) -> Refund:
        """Get a refund by ID."""
        return cast(Refund, self._request("GET", f"/v1/refunds/{refund_id}"))

    def payouts_create(self, options: PayoutCreateOptions) -> Payout:
        """Create a payout."""
        return cast(Payout, self._request("POST", "/v1/payouts", asdict(options)))

    def payouts_list(self, limit: int = 20) -> dict:
        """List payouts."""
        return self._request("GET", f"/v1/payouts?limit={limit}")

    def balance_retrieve(self) -> Balance:
        """Retrieve merchant balance."""
        return cast(Balance, self._request("GET", "/v1/balance"))

    @staticmethod
    def construct_webhook_event(
        payload: str | dict,
        signature: str,
        secret: str,
    ) -> WebhookEvent:
        """Construct and verify webhook event."""
        if not signature:
            raise WebhookVerificationError("Signature is required")
        if not secret:
            raise WebhookVerificationError("Secret is required")

        payload_str = payload if isinstance(payload, str) else json.dumps(payload)

        if not Webhooks.verify_signature(payload_str, signature, secret):
            raise WebhookVerificationError("Invalid signature")

        if isinstance(payload, str):
            return json.loads(payload)
        return payload


class Webhooks:
    """Webhook utilities"""

    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature."""
        try:
            parts = dict(p.split("=") for p in signature.split(","))
            timestamp = int(parts.get("t", "0"))
            expected_sig = parts.get("v1", "")

            if not timestamp or not expected_sig:
                return False

            current_time = int(time.time())
            if abs(current_time - timestamp) > 300:
                return False

            signed_payload = f"{timestamp}.{payload}"
            computed = hmac.new(
                secret.encode(),
                signed_payload.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(computed, expected_sig)
        except (ValueError, KeyError):
            return False
