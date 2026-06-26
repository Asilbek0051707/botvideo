"""Reusable navigation keyboard — Back, Home, Refresh."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_nav_keyboard(current: str, parent: str = "menu:main") -> InlineKeyboardMarkup:
    """Standalone 3-button navigation keyboard (Back / Home / Refresh)."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ Back",     callback_data=parent)
    builder.button(text="🏠 Home",    callback_data="menu:main")
    builder.button(text="🔄 Refresh", callback_data=current)
    builder.adjust(3)
    return builder.as_markup()


def add_nav_row(
    builder: InlineKeyboardBuilder,
    current: str,
    parent: str = "menu:main",
) -> None:
    """Append Back/Home/Refresh row to an existing builder.

    Call AFTER builder.adjust() so the nav row lands at the bottom
    and is not folded into the content layout.
    """
    builder.row(
        InlineKeyboardButton(text="⬅ Back",     callback_data=parent),
        InlineKeyboardButton(text="🏠 Home",    callback_data="menu:main"),
        InlineKeyboardButton(text="🔄 Refresh", callback_data=current),
    )
