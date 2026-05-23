"""Inbound webhooks (payment providers, external render callbacks).

Signature is verified with the shared HMAC secret when a signature header is
present. Events are recorded for audit; provider-specific handling can branch
on the `provider` path segment.
"""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.api.deps import DbDep
from factory.core.logging import get_logger
from factory.core.security import verify_signature
from factory.db.models import Event

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
log = get_logger(__name__)


@router.post("/{provider}")
async def inbound(
    provider: str,
    request: Request,
    db: Session = DbDep,
    x_factory_signature: str | None = Header(default=None, alias="X-Factory-Signature"),
) -> dict:
    body = await request.body()
    if x_factory_signature and not verify_signature(body, x_factory_signature):
        raise HTTPException(status_code=401, detail="bad signature")

    try:
        payload = await request.json()
    except Exception:
        payload = {"raw": body.decode("utf-8", "replace")[:2000]}

    db.add(Event(job_id=None, type=f"webhook.{provider}", data=payload))
    db.commit()
    log.info("webhook.received", provider=provider)
    return {"received": True, "provider": provider}
