"""Youth Trends router — category grid + paginated character lists."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.services.character_service import char_service

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


def _main_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _CATEGORIES:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:trends")
    return builder.as_markup()


def _char_list_keyboard(cat_id: str, page: int, total_pages: int, chars):
    """Build paginated character list keyboard."""
    builder = InlineKeyboardBuilder()
    for char in chars:
        builder.button(text=char.name, callback_data=f"char:{cat_id}:{char.id}")
    builder.adjust(2)

    # Pagination row
    if total_pages > 1:
        from aiogram.types import InlineKeyboardButton
        prev_cb = f"trends:{cat_id}:{max(0, page - 1)}" if page > 0 else "noop"
        next_cb = f"trends:{cat_id}:{page + 1}" if page < total_pages - 1 else "noop"
        left  = "◀" if page > 0 else " "
        right = "▶" if page < total_pages - 1 else " "
        info  = f"{page + 1}/{total_pages}"
        builder.row(
            InlineKeyboardButton(text=left,  callback_data=prev_cb),
            InlineKeyboardButton(text=info,  callback_data="noop"),
            InlineKeyboardButton(text=right, callback_data=next_cb),
        )

    add_nav_row(builder, current=f"trends:{cat_id}:{page}", parent="menu:trends")
    return builder.as_markup()


def _get_cat_id_and_page(data: str) -> tuple[str, int]:
    """Parse 'trends:marvel' → ('marvel', 0) or 'trends:marvel:2' → ('marvel', 2)."""
    parts = data.split(":", 2)  # ['trends', 'cat_id'] or ['trends', 'cat_id', 'page']
    cat_id = parts[1] if len(parts) >= 2 else ""
    page = int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else 0
    return cat_id, page


# ── handlers ─────────────────────────────────────────────────────


@router.callback_query(F.data == "menu:trends")
async def on_trends_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎮 <b>Youth Trends</b>\n\nChoose a category:",
        reply_markup=_main_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def on_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("trends:"))
async def on_trend_category(callback: CallbackQuery) -> None:
    cat_id, page = _get_cat_id_and_page(callback.data)
    cat = char_service.get_category(cat_id)
    chars, page, total_pages = char_service.get_page(cat_id, page)

    cat_name = cat.name if cat else cat_id.replace("_", " ").title()
    cat_icon = cat.icon if cat else "🎮"
    total_chars = len(char_service.get_characters(cat_id))

    if not chars:
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"{cat_icon} <b>{cat_name}</b>\n\n⏳ Characters coming soon.",
            reply_markup=get_nav_keyboard(current=callback.data, parent="menu:trends"),
        )
        await callback.answer()
        return

    header = (
        f"{cat_icon} <b>{cat_name}</b>\n"
        f"📋 {total_chars} characters  •  page {page + 1}/{total_pages}\n\n"
        "Select a character:"
    )
    await callback.message.edit_text(  # type: ignore[union-attr]
        header,
        reply_markup=_char_list_keyboard(cat_id, page, total_pages, chars),
    )
    await callback.answer()
