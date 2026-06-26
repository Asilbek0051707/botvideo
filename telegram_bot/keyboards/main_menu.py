"""Inline keyboard builders for the main menu."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Youth Trends",     callback_data="menu:trends")
    builder.button(text="📦 Material Finder",  callback_data="menu:materials")
    builder.button(text="📈 Trend Analyzer",   callback_data="menu:trend_analyzer")
    builder.button(text="📊 Channel Analyzer", callback_data="menu:channel_analyzer")
    builder.button(text="🤖 AI Generator",     callback_data="menu:ai_generator")
    builder.button(text="📁 Projects",         callback_data="menu:projects")
    builder.button(text="📊 Statistics",       callback_data="menu:statistics")
    builder.button(text="⚙️ Settings",          callback_data="menu:settings")
    builder.button(text="🔄 Refresh",          callback_data="menu:main")
    # Layout: 2-2-2-2-1
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Legacy single-button Back keyboard (kept for dashboard.py compatibility)."""
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Main Menu", callback_data="menu:main")
    return builder.as_markup()
