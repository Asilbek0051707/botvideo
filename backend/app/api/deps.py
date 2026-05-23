"""FastAPI dependencies: DB session + API-key auth."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from factory.core.security import verify_api_key
from factory.db.session import get_session


def db_session() -> Iterator[Session]:
    yield from get_session()


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    if not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key (header: X-API-Key)",
        )
    return x_api_key  # type: ignore[return-value]


DbDep = Depends(db_session)
ApiKeyDep = Depends(require_api_key)
