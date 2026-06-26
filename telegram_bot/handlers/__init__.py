"""Handler registry — admin commands, error handler, fallback."""

from __future__ import annotations

from aiogram import Dispatcher

from telegram_bot.handlers import admin, errors, user


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(admin.router)
    dp.include_router(errors.router)
    dp.include_router(user.router)  # fallback — must be last
