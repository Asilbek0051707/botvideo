"""Projects router — 📁 Projects module."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.utils.messages import FEATURE_SOON_TEXT

router = Router(name="projects")

_ITEMS: list[tuple[str, str]] = [
    ("📁 My Projects",     "proj:my"),
    ("➕ New Project",     "proj:new"),
    ("🗂 Saved Materials", "proj:saved"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}


def _projects_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:projects")
    return builder.as_markup()


@router.callback_query(F.data == "menu:projects")
async def on_projects(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📁 <b>Projects</b>\n\nManage your video projects:",
        reply_markup=_projects_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("proj:"))
async def on_project_action(callback: CallbackQuery) -> None:
    label = _LABEL.get(callback.data, "Projects")
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n{FEATURE_SOON_TEXT}",
        reply_markup=get_nav_keyboard(current=callback.data, parent="menu:projects"),
    )
    await callback.answer()
