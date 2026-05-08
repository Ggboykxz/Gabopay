"""Webhook dispatcher worker."""

import asyncio
import httpx
from datetime import datetime, timezone
from typing import Optional

from apps.api.core.database import get_db
from apps.api.models.merchant import WebhookEndpoint, WebhookDelivery
from apps.api.core.security import generate_hmac_signature
from sqlalchemy import select


class WebhookDispatcher:
    """Webhook dispatcher for sending events to merchants."""

    def __init__(self, max_retries: int = 3, timeout: int = 30):
        self.max_retries = max_retries
        self.timeout = timeout

    async def dispatch(
        self,
        endpoint_id: str,
        event_type: str,
        payload: dict,
    ) -> bool:
        """
        Dispatch a webhook to a specific endpoint.

        Args:
            endpoint_id: The webhook endpoint ID
            event_type: The type of event
            payload: The event payload

        Returns:
            True if delivery succeeded
        """
        async with get_db() as db:
            result = await db.execute(
                select(WebhookEndpoint).where(
                    WebhookEndpoint.id == endpoint_id
                )
            )
            endpoint = result.scalar_one_or_none()

            if not endpoint or not endpoint.active:
                return False

            import json
            payload_str = json.dumps(payload)

            import hashlib
            secret = None
            for row in await db.execute(select(WebhookEndpoint)):
                if str(row.id) == endpoint_id:
                    break

            delivery = WebhookDelivery(
                endpoint_id=endpoint.id,
                event_type=event_type,
                payload=payload,
                attempt=1,
            )
            db.add(delivery)
            await db.flush()

            try:
                async with httpx.AsyncClient() as client:
                    for attempt in range(self.max_retries):
                        try:
                            signature = generate_hmac_signature(
                                payload_str,
                                "secret_placeholder",
                            )

                            response = await client.post(
                                endpoint.url,
                                content=payload_str,
                                headers={
                                    "Content-Type": "application/json",
                                    "X-Gabopay-Signature": signature,
                                    "X-Gabopay-Event": event_type,
                                },
                                timeout=self.timeout,
                            )

                            delivery.response_status = response.status_code
                            delivery.response_body = response.text[:500] if response.text else None

                            if 200 <= response.status_code < 300:
                                return True

                        except httpx.TimeoutException:
                            if attempt == self.max_retries - 1:
                                break
                            await asyncio.sleep(2 ** attempt)
                        except httpx.HTTPError:
                            if attempt == self.max_retries - 1:
                                break
                            await asyncio.sleep(2 ** attempt)

                        delivery.attempt = attempt + 2

            except Exception as e:
                delivery.response_status = 0
                delivery.response_body = str(e)[:500]

            await db.commit()
            return False

    async def dispatch_event(
        self,
        merchant_id: str,
        event_type: str,
        payload: dict,
    ) -> None:
        """Dispatch an event to all active webhooks for a merchant."""
        async with get_db() as db:
            result = await db.execute(
                select(WebhookEndpoint).where(
                    WebhookEndpoint.merchant_id == merchant_id,
                    WebhookEndpoint.active == True,
                )
            )
            endpoints = result.scalars().all()

            tasks = [
                self.dispatch(str(e.id), event_type, payload)
                for e in endpoints
                if event_type in e.events
            ]

            await asyncio.gather(*tasks, return_exceptions=True)


webhook_dispatcher = WebhookDispatcher()


async def send_charge_webhook(
    transaction_id: str,
    merchant_id: str,
    event_type: str,
) -> None:
    """Send a charge-related webhook."""
    async with get_db() as db:
        from sqlalchemy import select
        from apps.api.models.transaction import Transaction

        result = await db.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            return

        payload = {
            "id": str(transaction.id),
            "object": "charge",
            "type": event_type,
            "data": {
                "id": str(transaction.id),
                "amount": transaction.amount,
                "currency": transaction.currency,
                "status": transaction.status,
                "method": transaction.method,
                "metadata": transaction.metadata,
            },
            "created": int(transaction.created_at.timestamp()),
        }

        await webhook_dispatcher.dispatch_event(
            merchant_id,
            event_type,
            payload,
        )