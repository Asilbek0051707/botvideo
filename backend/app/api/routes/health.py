"""Liveness/readiness probes (no auth)."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from factory.core.config import settings
from factory.db.session import engine
from factory.services.queue import celery_app

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "env": settings.env}


@router.get("/ready")
def ready() -> dict:
    checks = {"db": False, "broker": False}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["db"] = True
    except Exception:
        pass
    try:
        celery_app.connection().ensure_connection(max_retries=1, timeout=2)
        checks["broker"] = True
    except Exception:
        pass
    checks["status"] = "ok" if all(v for k, v in checks.items() if k != "status") else "degraded"
    return checks
