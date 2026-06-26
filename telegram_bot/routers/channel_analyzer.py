"""Channel Analyzer router — 📊 6-item grid."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.utils.messages import FEATURE_SOON_TEXT

router = Router(name="channel_analyzer")

_ITEMS: list[tuple[str, str]] = [
    ("🔗 Analyze Channel",   "ca:channel"),
    ("🎥 Analyze Video",     "ca:video"),
    ("🖼 Analyze Thumbnail", "ca:thumbnail"),
    ("🏆 Competitors",       "ca:competitors"),
    ("📈 Growth Prediction", "ca:growth"),
    ("📊 Statistics",        "ca:statistics"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}


def _ca_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:channel_analyzer")
    return builder.as_markup()


@router.callback_query(F.data == "menu:channel_analyzer")
async def on_channel_analyzer(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📊 <b>Channel Analyzer</b>\n\nChoose an analysis:",
        reply_markup=_ca_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ca:"))
async def on_ca_item(callback: CallbackQuery) -> None:
    label = _LABEL.get(callback.data, "Analysis")
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n{FEATURE_SOON_TEXT}",
        reply_markup=get_nav_keyboard(current=callback.data, parent="menu:channel_analyzer"),
    )
    await callback.answer()
