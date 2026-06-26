"""AI Generator router — 🤖 9-item grid."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.utils.messages import FEATURE_SOON_TEXT

router = Router(name="ai_generator")

_ITEMS: list[tuple[str, str]] = [
    ("📝 Script Generator",      "ai:script"),
    ("🏷 Title Generator",       "ai:title"),
    ("📄 Description",           "ai:description"),
    ("#️⃣ Tags Generator",        "ai:tags"),
    ("🖼 Image Prompt",          "ai:image_prompt"),
    ("🎨 Thumbnail Prompt",      "ai:thumbnail_prompt"),
    ("🎬 Video Prompt",          "ai:video_prompt"),
    ("🎤 Voice Prompt",          "ai:voice_prompt"),
    ("📈 SEO Generator",         "ai:seo"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}


def _ai_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(3)
    add_nav_row(builder, current="menu:ai_generator")
    return builder.as_markup()


@router.callback_query(F.data == "menu:ai_generator")
async def on_ai_generator(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🤖 <b>AI Generator</b>\n\nChoose a generator:",
        reply_markup=_ai_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ai:"))
async def on_ai_item(callback: CallbackQuery) -> None:
    label = _LABEL.get(callback.data, "Generator")
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n{FEATURE_SOON_TEXT}",
        reply_markup=get_nav_keyboard(current=callback.data, parent="menu:ai_generator"),
    )
    await callback.answer()
