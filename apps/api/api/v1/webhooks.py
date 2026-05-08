"""Webhook endpoints for merchant configuration."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
import hashlib

from apps.api.core.database import get_db
from apps.api.models.merchant import Merchant, WebhookEndpoint, WebhookDelivery
from apps.api.api.v1.charges import get_api_key_merchant

router = APIRouter()


class WebhookCreateRequest(BaseModel):
    """Request to create a webhook endpoint."""
    url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="Events to subscribe to")


class WebhookResponse(BaseModel):
    """Webhook endpoint response."""
    id: str
    object: str = "webhook_endpoint"
    url: str
    events: List[str]
    active: bool
    created: int


class WebhookUpdateRequest(BaseModel):
    """Request to update a webhook endpoint."""
    url: Optional[str] = None
    events: Optional[List[str]] = None
    active: Optional[bool] = None


class WebhookDeliveryResponse(BaseModel):
    """Webhook delivery response."""
    id: str
    event_type: str
    payload: dict
    response_status: Optional[int]
    attempt: int
    created: int


class WebhookListResponse(BaseModel):
    """List of webhooks response."""
    data: List[WebhookResponse]
    total: int


@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    request: WebhookCreateRequest,
    merchant: Merchant = Depends(get_current_merchant_from_auth),
):
    """Create a new webhook endpoint."""
    import re
    if not re.match(r"^https?://", request.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must start with http:// or https://",
        )

    secret = uuid.uuid4().hex + uuid.uuid4().hex
    secret_hash = hashlib.sha256(secret.encode()).hexdigest()

    async with get_db() as db:
        webhook = WebhookEndpoint(
            merchant_id=merchant.id,
            url=request.url,
            events=request.events,
            secret_hash=secret_hash,
            active=True,
        )
        db.add(webhook)
        await db.commit()

        return WebhookResponse(
            id=str(webhook.id),
            object="webhook_endpoint",
            url=webhook.url,
            events=webhook.events,
            active=webhook.active,
            created=int(webhook.created_at.timestamp()),
        )


async def get_current_merchant_from_auth(
    merchant: Merchant = Depends(get_api_key_merchant),
) -> Merchant:
    """Get merchant from API key auth."""
    return merchant[0]


@router.get("", response_model=WebhookListResponse)
async def list_webhooks(
    merchant: Merchant = Depends(get_current_merchant_from_auth),
):
    """List webhook endpoints for the merchant."""
    async with get_db() as db:
        result = await db.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.merchant_id == merchant.id
            )
        )
        webhooks = result.scalars().all()

        return WebhookListResponse(
            data=[
                WebhookResponse(
                    id=str(w.id),
                    object="webhook_endpoint",
                    url=w.url,
                    events=w.events,
                    active=w.active,
                    created=int(w.created_at.timestamp()),
                )
                for w in webhooks
            ],
            total=len(webhooks),
        )


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: uuid.UUID,
    merchant: Merchant = Depends(get_current_merchant_from_auth),
):
    """Get a webhook endpoint."""
    async with get_db() as db:
        result = await db.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.id == webhook_id,
                WebhookEndpoint.merchant_id == merchant.id,
            )
        )
        webhook = result.scalar_one_or_none()

        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found",
            )

        return WebhookResponse(
            id=str(webhook.id),
            object="webhook_endpoint",
            url=webhook.url,
            events=webhook.events,
            active=webhook.active,
            created=int(webhook.created_at.timestamp()),
        )


@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: uuid.UUID,
    request: WebhookUpdateRequest,
    merchant: Merchant = Depends(get_current_merchant_from_auth),
):
    """Update a webhook endpoint."""
    async with get_db() as db:
        result = await db.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.id == webhook_id,
                WebhookEndpoint.merchant_id == merchant.id,
            )
        )
        webhook = result.scalar_one_or_none()

        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found",
            )

        if request.url is not None:
            webhook.url = request.url
        if request.events is not None:
            webhook.events = request.events
        if request.active is not None:
            webhook.active = request.active

        await db.commit()

        return WebhookResponse(
            id=str(webhook.id),
            object="webhook_endpoint",
            url=webhook.url,
            events=webhook.events,
            active=webhook.active,
            created=int(webhook.created_at.timestamp()),
        )


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: uuid.UUID,
    merchant: Merchant = Depends(get_current_merchant_from_auth),
):
    """Delete a webhook endpoint."""
    async with get_db() as db:
        result = await db.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.id == webhook_id,
                WebhookEndpoint.merchant_id == merchant.id,
            )
        )
        webhook = result.scalar_one_or_none()

        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found",
            )

        await db.delete(webhook)
        await db.commit()


@router.get("/{webhook_id}/deliveries")
async def list_webhook_deliveries(
    webhook_id: uuid.UUID,
    merchant: Merchant = Depends(get_current_merchant_from_auth),
    limit: int = 20,
):
    """List webhook delivery attempts."""
    async with get_db() as db:
        result = await db.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.id == webhook_id,
                WebhookEndpoint.merchant_id == merchant.id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found",
            )

        result = await db.execute(
            select(WebhookDelivery)
            .where(WebhookDelivery.endpoint_id == webhook_id)
            .order_by(WebhookDelivery.created_at.desc())
            .limit(limit)
        )
        deliveries = result.scalars().all()

        return {
            "data": [
                WebhookDeliveryResponse(
                    id=str(d.id),
                    event_type=d.event_type,
                    payload=d.payload,
                    response_status=d.response_status,
                    attempt=d.attempt,
                    created=int(d.created_at.timestamp()),
                )
                for d in deliveries
            ],
            "total": len(deliveries),
        }