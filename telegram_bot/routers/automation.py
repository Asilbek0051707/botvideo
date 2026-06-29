"""AI Automation Engine router — STEP 10.

Entry: menu:auto

8-item main menu:
  ⚡ Quick Generate     auto:quick
  🎬 Full Video Package auto:full
  📦 Create Project     auto:proj
  🤖 AI Assistant       auto:ai
  📅 Auto Planner       auto:plan
  📝 Workflow History   auto:hist
  ⭐ Favorite Workflows  auto:fav
  ⚙ Settings           auto:cfg

FSM states — all wait for text input, then process and show result.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard

router = Router(name="automation")


# ─────────────────────────────────────────────────────────────────
# FSM
# ─────────────────────────────────────────────────────────────────

class AutoStates(StatesGroup):
    waiting_for_quick_topic   = State()
    waiting_for_package_topic = State()
    waiting_for_project_idea  = State()
    waiting_for_assistant_msg = State()   # conversational loop
    waiting_for_planner_topic = State()
    waiting_for_workflow_topic= State()


# ─────────────────────────────────────────────────────────────────
# KEYBOARDS
# ─────────────────────────────────────────────────────────────────

_MENU: list[tuple[str, str]] = [
    ("⚡ Quick Generate",     "auto:quick"),
    ("🎬 Full Video Package", "auto:full"),
    ("📦 Create Project",     "auto:proj"),
    ("🤖 AI Assistant",       "auto:ai"),
    ("📅 Auto Planner",       "auto:plan"),
    ("📝 Workflow History",   "auto:hist"),
    ("⭐ Favorites",          "auto:fav"),
    ("⚙ Settings",           "auto:cfg"),
]


def _main_kb():
    b = InlineKeyboardBuilder()
    for label, data in _MENU:
        b.button(text=label, callback_data=data)
    b.adjust(2)
    add_nav_row(b, current="menu:auto")
    return b.as_markup()


def _cancel_kb(parent: str = "menu:auto"):
    b = InlineKeyboardBuilder()
    b.button(text="❌ Bekor qilish", callback_data=parent)
    return b.as_markup()


def _result_kb(run_id: int, parent: str = "menu:auto"):
    b = InlineKeyboardBuilder()
    b.button(text="⭐ Saqlash",      callback_data=f"auto:fav_run:{run_id}")
    b.button(text="🔄 Qayta",        callback_data=parent)
    b.button(text="◀ Menyu",         callback_data="menu:auto")
    b.adjust(2)
    return b.as_markup()


def _section_back_kb():
    b = InlineKeyboardBuilder()
    b.button(text="◀ Orqaga", callback_data="menu:auto")
    return b.as_markup()


# ─────────────────────────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:auto")
async def on_auto_menu(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    from telegram_bot.services.automation_service import run_stats
    stats = await run_stats()
    text = (
        "🚀 <b>AI Automation Engine</b>\n\n"
        f"📊 Jami ishlar: <b>{stats['total']}</b>\n"
        f"⭐ Sevimlilar: <b>{stats['favorites']}</b>\n\n"
        "Avtonom kontent ishlab chiqarish tizimi.\n"
        "Bitta mavzu → to'liq paket."
    )
    await cb.message.edit_text(text, reply_markup=_main_kb())  # type: ignore[union-attr]
    await cb.answer()


# ─────────────────────────────────────────────────────────────────
# ⚡ QUICK GENERATE
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "auto:quick")
async def on_quick_start(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AutoStates.waiting_for_quick_topic)
    await cb.message.edit_text(  # type: ignore[union-attr]
        "⚡ <b>Quick Generate</b>\n\n"
        "Mavzuni kiriting:\n"
        "<i>Misol: Spider-Man vs Hulk Tiles Hop</i>",
        reply_markup=_cancel_kb(),
    )
    await cb.answer()


@router.message(StateFilter(AutoStates.waiting_for_quick_topic))
async def on_quick_topic(msg: Message, state: FSMContext) -> None:
    topic = (msg.text or "").strip()
    if not topic:
        await msg.answer("❗ Mavzuni kiriting.", reply_markup=_cancel_kb())
        return

    await state.clear()
    wait_msg = await msg.answer("⚡ <b>Generatsiya boshlandi...</b>\n⏳ Barcha generatorlar parallel ishlayapti...")

    from telegram_bot.services.automation_service import quick_generate, save_run, format_quick_result_summary

    result = await quick_generate(topic)
    run_id = await save_run(
        topic=topic,
        run_type="quick",
        result=result.to_dict(),
        duration_ms=result.duration_ms,
    )

    summary = format_quick_result_summary(result)
    await wait_msg.edit_text(summary, reply_markup=_result_kb(run_id, "auto:quick"))


# ─────────────────────────────────────────────────────────────────
# Quick result — show individual sections
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("auto:qshow:"))
async def on_quick_show_section(cb: CallbackQuery) -> None:
    parts  = cb.data.split(":", 3)   # auto:qshow:{run_id}:{section}  # type: ignore[union-attr]
    if len(parts) < 4:
        await cb.answer()
        return
    run_id, section = int(parts[2]), parts[3]

    from telegram_bot.services.automation_service import get_run
    import json

    run = await get_run(run_id)
    if not run:
        await cb.answer("Topilmadi", show_alert=True)
        return

    data = json.loads(run.result_json)
    text_map = {
        "script":     ("📝 Script",     data.get("script", "—")),
        "desc":       ("📄 Description", data.get("description", "—")),
        "thumb":      ("🎨 Thumbnail",   data.get("thumbnail_prompt", "—")),
        "image":      ("🖼 Image",       data.get("image_prompt", "—")),
        "anim":       ("🎥 Animation",   data.get("animation_prompt", "—")),
        "voice":      ("🎙 Voice",       data.get("voice_prompt", "—")),
        "idea":       ("💡 Video Idea",  data.get("video_idea", "—")),
    }
    label, content = text_map.get(section, ("Section", "—"))
    b = InlineKeyboardBuilder()
    b.button(text="◀ Natijaga", callback_data=f"auto:qback:{run_id}")
    await cb.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n{content[:3500]}",
        reply_markup=b.as_markup(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("auto:qback:"))
async def on_quick_back(cb: CallbackQuery) -> None:
    run_id = int(cb.data.split(":", 2)[2])  # type: ignore[union-attr]
    from telegram_bot.services.automation_service import get_run, format_quick_result_summary, QuickResult
    import json

    run = await get_run(run_id)
    if not run:
        cb.data = "menu:auto"  # type: ignore[union-attr]
        await on_auto_menu(cb, None)  # type: ignore[arg-type]
        return

    data = json.loads(run.result_json)
    result = QuickResult(
        topic=data.get("topic", ""),
        titles=data.get("titles", []),
        tags=data.get("tags", []),
        hashtags=data.get("hashtags", []),
        music=data.get("music", []),
        seo_summary=data.get("seo_summary", ""),
        upload_time=data.get("upload_time", ""),
        description=data.get("description", ""),
    )
    summary = format_quick_result_summary(result)
    await cb.message.edit_text(summary, reply_markup=_result_kb(run_id, "auto:quick"))  # type: ignore[union-attr]
    await cb.answer()


# ─────────────────────────────────────────────────────────────────
# 🎬 FULL VIDEO PACKAGE
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "auto:full")
async def on_full_start(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AutoStates.waiting_for_package_topic)
    await cb.message.edit_text(  # type: ignore[union-attr]
        "🎬 <b>Full Video Package</b>\n\n"
        "Karakter/mavzuni kiriting:\n"
        "<i>Misol: Minecraft Steve vs Creeper</i>",
        reply_markup=_cancel_kb(),
    )
    await cb.answer()


@router.message(StateFilter(AutoStates.waiting_for_package_topic))
async def on_full_topic(msg: Message, state: FSMContext) -> None:
    topic = (msg.text or "").strip()
    if not topic:
        await msg.answer("❗ Mavzuni kiriting.", reply_markup=_cancel_kb())
        return

    await state.clear()
    wait_msg = await msg.answer("🎬 <b>To'liq paket generatsiyasi...</b>\n⏳ Iltimos kuting...")

    from telegram_bot.services.automation_service import full_package, save_run

    pkg = await full_package(topic)
    run_id = await save_run(
        topic=topic,
        run_type="package",
        result={"summary": pkg["summary"], "duration_ms": pkg["duration_ms"]},
        duration_ms=pkg["duration_ms"],
    )

    summary = pkg["summary"]
    if len(summary) > 3800:
        summary = summary[:3800] + "\n\n<i>... (qisqartirildi)</i>"

    await wait_msg.edit_text(summary, reply_markup=_result_kb(run_id, "auto:full"))


# ─────────────────────────────────────────────────────────────────
# 📦 CREATE PROJECT FROM IDEA
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "auto:proj")
async def on_proj_start(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AutoStates.waiting_for_project_idea)
    await cb.message.edit_text(  # type: ignore[union-attr]
        "📦 <b>Loyiha yaratish</b>\n\n"
        "G'oyangizni kiriting:\n"
        "<i>Misol: Sonic Roblox Obby Challenge video</i>",
        reply_markup=_cancel_kb(),
    )
    await cb.answer()


@router.message(StateFilter(AutoStates.waiting_for_project_idea))
async def on_proj_idea(msg: Message, state: FSMContext) -> None:
    idea = (msg.text or "").strip()
    if not idea:
        await msg.answer("❗ G'oyani kiriting.", reply_markup=_cancel_kb())
        return

    await state.clear()
    wait_msg = await msg.answer("📦 <b>Loyiha yaratilmoqda...</b>")

    from telegram_bot.services.automation_service import create_project_from_idea, save_run

    project_id = await create_project_from_idea(idea)
    run_id     = await save_run(
        topic=idea,
        run_type="project",
        result={"project_id": project_id},
    )

    b = InlineKeyboardBuilder()
    b.button(text="📁 Loyihani ko'rish",  callback_data=f"prj:view:{project_id}")
    b.button(text="⭐ Saqlash",           callback_data=f"auto:fav_run:{run_id}")
    b.button(text="◀ Menyu",             callback_data="menu:auto")
    b.adjust(1)
    await wait_msg.edit_text(
        f"✅ <b>Loyiha yaratildi!</b>\n\n"
        f"📋 <b>ID:</b> #{project_id}\n"
        f"💡 <b>G'oya:</b> {idea}\n\n"
        f"5 ta standart vazifa qo'shildi.\n"
        f"Loyihani <b>📁 Loyihani ko'rish</b> tugmasi orqali oching.",
        reply_markup=b.as_markup(),
    )


# ─────────────────────────────────────────────────────────────────
# 🤖 AI ASSISTANT
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "auto:ai")
async def on_ai_start(cb: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.ai_assistant_service import get_preferred_provider

    provider = get_preferred_provider()
    prov_name = provider.config.name if provider else "Mahalliy shablon"

    await state.set_state(AutoStates.waiting_for_assistant_msg)
    await state.update_data(ai_history=[], ai_session=f"user_{cb.from_user.id}")  # type: ignore[union-attr]

    b = InlineKeyboardBuilder()
    b.button(text="💡 Video g'oyalar",       callback_data="auto:ai_hint:idea")
    b.button(text="🏷 Title maslahat",       callback_data="auto:ai_hint:title")
    b.button(text="📝 Script tuzilmasi",     callback_data="auto:ai_hint:script")
    b.button(text="🎨 Thumbnail maslahat",   callback_data="auto:ai_hint:thumbnail")
    b.button(text="🔄 Suhbatni tozalash",    callback_data="auto:ai_clear")
    b.button(text="❌ Chiqish",              callback_data="menu:auto")
    b.adjust(2)

    await cb.message.edit_text(  # type: ignore[union-attr]
        f"🤖 <b>AI Assistant</b>\n\n"
        f"Provayder: <b>{prov_name}</b>\n\n"
        "Savolingizni yozing yoki pastdagi tezkor tugmalardan birini tanlang:\n\n"
        "<i>Misol: Spider-Man uchun 5 ta title yozing</i>",
        reply_markup=b.as_markup(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("auto:ai_hint:"))
async def on_ai_hint(cb: CallbackQuery, state: FSMContext) -> None:
    hint_map = {
        "idea":      "Give me 5 YouTube Shorts ideas for gaming content",
        "title":     "Give me better title suggestions for my latest video",
        "script":    "Explain the best script structure for a 60-second Shorts video",
        "thumbnail": "Give me tips for creating a high CTR YouTube thumbnail",
    }
    hint_key = cb.data.split(":", 2)[2]  # type: ignore[union-attr]
    message  = hint_map.get(hint_key, "Help me with my YouTube channel")

    await state.set_state(AutoStates.waiting_for_assistant_msg)
    data   = await state.get_data()
    history: list[dict] = data.get("ai_history", [])
    session: str        = data.get("ai_session", f"user_{cb.from_user.id}")  # type: ignore[union-attr]

    await cb.message.edit_text(f"🤖 <b>AI Assistant</b>\n\n💬 <i>{message}</i>\n\n⏳ Javob tayyorlanmoqda...")  # type: ignore[union-attr]
    await cb.answer()

    from telegram_bot.services.ai_assistant_service import chat_with_ai, save_conversation, get_preferred_provider

    reply     = await chat_with_ai(message, history)
    history.append({"role": "user",      "content": message})
    history.append({"role": "assistant", "content": reply})
    if len(history) > 20:
        history = history[-20:]

    provider  = get_preferred_provider()
    prov_slug = provider.config.slug if provider else "local"
    await save_conversation(session, history, prov_slug)
    await state.update_data(ai_history=history)

    b = InlineKeyboardBuilder()
    b.button(text="🔄 Yangi savol",       callback_data="auto:ai")
    b.button(text="🔄 Suhbatni tozalash", callback_data="auto:ai_clear")
    b.button(text="◀ Menyu",             callback_data="menu:auto")
    b.adjust(2)
    await cb.message.edit_text(  # type: ignore[union-attr]
        f"🤖 <b>AI Assistant</b>\n\n{reply[:3500]}",
        reply_markup=b.as_markup(),
    )


@router.callback_query(F.data == "auto:ai_clear")
async def on_ai_clear(cb: CallbackQuery, state: FSMContext) -> None:
    data    = await state.get_data()
    session = data.get("ai_session", f"user_{cb.from_user.id}")  # type: ignore[union-attr]
    from telegram_bot.services.ai_assistant_service import clear_conversation
    await clear_conversation(session)
    await state.update_data(ai_history=[])
    await cb.answer("✅ Suhbat tozalandi", show_alert=True)
    cb.data = "auto:ai"  # type: ignore[union-attr]
    await on_ai_start(cb, state)


@router.message(StateFilter(AutoStates.waiting_for_assistant_msg))
async def on_assistant_message(msg: Message, state: FSMContext) -> None:
    text = (msg.text or "").strip()
    if not text:
        return

    data    = await state.get_data()
    history: list[dict] = data.get("ai_history", [])
    session: str        = data.get("ai_session", f"user_{msg.from_user.id}")  # type: ignore[union-attr]

    wait_msg = await msg.answer("⏳ <b>AI javob tayyorlanmoqda...</b>")

    from telegram_bot.services.ai_assistant_service import chat_with_ai, save_conversation, get_preferred_provider

    reply     = await chat_with_ai(text, history)
    history.append({"role": "user",      "content": text})
    history.append({"role": "assistant", "content": reply})
    if len(history) > 20:
        history = history[-20:]

    provider  = get_preferred_provider()
    prov_slug = provider.config.slug if provider else "local"
    await save_conversation(session, history, prov_slug)
    await state.update_data(ai_history=history)

    b = InlineKeyboardBuilder()
    b.button(text="🔄 Suhbatni tozalash", callback_data="auto:ai_clear")
    b.button(text="◀ Menyu",             callback_data="menu:auto")
    b.adjust(2)
    await wait_msg.edit_text(
        f"🤖 <b>AI Assistant</b>\n\n{reply[:3500]}",
        reply_markup=b.as_markup(),
    )


# ─────────────────────────────────────────────────────────────────
# 📅 AUTO PLANNER
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "auto:plan")
async def on_planner_start(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AutoStates.waiting_for_planner_topic)
    await cb.message.edit_text(  # type: ignore[union-attr]
        "📅 <b>Auto Planner</b>\n\n"
        "Kanal mavzusini kiriting:\n"
        "<i>Misol: Gaming Shorts — Minecraft va Roblox</i>",
        reply_markup=_cancel_kb(),
    )
    await cb.answer()


@router.message(StateFilter(AutoStates.waiting_for_planner_topic))
async def on_planner_topic(msg: Message, state: FSMContext) -> None:
    topic = (msg.text or "").strip()
    if not topic:
        await msg.answer("❗ Mavzuni kiriting.", reply_markup=_cancel_kb())
        return

    await state.clear()
    wait_msg = await msg.answer("📅 <b>Reja tuzilmoqda...</b>")

    from telegram_bot.services.content_planner_service import (
        generate_daily_plan, generate_weekly_plan, get_publishing_checklist
    )
    from telegram_bot.services.automation_service import save_run

    daily, weekly, checklist = await asyncio.gather(
        asyncio.to_thread(generate_daily_plan, topic),
        asyncio.to_thread(generate_weekly_plan, topic),
        asyncio.to_thread(get_publishing_checklist),
    )

    run_id = await save_run(
        topic=topic,
        run_type="planner",
        result={"daily": daily, "weekly": weekly},
    )

    b = InlineKeyboardBuilder()
    b.button(text="📅 Haftalik",      callback_data=f"auto:plan_show:{run_id}:weekly")
    b.button(text="✅ Checklist",     callback_data=f"auto:plan_show:{run_id}:check")
    b.button(text="⭐ Saqlash",       callback_data=f"auto:fav_run:{run_id}")
    b.button(text="◀ Menyu",         callback_data="menu:auto")
    b.adjust(2)

    await wait_msg.edit_text(
        f"{daily[:3500]}",
        reply_markup=b.as_markup(),
    )


@router.callback_query(F.data.startswith("auto:plan_show:"))
async def on_plan_show(cb: CallbackQuery) -> None:
    parts  = cb.data.split(":")  # type: ignore[union-attr]
    run_id = int(parts[3])
    view   = parts[4] if len(parts) > 4 else "weekly"

    from telegram_bot.services.automation_service import get_run
    import json

    run = await get_run(run_id)
    if not run:
        await cb.answer("Topilmadi", show_alert=True)
        return

    data = json.loads(run.result_json)
    content_map = {
        "weekly": ("📅 Haftalik reja", data.get("weekly", "—")),
        "check":  ("✅ Publishing Checklist", _get_checklist()),
    }
    label, content = content_map.get(view, ("Plan", "—"))

    b = InlineKeyboardBuilder()
    b.button(text="◀ Kunlik reja", callback_data=f"auto:plan_back:{run_id}")
    await cb.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n{content[:3500]}", reply_markup=b.as_markup()
    )
    await cb.answer()


def _get_checklist() -> str:
    from telegram_bot.services.content_planner_service import get_publishing_checklist
    import asyncio as _asyncio
    return get_publishing_checklist()


@router.callback_query(F.data.startswith("auto:plan_back:"))
async def on_plan_back(cb: CallbackQuery) -> None:
    run_id = int(cb.data.split(":", 3)[3])  # type: ignore[union-attr]
    from telegram_bot.services.automation_service import get_run
    import json

    run = await get_run(run_id)
    if not run:
        cb.data = "menu:auto"  # type: ignore[union-attr]
        await on_auto_menu(cb, None)  # type: ignore[arg-type]
        return

    data = json.loads(run.result_json)
    b = InlineKeyboardBuilder()
    b.button(text="📅 Haftalik",  callback_data=f"auto:plan_show:{run_id}:weekly")
    b.button(text="✅ Checklist", callback_data=f"auto:plan_show:{run_id}:check")
    b.button(text="◀ Menyu",     callback_data="menu:auto")
    b.adjust(2)
    await cb.message.edit_text(  # type: ignore[union-attr]
        data.get("daily", "—")[:3500], reply_markup=b.as_markup()
    )
    await cb.answer()


# ─────────────────────────────────────────────────────────────────
# 📝 WORKFLOW HISTORY
# ─────────────────────────────────────────────────────────────────

_RUN_ICON = {
    "quick":    "⚡",
    "package":  "🎬",
    "project":  "📦",
    "planner":  "📅",
    "workflow": "🔗",
    "assistant":"🤖",
}


@router.callback_query(F.data == "auto:hist")
async def on_history(cb: CallbackQuery) -> None:
    from telegram_bot.services.automation_service import list_runs

    runs = await list_runs(limit=10)
    if not runs:
        text = "📝 <b>Workflow tarixi</b>\n\nHozircha hech narsa yo'q."
    else:
        lines = ["📝 <b>So'nggi 10 ta ish</b>\n"]
        for r in runs:
            icon = _RUN_ICON.get(r.run_type, "▶")
            ts   = r.created_at.strftime("%m-%d %H:%M")
            fav  = "⭐" if r.is_favorite else ""
            lines.append(f"{icon} [{ts}] {fav} <b>{r.topic[:40]}</b>\n   ({r.run_type}, {r.duration_ms}ms)")
        text = "\n".join(lines)

    b = InlineKeyboardBuilder()
    b.button(text="🔄 Yangilash", callback_data="auto:hist")
    b.button(text="◀ Orqaga",    callback_data="menu:auto")
    b.adjust(2)
    await cb.message.edit_text(text, reply_markup=b.as_markup())  # type: ignore[union-attr]
    await cb.answer()


# ─────────────────────────────────────────────────────────────────
# ⭐ FAVORITES
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "auto:fav")
async def on_favorites(cb: CallbackQuery) -> None:
    from telegram_bot.services.automation_service import list_runs

    runs = await list_runs(favorites_only=True, limit=10)
    if not runs:
        text = "⭐ <b>Sevimli ishlar</b>\n\nHozircha hech narsa yo'q.\n\nIshlarga ⭐ Saqlash tugmasini bosing."
    else:
        lines = ["⭐ <b>Sevimli ishlar</b>\n"]
        for r in runs:
            icon = _RUN_ICON.get(r.run_type, "▶")
            ts   = r.created_at.strftime("%m-%d %H:%M")
            lines.append(f"{icon} [{ts}] <b>{r.topic[:40]}</b>\n   ({r.run_type})")
        text = "\n".join(lines)

    b = InlineKeyboardBuilder()
    b.button(text="◀ Orqaga", callback_data="menu:auto")
    await cb.message.edit_text(text, reply_markup=b.as_markup())  # type: ignore[union-attr]
    await cb.answer()


@router.callback_query(F.data.startswith("auto:fav_run:"))
async def on_toggle_fav_run(cb: CallbackQuery) -> None:
    run_id = int(cb.data.split(":", 3)[3])  # type: ignore[union-attr]
    from telegram_bot.services.automation_service import toggle_favorite_run

    is_fav = await toggle_favorite_run(run_id)
    icon   = "⭐" if is_fav else "☆"
    await cb.answer(f"{icon} {'Sevimlilarga qo\'shildi' if is_fav else 'Sevimlilardan olib tashlandi'}", show_alert=True)


# ─────────────────────────────────────────────────────────────────
# 🔗 WORKFLOW ENGINE (built-in chains)
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "auto:wf")
async def on_workflow_list(cb: CallbackQuery) -> None:
    from telegram_bot.services.automation_service import BUILTIN_WORKFLOWS

    b = InlineKeyboardBuilder()
    lines = ["🔗 <b>Workflow Templatelar</b>\n"]
    for i, wf in enumerate(BUILTIN_WORKFLOWS):
        steps_str = " → ".join(wf["steps"])
        lines.append(f"<b>{wf['name']}</b>\n   {wf['description']}\n   Steps: {steps_str}")
        b.button(text=wf["name"], callback_data=f"auto:wfrun:{i}")
    b.adjust(1)
    b.row()
    b.button(text="◀ Orqaga", callback_data="menu:auto")

    await cb.message.edit_text(  # type: ignore[union-attr]
        "\n\n".join(lines), reply_markup=b.as_markup()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("auto:wfrun:"))
async def on_workflow_select(cb: CallbackQuery, state: FSMContext) -> None:
    idx = int(cb.data.split(":", 3)[3])  # type: ignore[union-attr]
    from telegram_bot.services.automation_service import BUILTIN_WORKFLOWS

    if idx >= len(BUILTIN_WORKFLOWS):
        await cb.answer("Topilmadi", show_alert=True)
        return

    wf = BUILTIN_WORKFLOWS[idx]
    await state.set_state(AutoStates.waiting_for_workflow_topic)
    await state.update_data(wf_idx=idx)
    await cb.message.edit_text(  # type: ignore[union-attr]
        f"🔗 <b>{wf['name']}</b>\n\n"
        f"Steps: {' → '.join(wf['steps'])}\n\n"
        "Mavzuni kiriting:",
        reply_markup=_cancel_kb(),
    )
    await cb.answer()


@router.message(StateFilter(AutoStates.waiting_for_workflow_topic))
async def on_workflow_topic(msg: Message, state: FSMContext) -> None:
    topic = (msg.text or "").strip()
    if not topic:
        await msg.answer("❗ Mavzuni kiriting.", reply_markup=_cancel_kb())
        return

    data  = await state.get_data()
    idx   = data.get("wf_idx", 0)
    await state.clear()

    from telegram_bot.services.automation_service import BUILTIN_WORKFLOWS, execute_workflow, save_run

    wf         = BUILTIN_WORKFLOWS[idx] if idx < len(BUILTIN_WORKFLOWS) else BUILTIN_WORKFLOWS[0]
    wait_msg   = await msg.answer(f"🔗 <b>{wf['name']}</b>\n⏳ Workflow bajarilmoqda...")
    result     = await execute_workflow(topic, wf["steps"])

    run_id = await save_run(
        topic=topic,
        run_type="workflow",
        result=result,
        duration_ms=result.get("duration_ms", 0),
    )

    # Format result
    lines = [f"✅ <b>{wf['name']} — Natija</b>\n⏱ {result.get('duration_ms',0)}ms\n"]
    step_results = result.get("steps", [])
    for s in step_results:
        icon = "✅" if s.get("status") == "ok" else "❌"
        lines.append(f"{icon} {s['key']}")

    # Show first available content
    for key in ["script", "titles", "description", "tags", "thumbnail_prompt"]:
        val = result.get(key)
        if val:
            label = key.replace("_", " ").title()
            snippet = (str(val)[:300] + "...") if len(str(val)) > 300 else str(val)
            lines.append(f"\n<b>{label}:</b>\n{snippet}")
            break

    await wait_msg.edit_text("\n".join(lines)[:3800], reply_markup=_result_kb(run_id, "auto:wf"))


# ─────────────────────────────────────────────────────────────────
# ⚙ SETTINGS
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "auto:cfg")
async def on_auto_cfg(cb: CallbackQuery) -> None:
    from telegram_bot.services.automation_service import get_settings
    from telegram_bot.services.ai_assistant_service import get_preferred_provider

    settings = await get_settings()
    provider  = get_preferred_provider()
    prov_name = provider.config.name if provider else "Sozlanmagan"

    text = (
        "⚙ <b>Automation Settings</b>\n\n"
        f"🤖 Faol AI: <b>{prov_name}</b>\n"
        f"🌍 Til: <b>{settings.language}</b>\n"
        f"🎨 Kreativlik: <b>{settings.creativity}</b>\n"
        f"📝 Uslub: <b>{settings.output_style}</b>\n"
        f"🔢 Maks natija: <b>{settings.max_results}</b>\n\n"
        "<i>API kalitlarini .env orqali sozlang.\n"
        "Settings → 🔌 Integrations → provayder holati.</i>"
    )
    b = InlineKeyboardBuilder()
    b.button(text="🔌 Integratsiyalar", callback_data="menu:integrations")
    b.button(text="🔗 Workflowlar",    callback_data="auto:wf")
    b.button(text="◀ Orqaga",          callback_data="menu:auto")
    b.adjust(2)
    await cb.message.edit_text(text, reply_markup=b.as_markup())  # type: ignore[union-attr]
    await cb.answer()


# ─────────────────────────────────────────────────────────────────
# Import asyncio at module level for gather in planner
# ─────────────────────────────────────────────────────────────────

import asyncio
