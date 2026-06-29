"""Integration layer DB models — STEP 9 External Providers.

Stores provider status, sync history, cache, and logs.
No API keys are stored here — only env-var names are referenced.
Column-level index=True used (safe for repeated create_all calls).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from telegram_bot.db.models import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ProviderStatus(Base):
    """One row per registered provider — tracks runtime health."""

    __tablename__ = "int_providers"

    id:               Mapped[int]             = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug:             Mapped[str]             = mapped_column(String(50), unique=True, index=True)
    name:             Mapped[str]             = mapped_column(String(100))
    is_enabled:       Mapped[bool]            = mapped_column(Boolean, default=True, index=True)
    api_key_env:      Mapped[str]             = mapped_column(String(100), default="")
    requires_key:     Mapped[bool]            = mapped_column(Boolean, default=True)
    base_url:         Mapped[str]             = mapped_column(String(200), default="")
    timeout:          Mapped[int]             = mapped_column(Integer, default=30)
    retry_count:      Mapped[int]             = mapped_column(Integer, default=3)
    cache_ttl:        Mapped[int]             = mapped_column(Integer, default=3600)
    last_checked:     Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_status:      Mapped[str]             = mapped_column(String(20), default="unknown", index=True)
    last_message:     Mapped[str]             = mapped_column(String(500), default="")
    error_count:      Mapped[int]             = mapped_column(Integer, default=0)
    total_requests:   Mapped[int]             = mapped_column(Integer, default=0)
    created_at:       Mapped[datetime]        = mapped_column(DateTime, default=_now)
    updated_at:       Mapped[datetime]        = mapped_column(DateTime, default=_now, onupdate=_now)


class SyncHistory(Base):
    """Log entry for each sync operation."""

    __tablename__ = "int_sync_history"

    id:              Mapped[int]             = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider_slug:   Mapped[str]             = mapped_column(String(50), index=True)
    sync_type:       Mapped[str]             = mapped_column(String(50))
    status:          Mapped[str]             = mapped_column(String(20), default="pending")
    records_synced:  Mapped[int]             = mapped_column(Integer, default=0)
    error_msg:       Mapped[str]             = mapped_column(Text, default="")
    started_at:      Mapped[datetime]        = mapped_column(DateTime, default=_now, index=True)
    completed_at:    Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class CacheEntry(Base):
    """DB-backed cache for external API responses."""

    __tablename__ = "int_cache"

    id:            Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    cache_key:     Mapped[str]      = mapped_column(String(500), unique=True, index=True)
    provider_slug: Mapped[str]      = mapped_column(String(50), index=True)
    data:          Mapped[str]      = mapped_column(Text)
    expires_at:    Mapped[datetime] = mapped_column(DateTime, index=True)
    created_at:    Mapped[datetime] = mapped_column(DateTime, default=_now)


class ProviderLog(Base):
    """Structured log for provider events."""

    __tablename__ = "int_logs"

    id:            Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider_slug: Mapped[str]      = mapped_column(String(50), index=True)
    level:         Mapped[str]      = mapped_column(String(10), default="info", index=True)
    message:       Mapped[str]      = mapped_column(String(500))
    context:       Mapped[str]      = mapped_column(Text, default="{}")
    created_at:    Mapped[datetime] = mapped_column(DateTime, default=_now, index=True)
