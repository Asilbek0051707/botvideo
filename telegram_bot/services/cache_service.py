"""DB-backed cache service for external API responses.

All public functions are async (sync DB ops run via asyncio.to_thread).
Cache keys: any string up to 500 chars.
Data is stored as JSON text.
Expired entries are cleaned lazily on read + explicitly via cleanup().
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone


# ── sync helpers ────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_sync(key: str) -> dict | None:
    from telegram_bot.db.integration_models import CacheEntry
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        row = db.query(CacheEntry).filter_by(cache_key=key).first()
        if row is None:
            return None
        if row.expires_at.replace(tzinfo=timezone.utc) < _now():
            db.delete(row)
            db.commit()
            return None
        try:
            return json.loads(row.data)
        except Exception:
            return None


def _set_sync(key: str, data: dict, provider_slug: str, ttl_seconds: int) -> None:
    from telegram_bot.db.integration_models import CacheEntry
    from telegram_bot.db.session import SessionLocal

    expires = _now() + timedelta(seconds=ttl_seconds)
    payload = json.dumps(data, ensure_ascii=False, default=str)

    with SessionLocal() as db:
        row = db.query(CacheEntry).filter_by(cache_key=key).first()
        if row:
            row.data          = payload
            row.provider_slug = provider_slug
            row.expires_at    = expires
            row.created_at    = _now()
        else:
            db.add(CacheEntry(
                cache_key=key,
                provider_slug=provider_slug,
                data=payload,
                expires_at=expires,
            ))
        db.commit()


def _invalidate_sync(key: str) -> bool:
    from telegram_bot.db.integration_models import CacheEntry
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        row = db.query(CacheEntry).filter_by(cache_key=key).first()
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True


def _clear_provider_sync(provider_slug: str) -> int:
    from telegram_bot.db.integration_models import CacheEntry
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        rows = db.query(CacheEntry).filter_by(provider_slug=provider_slug).all()
        count = len(rows)
        for r in rows:
            db.delete(r)
        db.commit()
        return count


def _clear_all_sync() -> int:
    from telegram_bot.db.integration_models import CacheEntry
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        rows = db.query(CacheEntry).all()
        count = len(rows)
        for r in rows:
            db.delete(r)
        db.commit()
        return count


def _cleanup_expired_sync() -> int:
    from telegram_bot.db.integration_models import CacheEntry
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        rows = db.query(CacheEntry).filter(CacheEntry.expires_at < _now()).all()
        count = len(rows)
        for r in rows:
            db.delete(r)
        db.commit()
        return count


def _count_sync() -> dict:
    from telegram_bot.db.integration_models import CacheEntry
    from telegram_bot.db.session import SessionLocal
    from sqlalchemy import func

    with SessionLocal() as db:
        total   = db.query(func.count(CacheEntry.id)).scalar() or 0
        expired = (
            db.query(func.count(CacheEntry.id))
            .filter(CacheEntry.expires_at < _now())
            .scalar() or 0
        )
        return {"total": total, "expired": expired, "live": total - expired}


# ── async API ───────────────────────────────────────────────────────────

async def get_cache(key: str) -> dict | None:
    """Return cached data or None if missing/expired."""
    return await asyncio.to_thread(_get_sync, key)


async def set_cache(
    key: str,
    data: dict,
    provider_slug: str = "general",
    ttl_seconds: int = 3600,
) -> None:
    """Write or update a cache entry."""
    await asyncio.to_thread(_set_sync, key, data, provider_slug, ttl_seconds)


async def invalidate_cache(key: str) -> bool:
    """Delete a specific cache entry. Returns True if it existed."""
    return await asyncio.to_thread(_invalidate_sync, key)


async def clear_provider_cache(provider_slug: str) -> int:
    """Delete all cache entries for a provider. Returns count deleted."""
    return await asyncio.to_thread(_clear_provider_sync, provider_slug)


async def clear_all_cache() -> int:
    """Wipe the entire cache. Returns count deleted."""
    return await asyncio.to_thread(_clear_all_sync)


async def cleanup_expired() -> int:
    """Remove expired entries. Safe to call periodically. Returns count removed."""
    return await asyncio.to_thread(_cleanup_expired_sync)


async def cache_stats() -> dict:
    """Return {"total", "expired", "live"} counts."""
    return await asyncio.to_thread(_count_sync)


# ── convenience: get-or-fetch ───────────────────────────────────────────

async def get_or_fetch(
    key: str,
    fetch_fn,
    provider_slug: str = "general",
    ttl_seconds: int = 3600,
) -> dict:
    """Return cached value, or call fetch_fn() and cache the result.

    fetch_fn must be async and return a dict.
    """
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await fetch_fn()
    if data:
        await set_cache(key, data, provider_slug, ttl_seconds)
    return data or {}
