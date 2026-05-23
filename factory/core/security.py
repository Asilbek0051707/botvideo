"""API-key auth and webhook signing helpers."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from factory.core.config import settings


def verify_api_key(key: str | None) -> bool:
    if not key:
        return False
    allowed = settings.api_key_set
    # constant-time compare against each allowed key
    return any(hmac.compare_digest(key, candidate) for candidate in allowed)


def sign_payload(payload: bytes) -> str:
    """HMAC-SHA256 signature for outgoing webhooks."""
    mac = hmac.new(settings.webhook_signing_secret.encode(), payload, hashlib.sha256)
    return mac.hexdigest()


def verify_signature(payload: bytes, signature: str | None) -> bool:
    if not signature:
        return False
    return hmac.compare_digest(sign_payload(payload), signature)


def new_token(prefix: str = "key") -> str:
    return f"{prefix}_{secrets.token_urlsafe(32)}"
