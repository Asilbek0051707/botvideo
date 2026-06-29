"""Bot lifecycle hooks — on_startup and on_shutdown."""

from __future__ import annotations

from aiogram import Bot

from factory.core.config import settings
from factory.core.logging import get_logger

log = get_logger("telegram.lifecycle")


async def on_startup(bot: Bot) -> None:
    # Init bot-local SQLite database (creates tables if they don't exist)
    try:
        from telegram_bot.db.session import init_db
        init_db()
        log.info("telegram.db_ready")
    except Exception as exc:
        log.warning("telegram.db_init_failed", error=str(exc))

    # Seed default trending keywords (idempotent — skips if already seeded)
    try:
        from telegram_bot.services.keyword_service import seed_defaults
        await seed_defaults()
        log.info("telegram.keywords_seeded")
    except Exception as exc:
        log.warning("telegram.keywords_seed_failed", error=str(exc))

    # Pre-build character search index (274 chars → flat blob, ~2ms once)
    try:
        import asyncio as _asyncio
        from telegram_bot.services.character_service import char_service
        await _asyncio.to_thread(char_service._ensure_index)
        log.info("telegram.search_index_ready")
    except Exception as exc:
        log.warning("telegram.search_index_failed", error=str(exc))

    # Seed built-in automation workflow templates (idempotent)
    try:
        from telegram_bot.services.automation_service import seed_workflows
        await seed_workflows()
        log.info("telegram.workflows_seeded")
    except Exception as exc:
        log.warning("telegram.workflows_seed_failed", error=str(exc))

    me = await bot.get_me()
    log.info(
        "telegram.started",
        bot_username=me.username,
        bot_id=me.id,
        admin_id=settings.admin_id,
    )


async def on_shutdown(bot: Bot) -> None:
    log.info("telegram.stopped")
    await bot.session.close()
