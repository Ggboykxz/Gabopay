"""Webhook endpoints for merchant configuration."""

import uuid
import re
import hashlib
import ipaddress
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from apps.api.core.database import get_db
from apps.api.models.merchant import Merchant, WebhookEndpoint, WebhookDelivery
from apps.api.api.v1.charges import get_api_key_merchant
from apps.api.core.security import encrypt_credentials

router = APIRouter()

PRIVATE_IPS = {"10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "169.254.0.0/16"}


def _is_private_url(url: str) -> bool:
    try:
        host = urlparse(url).hostname
        if not host:
            return True
        ip = ipaddress.ip_address(host)
        for cidr in PRIVATE_IPS:
            if ip in ipaddress.ip_network(cidr):
                return True
    except ValueError:
        pass
    return False


class WebhookCreateRequest(BaseModel):
    """Request to create a webhook endpoint."""
    url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="Events to subscribe to")


class WebhookCreateResponse(BaseModel):
    """Webhook endpoint response with secret."""
    id: str
    object: str = "webhook_endpoint"
    url: str
    events: List[str]
    active: bool
    secret: str
    created: int


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


async def get_current_merchant_from_auth(
    merchant: Merchant = Depends(get_api_key_merchant),
) -> Merchant:
    """Get merchant from API key auth."""
    return merchant[0]


@router.post("", response_model=WebhookCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    request: WebhookCreateRequest,
    merchant: Merchant = Depends(get_current_merchant_from_auth),
):
    """Create a new webhook endpoint."""
    from apps.api.core.config import get_settings
    settings = get_settings()

    if not re.match(r"^https://", request.url):
        if settings.is_production or not re.match(r"^https?://", request.url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL must use https://",
            )

    if _is_private_url(request.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must not point to a private or internal network",
        )

    secret = uuid.uuid4().hex + uuid.uuid4().hex
    secret_hash = hashlib.sha256(secret.encode()).hexdigest()
    encrypted_secret = encrypt_credentials(secret)

    async with get_db() as db:
        webhook = WebhookEndpoint(
            merchant_id=merchant.id,
            url=request.url,
            events=request.events,
            secret_hash=secret_hash,
            secret_encrypted=encrypted_secret,
            active=True,
        )
        db.add(webhook)
        await db.commit()

        return WebhookCreateResponse(
            id=str(webhook.id),
            object="webhook_endpoint",
            url=webhook.url,
            events=webhook.events,
            active=webhook.active,
            secret=secret,
            created=int(webhook.created_at.timestamp()),
        )


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