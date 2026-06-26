"""Fallback handler — catches messages that no other handler claimed."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from telegram_bot.keyboards.main_menu import get_main_menu_keyboard
from telegram_bot.utils.messages import WELCOME_TEXT

router = Router(name="fallback")


@router.message(~CommandStart(), F.text)
async def on_unrecognized_text(message: Message) -> None:
    """Any plain text that doesn't match a command shows the main menu."""
    await message.answer(WELCOME_TEXT, reply_markup=get_main_menu_keyboard())
