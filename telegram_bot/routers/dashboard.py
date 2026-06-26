"""Dashboard router — 🏠 Dashboard menu item."""

from __future__ import annotations

from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import CallbackQuery

from factory.core.config import settings
from telegram_bot.keyboards.main_menu import get_back_keyboard

router = Router(name="dashboard")


@router.callback_query(F.data == "menu:dashboard")
async def on_dashboard(callback: CallbackQuery) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = (
        "🏠 <b>Dashboard</b>\n\n"
        f"<b>Status:</b> ✅ Online\n"
        f"<b>Admin ID:</b> <code>{settings.admin_id}</code>\n"
        f"<b>Time:</b> {now}\n\n"
        "<i>More stats will appear here once modules are active.</i>"
    )
    await callback.message.edit_text(text, reply_markup=get_back_keyboard())  # type: ignore[union-attr]
    await callback.answer()
