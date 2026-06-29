"""Integration Manager — singleton that manages all external providers.

Usage:
    from telegram_bot.services.integration_manager import manager

    provider = manager.get("youtube")
    ok, msg  = await provider.health_check()
    statuses = await manager.health_check_all()
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from telegram_bot.services.integrations import (
    AnthropicProvider,
    BaseIntegrationProvider,
    GeminiProvider,
    GoogleTrendsProvider,
    OpenAIProvider,
    OpenRouterProvider,
    YouTubeProvider,
)

# Registry: slug → provider instance
_REGISTRY: dict[str, BaseIntegrationProvider] = {}


def _build_registry() -> dict[str, BaseIntegrationProvider]:
    providers: list[type[BaseIntegrationProvider]] = [
        YouTubeProvider,
        GoogleTrendsProvider,
        OpenAIProvider,
        AnthropicProvider,
        OpenRouterProvider,
        GeminiProvider,
    ]
    reg: dict[str, BaseIntegrationProvider] = {}
    for cls in providers:
        p = cls()
        reg[p.config.slug] = p
    return reg


class IntegrationManager:
    """Lightweight facade over the provider registry."""

    def __init__(self, registry: dict[str, BaseIntegrationProvider]) -> None:
        self._reg = registry

    # ── provider access ─────────────────────────────────────────────

    def get(self, slug: str) -> BaseIntegrationProvider | None:
        return self._reg.get(slug)

    def list_all(self) -> list[BaseIntegrationProvider]:
        return list(self._reg.values())

    def list_by_category(self, category: str) -> list[BaseIntegrationProvider]:
        return [p for p in self._reg.values() if p.config.category == category]

    # ── health ───────────────────────────────────────────────────────

    async def health_check_all(self) -> dict[str, tuple[bool, str]]:
        """Run health checks in parallel. Never raises."""
        results: dict[str, tuple[bool, str]] = {}

        async def _check(slug: str, prov: BaseIntegrationProvider) -> None:
            try:
                results[slug] = await prov.health_check()
            except Exception as exc:
                results[slug] = (False, str(exc))

        await asyncio.gather(*[_check(s, p) for s, p in self._reg.items()])
        await _persist_health(results)
        return results

    async def health_check_one(self, slug: str) -> tuple[bool, str]:
        prov = self.get(slug)
        if prov is None:
            return False, f"Provider '{slug}' not found"
        try:
            result = await prov.health_check()
        except Exception as exc:
            result = (False, str(exc))
        await _persist_health({slug: result})
        return result

    # ── provider status DB ───────────────────────────────────────────

    async def sync_provider_registry(self) -> None:
        """Ensure all registered providers have a row in int_providers."""
        await asyncio.to_thread(_sync_registry_sync, list(self._reg.values()))

    # ── background tasks ─────────────────────────────────────────────

    async def run_background_sync(self) -> None:
        """Lightweight sync: health check + cache cleanup.
        Meant to be called via asyncio.create_task at bot startup.
        """
        import asyncio as _asyncio
        from telegram_bot.services.cache_service import cleanup_expired

        while True:
            try:
                await self.health_check_all()
                await cleanup_expired()
            except Exception:
                pass
            await _asyncio.sleep(1800)   # repeat every 30 min


# ── DB sync helpers ──────────────────────────────────────────────────────

def _sync_registry_sync(providers: list[BaseIntegrationProvider]) -> None:
    from telegram_bot.db.integration_models import ProviderStatus
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        for p in providers:
            row = db.query(ProviderStatus).filter_by(slug=p.config.slug).first()
            if not row:
                row = ProviderStatus(
                    slug=p.config.slug,
                    name=p.config.name,
                    api_key_env=p.config.api_key_env,
                    requires_key=p.config.requires_key,
                    base_url=p.config.base_url,
                    timeout=p.config.timeout,
                    retry_count=p.config.retry_count,
                    cache_ttl=p.config.cache_ttl,
                )
                db.add(row)
            else:
                row.name         = p.config.name
                row.api_key_env  = p.config.api_key_env
                row.requires_key = p.config.requires_key
        db.commit()


async def _persist_health(results: dict[str, tuple[bool, str]]) -> None:
    await asyncio.to_thread(_persist_health_sync, results)


def _persist_health_sync(results: dict[str, tuple[bool, str]]) -> None:
    from telegram_bot.db.integration_models import ProviderStatus, ProviderLog
    from telegram_bot.db.session import SessionLocal

    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for slug, (ok, msg) in results.items():
            row = db.query(ProviderStatus).filter_by(slug=slug).first()
            if row:
                row.last_checked = now
                row.last_status  = "ok" if ok else "error"
                row.last_message = msg[:499]
                if not ok:
                    row.error_count = (row.error_count or 0) + 1
            # write log
            db.add(ProviderLog(
                provider_slug=slug,
                level="info" if ok else "error",
                message=msg[:499],
                context=json.dumps({"ok": ok}),
                created_at=now,
            ))
        db.commit()


# ── module-level singleton ────────────────────────────────────────────────

_REGISTRY = _build_registry()
manager   = IntegrationManager(_REGISTRY)


# ── helpers for DB provider listing ─────────────────────────────────────

def _list_provider_rows_sync() -> list:
    from telegram_bot.db.integration_models import ProviderStatus
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return db.query(ProviderStatus).order_by(ProviderStatus.slug).all()


async def list_provider_rows() -> list:
    return await asyncio.to_thread(_list_provider_rows_sync)


def _list_logs_sync(slug: str | None, limit: int) -> list:
    from telegram_bot.db.integration_models import ProviderLog
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(ProviderLog)
        if slug:
            q = q.filter_by(provider_slug=slug)
        return q.order_by(ProviderLog.created_at.desc()).limit(limit).all()


async def list_logs(slug: str | None = None, limit: int = 20) -> list:
    return await asyncio.to_thread(_list_logs_sync, slug, limit)


def _log_sync_history_sync(
    provider_slug: str,
    sync_type: str,
    status: str,
    records: int = 0,
    error: str = "",
) -> None:
    from telegram_bot.db.integration_models import SyncHistory
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        db.add(SyncHistory(
            provider_slug=provider_slug,
            sync_type=sync_type,
            status=status,
            records_synced=records,
            error_msg=error,
            completed_at=datetime.now(timezone.utc),
        ))
        db.commit()


async def log_sync_history(
    provider_slug: str,
    sync_type: str,
    status: str,
    records: int = 0,
    error: str = "",
) -> None:
    await asyncio.to_thread(
        _log_sync_history_sync, provider_slug, sync_type, status, records, error
    )


def _list_sync_history_sync(slug: str | None, limit: int) -> list:
    from telegram_bot.db.integration_models import SyncHistory
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(SyncHistory)
        if slug:
            q = q.filter_by(provider_slug=slug)
        return q.order_by(SyncHistory.started_at.desc()).limit(limit).all()


async def list_sync_history(slug: str | None = None, limit: int = 10) -> list:
    return await asyncio.to_thread(_list_sync_history_sync, slug, limit)
