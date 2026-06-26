"""Settings router — ⚙️ Settings menu item."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from telegram_bot.keyboards.main_menu import get_back_keyboard
from telegram_bot.utils.messages import COMING_SOON_TEXT

router = Router(name="settings")


@router.callback_query(F.data == "menu:settings")
async def on_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"⚙️ <b>Settings</b>\n\n{COMING_SOON_TEXT}",
        reply_markup=get_back_keyboard(),
    )
    await callback.answer()
