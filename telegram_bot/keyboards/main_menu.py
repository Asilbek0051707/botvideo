"""Inline keyboard builders for the main menu and navigation."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Dashboard",        callback_data="menu:dashboard")
    builder.button(text="🎮 Youth Trends",     callback_data="menu:trends")
    builder.button(text="📦 Material Finder",  callback_data="menu:materials")
    builder.button(text="📈 Trend Analyzer",   callback_data="menu:trend_analyzer")
    builder.button(text="📊 Channel Analyzer", callback_data="menu:channel_analyzer")
    builder.button(text="🤖 AI Generator",     callback_data="menu:ai_generator")
    builder.button(text="⚙️ Settings",          callback_data="menu:settings")
    # Layout: 1 | 2 | 2 | 1 | 1
    builder.adjust(1, 2, 2, 1, 1)
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Main Menu", callback_data="menu:main")
    return builder.as_markup()
