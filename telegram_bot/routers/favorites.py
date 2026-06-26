"""Favourites router — ⭐ view and manage saved items."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.db.repository import favourite_repo
from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard

router = Router(name="favourites")


def _fav_list_keyboard(items, item_type: str):
    builder = InlineKeyboardBuilder()
    for fav in items:
        # Navigate back to the character when clicked
        if item_type == "character" and fav.category_id:
            cb = f"char:{fav.category_id}:{fav.item_id.split(':')[-1]}"
        else:
            cb = "menu:main"
        builder.button(text=f"⭐ {fav.item_name}", callback_data=cb)
    builder.adjust(1)
    # Tab row
    builder.row(
        InlineKeyboardButton(text="👤 Characters", callback_data="favlist:character"),
        InlineKeyboardButton(text="📂 Categories", callback_data="favlist:category"),
    )
    add_nav_row(builder, current=f"favlist:{item_type}")
    return builder.as_markup()


@router.callback_query(F.data == "menu:favourites")
async def on_favourites(callback: CallbackQuery) -> None:
    await _show_fav_list(callback, "character")


@router.callback_query(F.data.startswith("favlist:"))
async def on_fav_tab(callback: CallbackQuery) -> None:
    item_type = callback.data.split(":")[1]
    await _show_fav_list(callback, item_type)


async def _show_fav_list(callback: CallbackQuery, item_type: str) -> None:
    if item_type == "character":
        items = await favourite_repo.list_characters()
        title = "⭐ Favourite Characters"
    else:
        items = await favourite_repo.list_categories()
        title = "⭐ Favourite Categories"

    if not items:
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"{title}\n\n<i>No favourites saved yet.\n"
            "Open a character and tap ⭐ to save it.</i>",
            reply_markup=get_nav_keyboard(current=f"favlist:{item_type}"),
        )
    else:
        text = f"{title}\n\n{len(items)} saved:"
        await callback.message.edit_text(  # type: ignore[union-attr]
            text,
            reply_markup=_fav_list_keyboard(items, item_type),
        )
    await callback.answer()
