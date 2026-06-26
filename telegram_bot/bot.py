"""Telegram bot entry point — Aiogram 3, long-polling.

Run:  python -m telegram_bot.bot

Idles gracefully when TELEGRAM_BOT_TOKEN is unset so the container stays up
in multi-service stacks where the bot is not yet configured.
"""

from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from factory.core.config import settings
from factory.core.logging import configure_logging, get_logger
from telegram_bot.core.startup import on_shutdown, on_startup
from telegram_bot.handlers import register_handlers
from telegram_bot.middlewares.auth import AdminOnlyMiddleware
from telegram_bot.middlewares.logging import RequestLoggingMiddleware
from telegram_bot.routers import register_routers

log = get_logger("telegram.bot")


def _build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # --- Middlewares (outer → inner) ---
    # Auth gate: blocks non-admin users before any handler runs
    dp.update.outer_middleware(AdminOnlyMiddleware())
    # Logging: records every update for debugging
    dp.update.middleware(RequestLoggingMiddleware())

    # --- Routers (feature modules) ---
    register_routers(dp)

    # --- Handlers (admin commands, error handler, fallback) ---
    register_handlers(dp)

    return dp


async def main() -> None:
    configure_logging()

    if not settings.telegram_bot_token:
        log.warning("telegram.no_token", msg="TELEGRAM_BOT_TOKEN is not set — idling")
        while True:
            await asyncio.sleep(3600)

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = _build_dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    log.info("telegram.starting", admin_id=settings.admin_id)

    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
