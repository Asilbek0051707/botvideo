"""Lightweight per-request logging middleware."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update

from factory.core.logging import get_logger

log = get_logger("telegram.request")


def _update_type(event: Update) -> str:
    if event.message:
        return "message"
    if event.callback_query:
        return "callback_query"
    if event.inline_query:
        return "inline_query"
    if event.edited_message:
        return "edited_message"
    return "other"


class RequestLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        telegram_user = (
            (event.message and event.message.from_user)
            or (event.callback_query and event.callback_query.from_user)
        )
        log.debug(
            "telegram.update",
            update_id=event.update_id,
            type=_update_type(event),
            user_id=telegram_user.id if telegram_user else None,
        )
        return await handler(event, data)
