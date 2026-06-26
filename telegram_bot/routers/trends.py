"""Youth Trends router — 🎮 24-category grid."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.utils.messages import FEATURE_SOON_TEXT

router = Router(name="trends")

_CATEGORIES: list[tuple[str, str]] = [
    ("🎮 Tiles Hop",              "trends:tiles_hop"),
    ("🎭 Famous Characters",      "trends:famous_chars"),
    ("🧩 Sprunki",                "trends:sprunki"),
    ("📈 Character Evolution",    "trends:char_evo"),
    ("⚔ Char VS Character",      "trends:char_vs"),
    ("🔷 Geometry Dash",          "trends:geometry"),
    ("🚇 Subway Surfers",         "trends:subway"),
    ("⛏ Minecraft Parkour",      "trends:minecraft"),
    ("🎙 AI Stories",             "trends:ai_stories"),
    ("❓ Guess Character",        "trends:guess"),
    ("👹 Horror EXE",             "trends:horror"),
    ("🦸 Marvel",                 "trends:marvel"),
    ("🦇 DC",                     "trends:dc"),
    ("🏰 Disney",                 "trends:disney"),
    ("🎌 Anime",                  "trends:anime"),
    ("🟩 Roblox",                 "trends:roblox"),
    ("🦔 Sonic",                  "trends:sonic"),
    ("🍄 Mario",                  "trends:mario"),
    ("🐶 Paw Patrol",             "trends:paw_patrol"),
    ("🔵 Bluey",                  "trends:bluey"),
    ("🚽 Skibidi Toilet",         "trends:skibidi"),
    ("🧸 Poppy Playtime",         "trends:poppy"),
    ("🌈 Rainbow Friends",        "trends:rainbow"),
    ("🎪 Amazing Digital Circus", "trends:circus"),
]

_LABEL: dict[str, str] = {data: label for label, data in _CATEGORIES}


def _trends_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _CATEGORIES:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:trends")
    return builder.as_markup()


@router.callback_query(F.data == "menu:trends")
async def on_trends(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎮 <b>Youth Trends</b>\n\nChoose a category:",
        reply_markup=_trends_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("trends:"))
async def on_trend_category(callback: CallbackQuery) -> None:
    label = _LABEL.get(callback.data, "Category")
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n{FEATURE_SOON_TEXT}",
        reply_markup=get_nav_keyboard(current=callback.data, parent="menu:trends"),
    )
    await callback.answer()
