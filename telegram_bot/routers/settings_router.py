"""Settings router — ⚙️ 8-item grid with admin & about detail pages."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.utils.messages import FEATURE_SOON_TEXT

router = Router(name="settings")

_ITEMS: list[tuple[str, str]] = [
    ("👤 Admin",    "set:admin"),
    ("🌍 Language", "set:language"),
    ("🗄 Database", "set:database"),
    ("🚂 Railway",  "set:railway"),
    ("🐙 GitHub",   "set:github"),
    ("📄 Logs",     "set:logs"),
    ("♻ Cache",        "set:cache"),
    ("🔌 Integrations","set:integrations"),
    ("ℹ About",        "set:about"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}


def _settings_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:settings")
    return builder.as_markup()


@router.callback_query(F.data == "menu:settings")
async def on_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "⚙️ <b>Settings</b>\n\nBot configuration:",
        reply_markup=_settings_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "set:admin")
async def on_settings_admin(callback: CallbackQuery) -> None:
    from factory.core.config import settings

    text = (
        "👤 <b>Admin</b>\n\n"
        f"<b>ID:</b> <code>{settings.admin_id}</code>\n"
        "<b>Bot:</b> @Asilbek_2005bot\n"
        "<b>Access:</b> ✅ Full"
    )
    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=get_nav_keyboard(current="set:admin", parent="menu:settings"),
    )
    await callback.answer()


@router.callback_query(F.data == "set:about")
async def on_settings_about(callback: CallbackQuery) -> None:
    text = (
        "ℹ <b>About</b>\n\n"
        "<b>Bot:</b> YouTube AI Studio\n"
        "<b>Version:</b> 0.1.0\n"
        "<b>Framework:</b> Aiogram 3\n"
        "<b>Repo:</b> Asilbek0051707/botvideo\n"
        "<b>Author:</b> @klipso_A"
    )
    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=get_nav_keyboard(current="set:about", parent="menu:settings"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set:"))
async def on_settings_item(callback: CallbackQuery) -> None:
    label = _LABEL.get(callback.data, "Setting")
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n{FEATURE_SOON_TEXT}",
        reply_markup=get_nav_keyboard(current=callback.data, parent="menu:settings"),
    )
    await callback.answer()
