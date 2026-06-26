"""Trend Analyzer router — 📈 7-item grid."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.utils.messages import FEATURE_SOON_TEXT

router = Router(name="trend_analyzer")

_ITEMS: list[tuple[str, str]] = [
    ("🔥 Trending Characters", "ta:trending_chars"),
    ("🎵 Trending Music",      "ta:trending_music"),
    ("🎮 Trending Gameplay",   "ta:trending_gameplay"),
    ("😂 Trending Memes",      "ta:trending_memes"),
    ("📈 Trending Shorts",     "ta:trending_shorts"),
    ("🌍 Country Trends",      "ta:country_trends"),
    ("📊 Viral Score",         "ta:viral_score"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}


def _ta_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:trend_analyzer")
    return builder.as_markup()


@router.callback_query(F.data == "menu:trend_analyzer")
async def on_trend_analyzer(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📈 <b>Trend Analyzer</b>\n\nChoose an analysis type:",
        reply_markup=_ta_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ta:"))
async def on_ta_item(callback: CallbackQuery) -> None:
    label = _LABEL.get(callback.data, "Analysis")
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n{FEATURE_SOON_TEXT}",
        reply_markup=get_nav_keyboard(current=callback.data, parent="menu:trend_analyzer"),
    )
    await callback.answer()
