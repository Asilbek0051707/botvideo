"""Search router — FSM-based instant search across characters."""

from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.main_menu import get_main_menu_keyboard
from telegram_bot.keyboards.navigation import get_nav_keyboard
from telegram_bot.services.character_service import char_service

router = Router(name="search")


class SearchStates(StatesGroup):
    waiting_for_query = State()


# ── entry points ──────────────────────────────────────────────────


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer(
        "🔍 <b>Search</b>\n\nType a character name, category, or keyword:"
    )


@router.callback_query(F.data == "menu:search")
async def on_search_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_for_query)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔍 <b>Search</b>\n\nType a character name, category, or keyword:"
    )
    await callback.answer()


# ── query handler ─────────────────────────────────────────────────


@router.message(SearchStates.waiting_for_query)
async def on_search_query(message: Message, state: FSMContext) -> None:
    query = (message.text or "").strip()
    await state.clear()

    if not query:
        await message.answer("❌ Empty query. Use /search to try again.")
        return

    results = await asyncio.to_thread(char_service.search, query, 15)

    if not results:
        await message.answer(
            f"🔍 No results for <b>{query}</b>.\n\n"
            "Try a different keyword.",
            reply_markup=get_nav_keyboard(current="menu:search"),
        )
        return

    builder = InlineKeyboardBuilder()
    for cat, char in results:
        label = f"{cat.icon} {char.name} ({cat.name})"
        builder.button(text=label, callback_data=f"char:{cat.id}:{char.id}")
    builder.adjust(1)
    builder.row()  # spacing
    from aiogram.types import InlineKeyboardButton
    builder.row(
        InlineKeyboardButton(text="🔍 New Search", callback_data="menu:search"),
        InlineKeyboardButton(text="🏠 Home",       callback_data="menu:main"),
    )

    await message.answer(
        f"🔍 Results for <b>{query}</b>: {len(results)} found",
        reply_markup=builder.as_markup(),
    )
