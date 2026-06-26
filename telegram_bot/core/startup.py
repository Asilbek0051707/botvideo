"""Bot lifecycle hooks — on_startup and on_shutdown."""

from __future__ import annotations

from aiogram import Bot

from factory.core.config import settings
from factory.core.logging import get_logger

log = get_logger("telegram.lifecycle")


async def on_startup(bot: Bot) -> None:
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
