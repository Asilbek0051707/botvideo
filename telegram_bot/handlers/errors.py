"""Global error handler — catches unhandled exceptions in any handler."""

from __future__ import annotations

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ErrorEvent

from factory.core.logging import get_logger

log = get_logger("telegram.errors")

router = Router(name="errors")


@router.errors()
async def handle_error(event: ErrorEvent) -> None:
    exc = event.exception
    # Suppress "message is not modified" — expected when Refresh hits same content
    if isinstance(exc, TelegramBadRequest) and "message is not modified" in str(exc).lower():
        return
    log.error(
        "telegram.unhandled_error",
        exc_info=exc,
        update=event.update.update_id if event.update else None,
    )
