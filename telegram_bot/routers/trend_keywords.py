"""Trending Keywords — browse, search and filter keyword engine."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row

router = Router(name="trend_keywords")

_LEVEL_EMOJI = {"viral": "🔥", "high": "📈", "medium": "📊", "low": "📉"}
_CAT_EMOJI   = {
    "cartoon":  "🎭", "gaming": "🎮", "anime": "🎌",
    "meme":     "😂", "kids":   "🧸", "general": "🌐",
    "movie":    "🎬", "challenge": "💪", "idea": "💡",
    "character": "🦸",
}

_FILTER_CATS = [
    ("🎭 Cartoon",   "cartoon"),
    ("🎮 Gaming",    "gaming"),
    ("🎌 Anime",     "anime"),
    ("😂 Meme",      "meme"),
    ("🎬 Movie",     "movie"),
    ("💡 G'oya",     "idea"),
    ("🌐 Hammasi",   "all"),
]


class KwStates(StatesGroup):
    waiting_for_search = State()


# ── entry ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "ta:trend_keywords")
async def on_trend_keywords(callback: CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Top Kalit So'zlar",   callback_data="kw:top")
    builder.button(text="🔍 Kalit So'z Qidirish", callback_data="kw:search")
    for label, cat in _FILTER_CATS[:-1]:
        builder.button(text=label, callback_data=f"kw:cat:{cat}")
    builder.adjust(2)
    add_nav_row(builder, current="ta:trend_keywords", parent="menu:trend_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        "🏷 <b>Trending Kalit So'zlar</b>\n\n"
        "YouTube Shorts uchun eng qidiriladigan\n"
        "va viral kalit so'zlar:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


# ── top keywords ───────────────────────────────────────────────────

@router.callback_query(F.data == "kw:top")
async def on_kw_top(callback: CallbackQuery) -> None:
    from telegram_bot.services import keyword_service

    kws = await keyword_service.list_keywords(limit=12, sort="priority")
    await _show_keywords(callback, kws, "🔥 <b>Top Kalit So'zlar</b>", "kw:top")


# ── category filter ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("kw:cat:"))
async def on_kw_cat(callback: CallbackQuery) -> None:
    from telegram_bot.services import keyword_service

    cat = callback.data.split(":", 2)[2]
    cat_label = next((l for l, c in _FILTER_CATS if c == cat), cat)
    kws = await keyword_service.list_keywords(category=cat if cat != "all" else None, limit=12)
    await _show_keywords(callback, kws, f"{cat_label} kalit so'zlar", f"kw:cat:{cat}")


# ── search ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "kw:search")
async def on_kw_search(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(KwStates.waiting_for_search)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔍 <b>Kalit so'z qidirish</b>\n\n"
        "So'z yozing:\n"
        "Misol: <code>sonic</code>, <code>battle</code>, <code>funny</code>"
    )
    await callback.answer()


@router.message(KwStates.waiting_for_search)
async def on_kw_search_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services import keyword_service

    query = (message.text or "").strip()
    await state.clear()
    if not query:
        return

    kws = await keyword_service.search(query, limit=10)

    if not kws:
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅ Orqaga", callback_data="ta:trend_keywords")
        await message.answer(
            f"❌ <b>'{query}'</b> bo'yicha natija topilmadi.",
            reply_markup=builder.as_markup(),
        )
        return

    lines = [f"🔍 <b>'{query}'</b> bo'yicha kalit so'zlar:\n"]
    for kw in kws:
        import json
        related = json.loads(kw.related_keywords or "[]")
        lvl_emoji = _LEVEL_EMOJI.get(kw.trend_level, "📊")
        cat_emoji = _CAT_EMOJI.get(kw.category, "🌐")
        related_str = ", ".join(related[:3]) if related else "—"
        lines.append(
            f"{lvl_emoji} <b>{kw.keyword}</b> {cat_emoji}\n"
            f"   🔗 {related_str}"
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Qayta qidirish", callback_data="kw:search")
    builder.button(text="⬅ Orqaga",          callback_data="ta:trend_keywords")
    builder.adjust(2)

    await message.answer("\n\n".join(lines), reply_markup=builder.as_markup())


# ── shared display helper ──────────────────────────────────────────

async def _show_keywords(
    callback: CallbackQuery,
    kws: list,
    title: str,
    back_cb: str,
) -> None:
    import json

    if not kws:
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅ Orqaga", callback_data="ta:trend_keywords")
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"{title}\n\n❌ Ma'lumot topilmadi.",
            reply_markup=builder.as_markup(),
        )
        await callback.answer()
        return

    lines = [f"{title}\n"]
    for kw in kws:
        related = json.loads(kw.related_keywords or "[]")
        lvl_emoji = _LEVEL_EMOJI.get(kw.trend_level, "📊")
        cat_emoji  = _CAT_EMOJI.get(kw.category, "🌐")
        related_str = ", ".join(related[:3]) if related else "—"
        lines.append(
            f"{lvl_emoji} <b>{kw.keyword}</b> {cat_emoji}\n"
            f"   🔗 {related_str}"
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Qidirish",          callback_data="kw:search")
    builder.button(text="🔄 Yangilash",          callback_data=back_cb)
    builder.button(text="⬅ Kalit So'zlar Menyu", callback_data="ta:trend_keywords")
    builder.adjust(2, 1)

    await callback.message.edit_text(  # type: ignore[union-attr]
        "\n\n".join(lines), reply_markup=builder.as_markup()
    )
    await callback.answer()
