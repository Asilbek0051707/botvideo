"""Minimal auth surface — validate an API key. (JWT/OAuth can layer on later.)"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.deps import ApiKeyDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/verify", dependencies=[ApiKeyDep])
def verify() -> dict:
    return {"valid": True}
