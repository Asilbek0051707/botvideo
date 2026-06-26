"""Entry point router — /start command and main menu navigation."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards.main_menu import get_main_menu_keyboard
from telegram_bot.utils.messages import WELCOME_TEXT

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "menu:main")
async def back_to_main_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        WELCOME_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()
