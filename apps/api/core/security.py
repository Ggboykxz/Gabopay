"""Security utilities for API key hashing, HMAC signatures, and rate limiting."""

import hashlib
import hmac
import secrets
import time
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from apps.api.core.config import get_settings


@dataclass
class RateLimitResult:
    """Result of rate limit check."""
    allowed: bool
    remaining: int
    reset_at: int


def generate_api_key(prefix: str = "gp_test") -> Tuple[str, str]:
    """
    Generate a new API key with prefix.

    Returns:
        Tuple of (full_key, key_hash)
    """
    random_part = secrets.token_hex(24)
    full_key = f"{prefix}_{random_part}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, key_hash


def verify_api_key(key: str, key_hash: str) -> bool:
    """Verify an API key against its hash."""
    return hashlib.sha256(key.encode()).hexdigest() == key_hash


def parse_api_key(key: str) -> Optional[Tuple[str, str]]:
    """
    Parse an API key to extract prefix and mode.

    Expected format: gp_test_<random> or gp_live_<random>

    Returns:
        Tuple of (prefix, mode) or None if invalid
    """
    if not key or "_" not in key:
        return None

    parts = key.split("_")
    if len(parts) < 3:
        return None

    prefix = f"{parts[0]}_{parts[1]}"
    mode = parts[1]

    if prefix not in ["gp_test", "gp_live"]:
        return None

    if mode not in ["test", "live"]:
        return None

    return prefix, mode


def generate_hmac_signature(payload: str, secret: str, timestamp: Optional[int] = None) -> str:
    """
    Generate HMAC-SHA256 signature for webhook payload.

    Args:
        payload: The JSON payload string
        secret: The webhook secret
        timestamp: Optional timestamp (defaults to current time)

    Returns:
        HMAC signature string
    """
    if timestamp is None:
        timestamp = int(time.time())

    message = f"{timestamp}.{payload}"
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return f"t={timestamp},v1={signature}"


def verify_hmac_signature(
    payload: str,
    signature: str,
    secret: str,
    tolerance_seconds: int = 300
) -> bool:
    """
    Verify HMAC signature from webhook.

    Args:
        payload: The raw payload body
        signature: The signature from headers
        secret: The webhook secret
        tolerance_seconds: Time window for replay attack protection

    Returns:
        True if signature is valid
    """
    try:
        parts = dict(part.split("=") for part in signature.split(","))
        timestamp = int(parts.get("t", 0))
        expected_signature = parts.get("v1", "")

        # Check timestamp is within tolerance
        current_time = int(time.time())
        if abs(current_time - timestamp) > tolerance_seconds:
            return False

        message = f"{timestamp}.{payload}"
        computed_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_signature, expected_signature)
    except (ValueError, KeyError):
        return False


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data like phone numbers or emails.

    Args:
        data: The data to mask
        visible_chars: Number of characters to keep visible at the end

    Returns:
        Masked string
    """
    if len(data) <= visible_chars:
        return "*" * len(data)

    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


def encrypt_credentials(data: str, key: Optional[str] = None) -> str:
    """Encrypt sensitive credentials using Fernet."""
    from cryptography.fernet import Fernet

    settings = get_settings()
    if key is None:
        key = settings.ENCRYPTION_KEY

    if not key:
        logger.warning("ENCRYPTION_KEY is not set! Credentials will be stored in plaintext.")
        return data

    f = Fernet(key.encode() if isinstance(key, str) else key)
    return f.encrypt(data.encode()).decode()


def decrypt_credentials(encrypted_data: str, key: Optional[str] = None) -> str:
    """Decrypt credentials encrypted with Fernet."""
    from cryptography.fernet import Fernet

    settings = get_settings()
    if key is None:
        key = settings.ENCRYPTION_KEY

    if not key:
        return encrypted_data

    f = Fernet(key.encode() if isinstance(key, str) else key)
    return f.decrypt(encrypted_data.encode()).decode()