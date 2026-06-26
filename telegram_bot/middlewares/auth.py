"""Admin-only access gate — blocks every non-admin user."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update

from factory.core.config import settings
from factory.core.logging import get_logger
from telegram_bot.utils.messages import ACCESS_DENIED_TEXT

log = get_logger("telegram.auth")


class AdminOnlyMiddleware(BaseMiddleware):
    """Outer middleware registered on dp.update — intercepts every incoming update.

    Passes through when ADMIN_ID is not configured (warns loudly so the operator
    notices the misconfiguration). Any other user gets a polite rejection.
    """

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        admin_id = settings.admin_id

        if admin_id is None:
            log.warning(
                "telegram.auth.no_admin_id",
                msg="ADMIN_ID is not set — all users are allowed (fix this in production)",
            )
            return await handler(event, data)

        # Extract the Telegram user from whatever event type arrived
        telegram_user = (
            (event.message and event.message.from_user)
            or (event.callback_query and event.callback_query.from_user)
            or (event.inline_query and event.inline_query.from_user)
        )

        if telegram_user is None:
            # System updates (channel posts etc.) — skip silently
            return await handler(event, data)

        if telegram_user.id != admin_id:
            log.warning(
                "telegram.auth.denied",
                user_id=telegram_user.id,
                username=telegram_user.username,
            )
            if event.message:
                await event.message.answer(ACCESS_DENIED_TEXT)
            elif event.callback_query:
                await event.callback_query.answer(
                    "⛔ Access denied.", show_alert=True
                )
            return  # do NOT call handler

        return await handler(event, data)
