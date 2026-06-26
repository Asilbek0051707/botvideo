"""Material Finder router — 📦 14-item grid."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.utils.messages import FEATURE_SOON_TEXT

router = Router(name="materials")

_ITEMS: list[tuple[str, str]] = [
    ("🖼 PNG Images",       "mat:png"),
    ("🟢 Green Screen",     "mat:green_screen"),
    ("🎬 Animations",       "mat:animations"),
    ("🎞 GIF",              "mat:gif"),
    ("🎥 Videos",           "mat:videos"),
    ("🌄 Backgrounds",      "mat:backgrounds"),
    ("🎵 Music",            "mat:music"),
    ("🔊 Sound Effects",    "mat:sfx"),
    ("🎤 AI Voices",        "mat:ai_voices"),
    ("✨ Visual Effects",   "mat:vfx"),
    ("🖌 Thumbnail Assets", "mat:thumbnails"),
    ("🎨 AI Prompts",       "mat:prompts"),
    ("📂 Material Packs",   "mat:packs"),
    ("🌐 Internet Search",  "mat:internet"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}


def _materials_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:materials")
    return builder.as_markup()


@router.callback_query(F.data == "menu:materials")
async def on_materials(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📦 <b>Material Finder</b>\n\nChoose material type:",
        reply_markup=_materials_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mat:"))
async def on_material_item(callback: CallbackQuery) -> None:
    label = _LABEL.get(callback.data, "Material")
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n{FEATURE_SOON_TEXT}",
        reply_markup=get_nav_keyboard(current=callback.data, parent="menu:materials"),
    )
    await callback.answer()
