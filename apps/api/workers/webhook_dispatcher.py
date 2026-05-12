"""Webhook dispatcher worker."""

import json
import asyncio
import logging
import httpx
from typing import Optional
from sqlalchemy import select

from apps.api.core.database import get_db
from apps.api.models.merchant import WebhookEndpoint, WebhookDelivery
from apps.api.core.security import generate_hmac_signature, decrypt_credentials

logger = logging.getLogger(__name__)


class WebhookDispatcher:
    """Webhook dispatcher for sending events to merchants."""

    def __init__(self, max_retries: int = 3, timeout: int = 30):
        self.max_retries = max_retries
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

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

            secret = None
            if endpoint.secret_encrypted:
                secret = decrypt_credentials(endpoint.secret_encrypted)

            payload_str = json.dumps(payload)

            delivery = WebhookDelivery(
                endpoint_id=endpoint.id,
                event_type=event_type,
                payload=payload,
                attempt=1,
            )
            db.add(delivery)
            await db.flush()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for attempt in range(self.max_retries):
                    try:
                        signature = generate_hmac_signature(
                            payload_str,
                            secret or "",
                        )

                        response = await client.post(
                            endpoint.url,
                            content=payload_str,
                            headers={
                                "Content-Type": "application/json",
                                "X-Gabopay-Signature": signature,
                                "X-Gabopay-Event": event_type,
                            },
                        )

                        async with get_db() as db:
                            result = await db.execute(
                                select(WebhookDelivery).where(
                                    WebhookDelivery.id == delivery.id
                                )
                            )
                            d = result.scalar_one_or_none()
                            if d:
                                d.response_status = response.status_code
                                d.response_body = response.text[:500] if response.text else None
                            await db.commit()

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

                    async with get_db() as db:
                        result = await db.execute(
                            select(WebhookDelivery).where(
                                WebhookDelivery.id == delivery.id
                            )
                        )
                        d = result.scalar_one_or_none()
                        if d:
                            d.attempt = attempt + 2
                        await db.commit()

        except Exception as e:
            logger.error(f"Webhook dispatch error: {e}")
            async with get_db() as db:
                result = await db.execute(
                    select(WebhookDelivery).where(
                        WebhookDelivery.id == delivery.id
                    )
                )
                d = result.scalar_one_or_none()
                if d:
                    d.response_status = 0
                    d.response_body = str(e)[:500]
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
    from sqlalchemy import select
    from apps.api.models.transaction import Transaction

    async with get_db() as db:
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
                "metadata": transaction.metadata_,
            },
            "created": int(transaction.created_at.timestamp()),
        }

        await webhook_dispatcher.dispatch_event(
            merchant_id,
            event_type,
            payload,
        )
