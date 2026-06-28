"""Video Idea Generator — template-based ideas with save, search, manage."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row

router = Router(name="video_ideas")

_PAGE_SIZE = 5


class IdeaStates(StatesGroup):
    waiting_for_character = State()
    waiting_for_search    = State()


# ── entry ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "ta:video_ideas")
async def on_video_ideas_menu(callback: CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 Karakter bo'yicha g'oyalar", callback_data="vi:by_char")
    builder.button(text="💾 Saqlangan g'oyalar",          callback_data="vi:saved")
    builder.button(text="🔍 G'oya qidirish",              callback_data="vi:search")
    builder.adjust(1)
    add_nav_row(builder, current="ta:video_ideas", parent="menu:trend_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎯 <b>Video G'oya Generator</b>\n\n"
        "Karakter nomi yoki mavzu asosida\n"
        "YouTube Shorts uchun tayyor g'oyalar:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


# ── by character ───────────────────────────────────────────────────

@router.callback_query(F.data == "vi:by_char")
async def on_vi_by_char(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IdeaStates.waiting_for_character)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎬 <b>Karakter bo'yicha g'oyalar</b>\n\n"
        "Karakter nomini yozing:\n\n"
        "Misol: <code>Spider-Man</code>\n"
        "Yoki: <code>Minecraft Steve</code>"
    )
    await callback.answer()


@router.message(IdeaStates.waiting_for_character)
async def on_idea_character(message: Message, state: FSMContext) -> None:
    from telegram_bot.services import idea_service, viral_score

    character = (message.text or "").strip()
    await state.clear()
    if not character:
        await message.answer("❌ Bo'sh nom. Qayta urining.")
        return

    ideas = idea_service.generate_ideas(character, count=6)
    score, verdict, _ = viral_score.calculate(character)

    bar_filled = round(score / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)

    lines = [
        f"🎯 <b>{character}</b> uchun g'oyalar\n"
        f"📊 Viral Score: <code>[{bar}]</code> <b>{score}/100</b> — {verdict}\n"
    ]
    for i, idea in enumerate(ideas, 1):
        lines.append(
            f"{i}. <b>{idea['title']}</b>\n"
            f"   📝 {idea['description']}\n"
            f"   ⏱ {idea['length']} | 👥 {idea['audience']}"
        )

    builder = InlineKeyboardBuilder()
    for i in range(min(6, len(ideas))):
        builder.button(text=f"💾 {i+1}. Saqlash", callback_data=f"vi_save:{i}")
    builder.adjust(2)
    builder.button(text="🔄 Yangi g'oyalar", callback_data="vi:by_char")
    builder.button(text="⬅ Orqaga",          callback_data="ta:video_ideas")
    builder.adjust(2)

    await state.update_data(last_ideas=ideas, last_char=character)
    await message.answer("\n\n".join(lines), reply_markup=builder.as_markup())


# ── save idea ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("vi_save:"))
async def on_vi_save(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services import idea_service, viral_score

    idx = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    last_ideas: list[dict] = data.get("last_ideas", [])

    if idx >= len(last_ideas):
        await callback.answer("❌ G'oya topilmadi")
        return

    idea = last_ideas[idx]
    score, _, _ = viral_score.calculate(idea.get("character", ""))
    saved_id = await idea_service.save_idea(
        title=idea["title"],
        description=idea["description"],
        character=idea.get("character", ""),
        category=idea.get("category", "general"),
        score=score,
        keywords=idea.get("keywords", []),
    )
    await callback.answer(f"✅ Saqlandi! #{saved_id}", show_alert=False)


# ── search ideas ───────────────────────────────────────────────────

@router.callback_query(F.data == "vi:search")
async def on_vi_search(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IdeaStates.waiting_for_search)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔍 <b>G'oya qidirish</b>\n\n"
        "Kalit so'z yozing:\n"
        "Misol: <code>battle</code>, <code>evolution</code>, <code>funny</code>, <code>baby</code>"
    )
    await callback.answer()


@router.message(IdeaStates.waiting_for_search)
async def on_idea_search(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.idea_service import search_templates

    keyword = (message.text or "").strip().lower()
    await state.clear()
    if not keyword:
        return

    matched = search_templates(keyword)[:6]
    lines = [f"🔍 <b>'{keyword}'</b> bo'yicha shablon g'oyalar:\n"]
    for i, t in enumerate(matched, 1):
        title = t["title"].format(char="[Karakter]", char1="[Char1]", char2="[Char2]")
        lines.append(
            f"{i}. <b>{title}</b>\n"
            f"   📝 {t['desc']}\n"
            f"   ⏱ {t.get('length', '60s')} | 👥 {t.get('audience', 'all')}"
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 Karakter bilan to'ldirish", callback_data="vi:by_char")
    builder.button(text="⬅ Orqaga",                     callback_data="ta:video_ideas")
    builder.adjust(1)

    await message.answer("\n\n".join(lines), reply_markup=builder.as_markup())


# ── saved ideas list ───────────────────────────────────────────────

@router.callback_query(F.data == "vi:saved")
async def on_vi_saved(callback: CallbackQuery) -> None:
    from telegram_bot.services import idea_service

    ideas = await idea_service.list_ideas(limit=_PAGE_SIZE)
    if not ideas:
        builder = InlineKeyboardBuilder()
        builder.button(text="🎬 G'oya yaratish", callback_data="vi:by_char")
        builder.button(text="⬅ Orqaga",           callback_data="ta:video_ideas")
        builder.adjust(1)
        await callback.message.edit_text(  # type: ignore[union-attr]
            "💾 <b>Saqlangan g'oyalar</b>\n\n"
            "Hali hech qanday g'oya saqlanmagan.\n"
            "G'oya yaratib, 'Saqlash' tugmasini bosing!",
            reply_markup=builder.as_markup(),
        )
        await callback.answer()
        return

    lines = [f"💾 <b>Saqlangan g'oyalar</b> ({len(ideas)} ta):\n"]
    for i, idea in enumerate(ideas, 1):
        lines.append(
            f"{i}. <b>{idea.title}</b>\n"
            f"   🎭 {idea.character or '—'} | 📊 {idea.trend_score}/100\n"
            f"   📝 {idea.description[:55]}…"
        )

    builder = InlineKeyboardBuilder()
    for i, idea in enumerate(ideas, 1):
        builder.button(text=f"🗑 {i}. O'chirish", callback_data=f"vi_del:{idea.id}")
    builder.adjust(2)
    builder.button(text="🎬 Yangi g'oya", callback_data="vi:by_char")
    builder.button(text="⬅ Orqaga",      callback_data="ta:video_ideas")
    builder.adjust(2)

    await callback.message.edit_text(  # type: ignore[union-attr]
        "\n".join(lines), reply_markup=builder.as_markup()
    )
    await callback.answer()


# ── delete idea ────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("vi_del:"))
async def on_vi_delete(callback: CallbackQuery) -> None:
    from telegram_bot.services import idea_service

    idea_id = int(callback.data.split(":", 1)[1])
    await idea_service.delete_idea(idea_id)
    await callback.answer("🗑 O'chirildi")
    await on_vi_saved(callback)
