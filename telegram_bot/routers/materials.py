"""Material Finder router — 📦 browse material types + search providers."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.services.search_service import search_service

router = Router(name="materials")

_ITEMS: list[tuple[str, str]] = [
    ("🖼 PNG Images",       "mat:png"),
    ("🟢 Green Screen",     "mat:gs"),
    ("🎬 Animations",       "mat:anim"),
    ("🎞 GIF",              "mat:gif"),
    ("🎥 Videos",           "mat:vid"),
    ("🌄 Backgrounds",      "mat:bg"),
    ("🎵 Music",            "mat:mus"),
    ("🔊 Sound Effects",    "mat:sfx"),
    ("🎤 AI Voices",        "mat:voice"),
    ("✨ Visual Effects",   "mat:fx"),
    ("🖌 Thumbnail Assets", "mat:thumb"),
    ("🎨 AI Prompts",       "mat:prompts"),
    ("📂 Material Packs",   "mat:pack"),
    ("🌐 Internet Search",  "mat:search"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}

_MAT_KEYWORDS: dict[str, str] = {
    "mat:png":    "transparent PNG",
    "mat:gs":     "green screen video",
    "mat:anim":   "animation loop",
    "mat:gif":    "animated GIF",
    "mat:vid":    "video clip",
    "mat:bg":     "background wallpaper",
    "mat:mus":    "background music",
    "mat:sfx":    "sound effect",
    "mat:voice":  "voice sample AI",
    "mat:fx":     "visual effect particle",
    "mat:thumb":  "YouTube thumbnail template",
    "mat:prompts":"AI art prompt",
    "mat:pack":   "asset pack bundle",
    "mat:search": "free stock assets",
}


def _materials_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:materials")
    return builder.as_markup()


def _provider_keyboard(mat_cb: str, keyword: str):
    """Provider URL buttons for a generic material search (no character)."""
    from telegram_bot.services.providers.stubs import _MAT_MODIFIERS
    mat_code = mat_cb.split(":")[1]
    builder = InlineKeyboardBuilder()
    for label, url in search_service.build_links(keyword, mat_code):
        builder.button(text=label, url=url)
    builder.adjust(1)
    add_nav_row(builder, current=mat_cb, parent="menu:materials")
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
    keyword = _MAT_KEYWORDS.get(callback.data, "asset")
    mat_code = callback.data.split(":")[1]

    # AI Prompts is information-only for now
    if mat_code == "prompts":
        await callback.message.edit_text(  # type: ignore[union-attr]
            "🎨 <b>AI Prompts</b>\n\n"
            "For character-specific AI prompts, open a character page and tap <b>🎨 AI Prompts</b>.",
            reply_markup=get_nav_keyboard(current=callback.data, parent="menu:materials"),
        )
        await callback.answer()
        return

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n"
        f"🔍 Search for: <b>{keyword}</b>\n\n"
        "Choose a provider — each button opens in your browser:",
        reply_markup=_provider_keyboard(callback.data, keyword),
    )
    await callback.answer()
