"""Synchronous SQLAlchemy session/engine.

We use sync sessions everywhere: FastAPI DB-touching handlers are declared `def`
(so they run in the threadpool) and Celery tasks are sync by nature. Heavy work is
pushed to the queue, so the request path stays light without async DB plumbing.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from factory.core.config import settings

engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


def get_session() -> Iterator[Session]:
    """FastAPI dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Transactional scope for workers/scripts."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Dev convenience: create tables from models. Prod uses Alembic migrations."""
    from factory.db import models  # noqa: F401  (register mappers)

    Base = models.Base
    Base.metadata.create_all(bind=engine)
