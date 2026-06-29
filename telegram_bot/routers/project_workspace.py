"""Project Workspace router — STEP 8 full project management (11-item menu).

Registered BEFORE projects.router, so menu:projects is handled here.
The old projects.router still covers projview:, projdel:, proj:saved.

Callback scheme:
  menu:projects        — 11-item workspace menu (shadows old handler)
  prj:list             — enhanced project list
  prj:create           — FSM: create new project
  prj:fav              — favorited projects
  prj:notes            — global notes menu
  prj:plan             — content planner
  prj:dash             — statistics dashboard
  prj:progress         — overall progress
  prj:res              — resources browser
  prj:archive          — archived projects
  prj:settings         — project settings info
  prj:view:{id}        — enhanced project view (with modules grid)
  prj:tasks:{id}       — task list for project
  prj:notes:{id}       — notes for project
  prj:res:{id}         — resources for project
  prj:status:{id}      — status picker
  prj:set_status:{id}:{s}— set project status
  prj:fav_tog:{id}     — toggle project favorite
  prj:arch:{id}        — archive/unarchive project
  prj:del:{id}         — delete project
  prj:search           — FSM: search projects
  prjt_add:{id}        — FSM: add task
  prjt_done:{tid}      — mark task done
  prjt_del:{tid}       — delete task
  prjn_add:{id}        — FSM: add note (title)
  prjn_body:{id}       — FSM: add note (content after title)
  prjn_del:{nid}       — delete note
  prjr_add:{id}        — FSM: add resource link
  prjr_del:{rid}       — delete resource
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router(name="project_workspace")

# ── constants ────────────────────────────────────────────────────

_STATUS_ICONS: dict[str, str] = {
    "idea":       "💡",
    "planning":   "📋",
    "writing":    "✍️",
    "collecting": "📦",
    "editing":    "✂️",
    "ready":      "✅",
    "published":  "🚀",
    "archived":   "🗄",
    "cancelled":  "❌",
    "draft":      "📝",
    "active":     "🔄",
    "complete":   "✅",
}

_PRIORITY_ICONS = {"low": "🟢", "medium": "🟡", "high": "🟠", "urgent": "🔴"}

_PROJECT_STATUSES: list[tuple[str, str]] = [
    ("idea",       "💡 Idea"),
    ("planning",   "📋 Planning"),
    ("writing",    "✍️ Writing"),
    ("collecting", "📦 Collecting"),
    ("editing",    "✂️ Editing"),
    ("ready",      "✅ Ready"),
    ("published",  "🚀 Published"),
    ("cancelled",  "❌ Cancelled"),
]

_VIDEO_TYPES: list[tuple[str, str]] = [
    ("shorts",      "📱 Shorts"),
    ("long",        "🎬 Long Video"),
    ("story",       "📖 Story"),
    ("gaming",      "🎮 Gaming"),
    ("kids",        "🧸 Kids"),
    ("educational", "📚 Educational"),
    ("funny",       "😂 Funny"),
    ("other",       "🎥 Other"),
]

_CATEGORIES: list[str] = [
    "Marvel", "DC", "Anime", "Gaming", "Kids", "Disney",
    "Minecraft", "Roblox", "Story", "Educational", "Other",
]

_TASK_TEMPLATES: list[str] = [
    "Script yozish", "Thumbnail yaratish", "PNG to'plash",
    "Musiqa tanlash", "AI Prompt yaratish", "Tavsif yozish",
    "Teglar tayyorlash", "Yuklashga tayyorlash",
    "Publish qilish", "Analytics tekshirish",
]

_MODULE_ITEMS: list[tuple[str, str]] = [
    ("📝 Script",    "script"),   ("🎨 Thumbnail", "thumbnail"),
    ("🖼 Images",    "image"),    ("🎬 Animation", "animation"),
    ("🟢 Green Scr", "gs"),       ("🎥 Video",     "video"),
    ("🎵 Music",     "music"),    ("🔊 SFX",        "sfx"),
    ("🎤 Voice",     "voice"),    ("📈 SEO",        "seo"),
    ("🏷 Tags",      "tags"),     ("🔥 Hashtags",   "hashtags"),
    ("🤖 AI Prompts","prompt"),   ("💡 Ideas",      "idea"),
    ("📄 Desc",      "description"), ("📅 Plan",   "plan"),
]


class ProjStates(StatesGroup):
    waiting_for_name     = State()
    waiting_for_category = State()
    waiting_for_character = State()
    waiting_for_video_type = State()
    waiting_for_task_title = State()
    waiting_for_note_title = State()
    waiting_for_note_body  = State()
    waiting_for_res_title  = State()
    waiting_for_res_url    = State()
    waiting_for_search     = State()


# ── helpers ───────────────────────────────────────────────────────

def _proj_kb():
    b = InlineKeyboardBuilder()
    items = [
        ("➕ Yangi Loyiha",  "prj:create"),
        ("📂 Loyihalarim",   "prj:list"),
        ("⭐ Sevimlilar",    "prj:fav"),
        ("📝 Eslatmalar",    "prj:notes"),
        ("📅 Planner",       "prj:plan"),
        ("📊 Dashboard",     "prj:dash"),
        ("📈 Progress",      "prj:progress"),
        ("📦 Resurslar",     "prj:res"),
        ("🗄 Arxiv",         "prj:archive"),
        ("⚙ Sozlamalar",    "prj:settings"),
    ]
    for label, data in items:
        b.button(text=label, callback_data=data)
    b.adjust(2)
    b.button(text="🏠 Bosh menyu", callback_data="menu:main")
    b.adjust(2, 2, 2, 2, 2, 1)
    return b.as_markup()


def _back_proj_kb():
    b = InlineKeyboardBuilder()
    b.button(text="📁 Loyihalar",  callback_data="menu:projects")
    b.button(text="📂 Ro'yxat",    callback_data="prj:list")
    b.adjust(2)
    return b.as_markup()


def _proj_view_kb(proj_id: int, is_fav: bool = False, is_arch: bool = False):
    b = InlineKeyboardBuilder()
    # Modules grid
    for label, code in _MODULE_ITEMS[:8]:
        b.button(text=label, callback_data=f"prjr_add:{proj_id}")
    b.adjust(4)
    # Actions
    fav_text = "⭐ Sevimlilardan olib tashla" if is_fav else "☆ Sevimlilarga"
    arch_text = "📤 Arxivdan chiqar" if is_arch else "🗄 Arxivlash"
    b.button(text="📋 Vazifalar",    callback_data=f"prj:tasks:{proj_id}")
    b.button(text="📝 Eslatmalar",   callback_data=f"prj:notes:{proj_id}")
    b.button(text="📦 Resurslar",    callback_data=f"prj:res:{proj_id}")
    b.button(text="🔄 Status",       callback_data=f"prj:status:{proj_id}")
    b.button(text=fav_text,          callback_data=f"prj:fav_tog:{proj_id}")
    b.button(text=arch_text,         callback_data=f"prj:arch:{proj_id}")
    b.button(text="🗑 O'chirish",    callback_data=f"prj:del:{proj_id}")
    b.button(text="⬅ Ro'yxat",      callback_data="prj:list")
    b.adjust(4, 2, 2, 2, 2)
    return b.as_markup()


def _progress_bar(pct: int) -> str:
    filled = int(pct / 10)
    return "█" * filled + "░" * (10 - filled) + f" {pct}%"


# ── MAIN MENU ─────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:projects")
async def on_projects_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    from telegram_bot.db.repository import project_repo
    from telegram_bot.services.project_service import get_project_stats

    count = await project_repo.count()
    stats = await get_project_stats()
    active = stats["by_status"].get("active", 0) + stats["by_status"].get("planning", 0)

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📁 <b>Loyihalar — AI Workspace</b>\n\n"
        f"📊 Jami: <b>{count}</b> ta | 🔄 Faol: <b>{active}</b> ta\n"
        f"✅ Bajarilgan vazifalar: <b>{stats['tasks_done']}/{stats['tasks_total']}</b>\n\n"
        "Loyiha turini tanlang:",
        reply_markup=_proj_kb(),
    )
    await callback.answer()


# ── PROJECT LIST ──────────────────────────────────────────────────

@router.callback_query(F.data == "prj:list")
async def on_project_list(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import list_projects_with_meta

    items = await list_projects_with_meta(archived=False, limit=15)
    b = InlineKeyboardBuilder()
    if not items:
        b.button(text="➕ Yangi Loyiha", callback_data="prj:create")
        b.button(text="⬅ Menyuga",      callback_data="menu:projects")
        b.adjust(1)
        await callback.message.edit_text(  # type: ignore[union-attr]
            "📂 <b>Loyihalarim</b>\n\nHali loyiha yo'q.\n"
            "➕ tugmasini bosib yangi loyiha yarating.",
            reply_markup=b.as_markup(),
        )
        await callback.answer()
        return

    lines = [f"📂 <b>Loyihalarim</b> ({len(items)} ta)\n"]
    for p, m in items:
        icon = _STATUS_ICONS.get(p.status, "📁")
        prio = _PRIORITY_ICONS.get(m.priority if m else "medium", "🟡")
        pct  = m.completion_pct if m else 0
        lines.append(f"{icon}{prio} <b>{p.name[:35]}</b> — {pct}%")
        b.button(text=f"{icon} {p.name[:28]}", callback_data=f"prj:view:{p.id}")

    b.adjust(1)
    b.button(text="➕ Yangi",       callback_data="prj:create")
    b.button(text="🔍 Qidirish",    callback_data="prj:search")
    b.button(text="⬅ Menyuga",     callback_data="menu:projects")
    b.adjust(1, 2, 1)
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ── PROJECT VIEW ──────────────────────────────────────────────────

@router.callback_query(F.data.startswith("prj:view:"))
async def on_project_view(callback: CallbackQuery) -> None:
    from telegram_bot.db.repository import project_repo
    from telegram_bot.services.project_service import get_or_create_meta, list_tasks, calculate_completion

    proj_id = int(callback.data.split(":", 2)[2])
    proj = await project_repo.get(proj_id)
    if not proj:
        await callback.answer("Loyiha topilmadi", show_alert=True)
        return

    meta = await get_or_create_meta(proj_id)
    tasks = await list_tasks(proj_id)
    pct = await calculate_completion(proj_id)
    await update_meta(proj_id, completion_pct=pct)

    done  = sum(1 for t in tasks if t.status == "done")
    total = len(tasks)
    icon  = _STATUS_ICONS.get(proj.status, "📁")
    prio  = _PRIORITY_ICONS.get(meta.priority, "🟡")
    created = proj.created_at.strftime("%d.%m.%Y") if proj.created_at else "?"

    text = (
        f"{icon} <b>{proj.name}</b> {prio}\n\n"
        f"📊 Progress: <code>{_progress_bar(pct)}</code>\n\n"
        f"📂 <b>Kategoriya:</b> {proj.category_name or '—'}\n"
        f"👤 <b>Karakter:</b> {proj.character_name or '—'}\n"
        f"🎯 <b>Video turi:</b> {meta.video_type}\n"
        f"🌍 <b>Til:</b> {meta.language or '—'} | <b>Mamlakat:</b> {meta.country or '—'}\n"
        f"👥 <b>Auditoriya:</b> {meta.target_audience or '—'}\n"
        f"📅 <b>Yaratilgan:</b> {created}\n"
        f"🔖 <b>Status:</b> {proj.status}\n\n"
        f"📋 <b>Vazifalar:</b> {done}/{total} bajarildi"
    )
    if proj.notes:
        text += f"\n\n📝 <b>Eslatma:</b> {proj.notes[:200]}"

    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=_proj_view_kb(proj_id, meta.is_favorite, meta.is_archived),
    )
    await callback.answer()


async def update_meta(project_id, **kw):
    from telegram_bot.services.project_service import update_meta as _um
    await _um(project_id, **kw)


# ── CREATE PROJECT FSM ────────────────────────────────────────────

@router.callback_query(F.data == "prj:create")
async def on_create_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ProjStates.waiting_for_name)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "➕ <b>Yangi Loyiha</b> (1/3)\n\n"
        "Loyiha nomini yozing:\n"
        "Misol: <code>Spider-Man Shorts Series</code>"
    )
    await callback.answer()


@router.message(ProjStates.waiting_for_name)
async def on_create_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("❌ Bo'sh nom. Qayta yozing:")
        return
    await state.update_data(proj_name=name)
    await state.set_state(ProjStates.waiting_for_category)

    b = InlineKeyboardBuilder()
    for cat in _CATEGORIES:
        b.button(text=cat, callback_data=f"prj_cat:{cat}")
    b.adjust(3)
    await message.answer(
        f"➕ <b>{name}</b> (2/3)\n\nKategoriyani tanlang yoki yozing:",
        reply_markup=b.as_markup(),
    )


@router.callback_query(F.data.startswith("prj_cat:"), ProjStates.waiting_for_category)
async def on_create_cat_button(callback: CallbackQuery, state: FSMContext) -> None:
    cat = callback.data.split(":", 1)[1]
    await state.update_data(proj_cat=cat)
    await state.set_state(ProjStates.waiting_for_character)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"➕ Kategoriya: <b>{cat}</b> (3/3)\n\nKarakter nomini yozing:\n"
        "Misol: <code>Spider-Man</code>\n"
        "Yoki <code>-</code> kiriting (o'tkazish uchun)"
    )
    await callback.answer()


@router.message(ProjStates.waiting_for_category)
async def on_create_cat_text(message: Message, state: FSMContext) -> None:
    cat = (message.text or "").strip() or "Other"
    await state.update_data(proj_cat=cat)
    await state.set_state(ProjStates.waiting_for_character)
    await message.answer(
        f"➕ Kategoriya: <b>{cat}</b> (3/3)\n\nKarakter nomini yozing:\n"
        "Misol: <code>Spider-Man</code>"
    )


@router.message(ProjStates.waiting_for_character)
async def on_create_char(message: Message, state: FSMContext) -> None:
    from telegram_bot.db.repository import project_repo
    from telegram_bot.services.project_service import get_or_create_meta

    char = (message.text or "").strip()
    if char == "-":
        char = ""
    data = await state.get_data()
    await state.clear()

    name = data.get("proj_name", "Yangi Loyiha")
    cat  = data.get("proj_cat", "Other")

    proj = await project_repo.create(
        name=name,
        category_id=cat.lower().replace(" ", "_"),
        category_name=cat,
        character_id=char.lower().replace(" ", "_"),
        character_name=char,
    )
    await get_or_create_meta(proj.id)

    # Add default tasks
    default_tasks = [
        "Script yozish", "Thumbnail yaratish", "PNG to'plash",
        "Musiqa tanlash", "Yuklashga tayyorlash",
    ]
    from telegram_bot.services.project_service import add_task
    for t in default_tasks:
        await add_task(proj.id, t)

    b = InlineKeyboardBuilder()
    b.button(text="📋 Ko'rish",   callback_data=f"prj:view:{proj.id}")
    b.button(text="📂 Ro'yxat",   callback_data="prj:list")
    b.button(text="⬅ Menyuga",   callback_data="menu:projects")
    b.adjust(2, 1)
    await message.answer(
        f"✅ <b>{name}</b> loyihasi yaratildi!\n\n"
        f"📂 Kategoriya: {cat}\n"
        f"👤 Karakter: {char or '—'}\n"
        f"📋 5 ta standart vazifa qo'shildi.",
        reply_markup=b.as_markup(),
    )


# ── PROJECT STATUS ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("prj:status:"))
async def on_status_picker(callback: CallbackQuery) -> None:
    proj_id = int(callback.data.split(":", 2)[2])
    b = InlineKeyboardBuilder()
    for code, label in _PROJECT_STATUSES:
        b.button(text=label, callback_data=f"prj:set_status:{proj_id}:{code}")
    b.adjust(2)
    b.button(text="⬅ Orqaga", callback_data=f"prj:view:{proj_id}")
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔄 <b>Status o'zgartirish</b>\n\nYangi statusni tanlang:",
        reply_markup=b.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prj:set_status:"))
async def on_set_status(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import update_project_status

    parts = callback.data.split(":", 3)
    proj_id = int(parts[2])
    status  = parts[3]
    await update_project_status(proj_id, status)
    label = dict(_PROJECT_STATUSES).get(status, status)
    await callback.answer(f"✅ Status: {label}")
    await on_project_view(callback)


# ── FAVORITE TOGGLE ───────────────────────────────────────────────

@router.callback_query(F.data.startswith("prj:fav_tog:"))
async def on_fav_toggle(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import get_or_create_meta, update_meta as _um

    proj_id = int(callback.data.split(":", 2)[2])
    meta = await get_or_create_meta(proj_id)
    new_val = not meta.is_favorite
    await _um(proj_id, is_favorite=new_val)
    msg = "⭐ Sevimlilarga qo'shildi" if new_val else "☆ Sevimlilardan olib tashlandi"
    await callback.answer(msg)
    await on_project_view(callback)


# ── ARCHIVE ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("prj:arch:"))
async def on_archive_toggle(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import get_or_create_meta, update_meta as _um

    proj_id = int(callback.data.split(":", 2)[2])
    meta = await get_or_create_meta(proj_id)
    new_val = not meta.is_archived
    await _um(proj_id, is_archived=new_val)
    msg = "🗄 Arxivlandi" if new_val else "📤 Arxivdan chiqarildi"
    await callback.answer(msg)
    await on_project_view(callback)


# ── DELETE PROJECT ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("prj:del:"))
async def on_delete_project(callback: CallbackQuery) -> None:
    from telegram_bot.db.repository import project_repo

    proj_id = int(callback.data.split(":", 2)[2])
    proj = await project_repo.get(proj_id)
    name = proj.name if proj else f"#{proj_id}"
    await project_repo.delete(proj_id)
    await callback.answer(f"🗑 O'chirildi: {name}")
    await on_project_list(callback)


# ── TASKS ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("prj:tasks:"))
async def on_task_list(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import list_tasks

    proj_id = int(callback.data.split(":", 2)[2])
    tasks = await list_tasks(proj_id)

    _TICON = {"todo": "⬜", "in_progress": "🔄", "done": "✅", "cancelled": "❌"}
    lines = [f"📋 <b>Vazifalar</b> ({len(tasks)} ta)\n"]
    for t in tasks:
        ico = _TICON.get(t.status, "⬜")
        lines.append(f"{ico} {t.title[:42]}")

    b = InlineKeyboardBuilder()
    for t in tasks:
        if t.status != "done":
            b.button(text=f"✅ {t.title[:20]}", callback_data=f"prjt_done:{t.id}")
    b.adjust(1)
    for t in tasks:
        b.button(text=f"🗑 {t.title[:18]}", callback_data=f"prjt_del:{t.id}")
    b.adjust(1, *([1] * len(tasks)))
    b.button(text="➕ Vazifa qo'shish", callback_data=f"prjt_add:{proj_id}")
    b.button(text="⬅ Loyiha",          callback_data=f"prj:view:{proj_id}")
    b.adjust(2)

    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data.startswith("prjt_add:"))
async def on_task_add_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    proj_id = int(callback.data.split(":", 1)[1])
    await state.update_data(task_proj_id=proj_id)
    await state.set_state(ProjStates.waiting_for_task_title)

    b = InlineKeyboardBuilder()
    for tmpl in _TASK_TEMPLATES[:6]:
        b.button(text=tmpl, callback_data=f"prjt_tmpl:{proj_id}:{tmpl[:30]}")
    b.adjust(2)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "➕ <b>Yangi Vazifa</b>\n\nVazifa nomini yozing yoki tanlang:",
        reply_markup=b.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prjt_tmpl:"))
async def on_task_template(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import add_task

    parts = callback.data.split(":", 2)
    proj_id = int(parts[1])
    title   = parts[2]
    await add_task(proj_id, title)
    await callback.answer(f"✅ Vazifa qo'shildi: {title}")

    # Refresh the callback data to show task list
    callback.data = f"prj:tasks:{proj_id}"
    await on_task_list(callback)


@router.message(ProjStates.waiting_for_task_title)
async def on_task_title_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.project_service import add_task

    title = (message.text or "").strip()
    data  = await state.get_data()
    proj_id = data.get("task_proj_id", 0)
    await state.clear()
    if not title or not proj_id:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    await add_task(proj_id, title)
    b = InlineKeyboardBuilder()
    b.button(text="📋 Vazifalar",  callback_data=f"prj:tasks:{proj_id}")
    b.button(text="👁 Loyiha",     callback_data=f"prj:view:{proj_id}")
    b.adjust(2)
    await message.answer(f"✅ Vazifa qo'shildi: <b>{title}</b>", reply_markup=b.as_markup())


@router.callback_query(F.data.startswith("prjt_done:"))
async def on_task_done(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import update_task_status

    tid = int(callback.data.split(":", 1)[1])
    await update_task_status(tid, "done")
    await callback.answer("✅ Vazifa bajarildi!")
    # Reload — need project_id from context; read from DB
    from telegram_bot.db.project_models import ProjectTask
    from telegram_bot.db.session import SessionLocal
    import asyncio
    def _get_pid():
        with SessionLocal() as db:
            t = db.get(ProjectTask, tid)
            return t.project_id if t else 0
    pid = await asyncio.to_thread(_get_pid)
    callback.data = f"prj:tasks:{pid}"
    await on_task_list(callback)


@router.callback_query(F.data.startswith("prjt_del:"))
async def on_task_delete(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import delete_task
    from telegram_bot.db.project_models import ProjectTask
    from telegram_bot.db.session import SessionLocal
    import asyncio

    tid = int(callback.data.split(":", 1)[1])
    def _get_pid():
        with SessionLocal() as db:
            t = db.get(ProjectTask, tid)
            return t.project_id if t else 0
    pid = await asyncio.to_thread(_get_pid)
    await delete_task(tid)
    await callback.answer("🗑 Vazifa o'chirildi")
    callback.data = f"prj:tasks:{pid}"
    await on_task_list(callback)


# ── NOTES ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("prj:notes:"))
async def on_note_list(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import list_notes

    proj_id = int(callback.data.split(":", 2)[2])
    notes = await list_notes(proj_id, limit=10)
    lines = [f"📝 <b>Eslatmalar</b> ({len(notes)} ta)\n"]
    b = InlineKeyboardBuilder()
    for i, n in enumerate(notes, 1):
        pin = "📌 " if n.is_pinned else ""
        dt  = n.created_at.strftime("%d.%m")
        lines.append(f"{i}. {pin}<b>{n.title or 'Eslatma'}</b> <i>({dt})</i>")
        lines.append(f"   {n.content[:60]}{'…' if len(n.content) > 60 else ''}")
        b.button(text=f"🗑 {i}", callback_data=f"prjn_del:{n.id}")
    b.adjust(4)
    b.button(text="➕ Eslatma qo'shish", callback_data=f"prjn_add:{proj_id}")
    b.button(text="⬅ Loyiha",            callback_data=f"prj:view:{proj_id}")
    b.adjust(4, 2)
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data.startswith("prjn_add:"))
async def on_note_add_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    proj_id = int(callback.data.split(":", 1)[1])
    await state.update_data(note_proj_id=proj_id)
    await state.set_state(ProjStates.waiting_for_note_title)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📝 <b>Yangi Eslatma</b>\n\nEslatma sarlavhasini yozing:\n"
        "(Yoki <code>-</code> kiriting va faqat matn yozing)"
    )
    await callback.answer()


@router.message(ProjStates.waiting_for_note_title)
async def on_note_title(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    await state.update_data(note_title=title if title != "-" else "")
    await state.set_state(ProjStates.waiting_for_note_body)
    await message.answer("📝 Eslatma matnini yozing:")


@router.message(ProjStates.waiting_for_note_body)
async def on_note_body(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.project_service import add_note

    content = (message.text or "").strip()
    data    = await state.get_data()
    proj_id = data.get("note_proj_id", 0)
    title   = data.get("note_title", "")
    await state.clear()
    if not content or not proj_id:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    await add_note(proj_id, title, content)
    b = InlineKeyboardBuilder()
    b.button(text="📝 Eslatmalar", callback_data=f"prj:notes:{proj_id}")
    b.button(text="👁 Loyiha",     callback_data=f"prj:view:{proj_id}")
    b.adjust(2)
    await message.answer("✅ Eslatma saqlandi!", reply_markup=b.as_markup())


@router.callback_query(F.data.startswith("prjn_del:"))
async def on_note_delete(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import delete_note
    from telegram_bot.db.project_models import ProjectNote
    from telegram_bot.db.session import SessionLocal
    import asyncio

    nid = int(callback.data.split(":", 1)[1])
    def _get_pid():
        with SessionLocal() as db:
            n = db.get(ProjectNote, nid)
            return n.project_id if n else 0
    pid = await asyncio.to_thread(_get_pid)
    await delete_note(nid)
    await callback.answer("🗑 Eslatma o'chirildi")
    callback.data = f"prj:notes:{pid}"
    await on_note_list(callback)


# ── RESOURCES ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("prj:res:"))
async def on_resources(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import list_resources

    proj_id = int(callback.data.split(":", 2)[2])
    items = await list_resources(proj_id, limit=10)
    _RICO = {
        "script": "📝", "thumbnail": "🎨", "image": "🖼", "music": "🎵",
        "seo": "📈", "tags": "🏷", "hashtags": "🔥", "prompt": "🤖",
        "idea": "💡", "description": "📄",
    }
    lines = [f"📦 <b>Resurslar</b> ({len(items)} ta)\n"]
    b = InlineKeyboardBuilder()
    for i, r in enumerate(items, 1):
        ico = _RICO.get(r.resource_type, "📄")
        lines.append(f"{i}. {ico} <b>{r.title[:40]}</b>")
        if r.url:
            lines.append(f"   🔗 {r.url[:50]}")
        b.button(text=f"🗑 {i}", callback_data=f"prjr_del:{r.id}")
    b.adjust(4)
    b.button(text="➕ Resurs qo'shish", callback_data=f"prjr_add:{proj_id}")
    b.button(text="⬅ Loyiha",           callback_data=f"prj:view:{proj_id}")
    b.adjust(4, 2)
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data.startswith("prjr_add:"))
async def on_resource_add_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    proj_id = int(callback.data.split(":", 1)[1])
    await state.update_data(res_proj_id=proj_id)
    await state.set_state(ProjStates.waiting_for_res_title)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📦 <b>Resurs qo'shish</b>\n\nResurs nomini yozing:\n"
        "Misol: <code>Spider-Man shorts script v1</code>"
    )
    await callback.answer()


@router.message(ProjStates.waiting_for_res_title)
async def on_res_title(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    if not title:
        await message.answer("❌ Bo'sh. Nom yozing:")
        return
    await state.update_data(res_title=title)
    await state.set_state(ProjStates.waiting_for_res_url)
    await message.answer(
        "📦 URL yoki qisqa tavsif yozing:\n"
        "Misol: <code>https://...</code>\n"
        "Yoki: <code>AI Generator dan olindi</code>"
    )


@router.message(ProjStates.waiting_for_res_url)
async def on_res_url(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.project_service import add_resource

    url_or_note = (message.text or "").strip()
    data = await state.get_data()
    proj_id = data.get("res_proj_id", 0)
    title   = data.get("res_title", "Resurs")
    await state.clear()

    is_url = url_or_note.startswith("http")
    await add_resource(
        proj_id, "other", title,
        url=url_or_note if is_url else "",
        notes=url_or_note if not is_url else "",
    )
    b = InlineKeyboardBuilder()
    b.button(text="📦 Resurslar", callback_data=f"prj:res:{proj_id}")
    b.button(text="👁 Loyiha",    callback_data=f"prj:view:{proj_id}")
    b.adjust(2)
    await message.answer(f"✅ Resurs saqlandi: <b>{title}</b>", reply_markup=b.as_markup())


@router.callback_query(F.data.startswith("prjr_del:"))
async def on_resource_delete(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import delete_resource
    from telegram_bot.db.project_models import ProjectResource
    from telegram_bot.db.session import SessionLocal
    import asyncio

    rid = int(callback.data.split(":", 1)[1])
    def _get_pid():
        with SessionLocal() as db:
            r = db.get(ProjectResource, rid)
            return r.project_id if r else 0
    pid = await asyncio.to_thread(_get_pid)
    await delete_resource(rid)
    await callback.answer("🗑 Resurs o'chirildi")
    callback.data = f"prj:res:{pid}"
    await on_resources(callback)


# ── FAVORITES LIST ────────────────────────────────────────────────

@router.callback_query(F.data == "prj:fav")
async def on_fav_list(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import list_projects_with_meta

    items = await list_projects_with_meta(archived=False, favorite=True, limit=10)
    b = InlineKeyboardBuilder()
    if not items:
        b.button(text="📂 Barcha loyihalar", callback_data="prj:list")
        b.button(text="⬅ Menyuga",           callback_data="menu:projects")
        b.adjust(1)
        await callback.message.edit_text(  # type: ignore[union-attr]
            "⭐ <b>Sevimli Loyihalar</b>\n\nHali sevimli loyiha yo'q.\n"
            "Loyiha sahifasida ☆ tugmasini bosing.",
            reply_markup=b.as_markup(),
        )
        await callback.answer()
        return
    lines = [f"⭐ <b>Sevimlilar</b> ({len(items)} ta)\n"]
    for p, m in items:
        icon = _STATUS_ICONS.get(p.status, "📁")
        lines.append(f"{icon} <b>{p.name[:38]}</b>")
        b.button(text=f"{icon} {p.name[:28]}", callback_data=f"prj:view:{p.id}")
    b.adjust(1)
    b.button(text="⬅ Menyuga", callback_data="menu:projects")
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ── ARCHIVE ───────────────────────────────────────────────────────

@router.callback_query(F.data == "prj:archive")
async def on_archive_list(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import list_projects_with_meta

    items = await list_projects_with_meta(archived=True, limit=10)
    b = InlineKeyboardBuilder()
    if not items:
        b.button(text="📂 Faol loyihalar", callback_data="prj:list")
        b.button(text="⬅ Menyuga",         callback_data="menu:projects")
        b.adjust(1)
        await callback.message.edit_text(  # type: ignore[union-attr]
            "🗄 <b>Arxiv</b>\n\nHali arxivlangan loyiha yo'q.",
            reply_markup=b.as_markup(),
        )
        await callback.answer()
        return
    lines = [f"🗄 <b>Arxiv</b> ({len(items)} ta)\n"]
    for p, m in items:
        lines.append(f"🗄 <b>{p.name[:38]}</b>")
        b.button(text=p.name[:28], callback_data=f"prj:view:{p.id}")
    b.adjust(1)
    b.button(text="⬅ Menyuga", callback_data="menu:projects")
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ── DASHBOARD ─────────────────────────────────────────────────────

@router.callback_query(F.data == "prj:dash")
async def on_dashboard(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import get_project_stats

    stats = await get_project_stats()
    by_s = stats["by_status"]
    lines = [
        "📊 <b>Project Dashboard</b>\n",
        f"📁 <b>Jami loyihalar:</b> {stats['total']}",
        f"🗄 <b>Arxivlangan:</b> {stats['archived']}",
        "",
        "<b>📋 Statuslar bo'yicha:</b>",
    ]
    for code, label in _PROJECT_STATUSES:
        count = by_s.get(code, 0)
        if count:
            icon = _STATUS_ICONS.get(code, "📁")
            lines.append(f"  {icon} {label}: <b>{count}</b>")

    lines += [
        "",
        f"📋 <b>Jami vazifalar:</b> {stats['tasks_total']}",
        f"✅ <b>Bajarilgan:</b> {stats['tasks_done']}",
        f"📝 <b>Eslatmalar:</b> {stats['notes']}",
        f"📦 <b>Resurslar:</b> {stats['resources']}",
    ]
    if stats["tasks_total"]:
        pct = int(stats["tasks_done"] / stats["tasks_total"] * 100)
        lines.append(f"\n<b>Umumiy progress:</b> <code>{_progress_bar(pct)}</code>")

    b = InlineKeyboardBuilder()
    b.button(text="📂 Loyihalar", callback_data="prj:list")
    b.button(text="⬅ Menyuga",   callback_data="menu:projects")
    b.adjust(2)
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ── PROGRESS ──────────────────────────────────────────────────────

@router.callback_query(F.data == "prj:progress")
async def on_progress(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import list_projects_with_meta, list_tasks

    items = await list_projects_with_meta(archived=False, limit=10)
    lines = ["📈 <b>Progress Tracker</b>\n"]
    for p, m in items:
        pct = m.completion_pct if m else 0
        lines.append(f"<b>{p.name[:30]}</b>")
        lines.append(f"<code>{_progress_bar(pct)}</code>\n")

    b = InlineKeyboardBuilder()
    b.button(text="📊 Dashboard",   callback_data="prj:dash")
    b.button(text="📂 Loyihalar",   callback_data="prj:list")
    b.button(text="⬅ Menyuga",     callback_data="menu:projects")
    b.adjust(2, 1)
    await callback.message.edit_text(
        "\n".join(lines) if items else "📈 <b>Progress</b>\n\nHali loyiha yo'q.",
        reply_markup=b.as_markup(),
    )
    await callback.answer()


# ── GLOBAL NOTES ──────────────────────────────────────────────────

@router.callback_query(F.data == "prj:notes")
async def on_global_notes(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import list_projects_with_meta

    items = await list_projects_with_meta(archived=False, limit=10)
    b = InlineKeyboardBuilder()
    lines = ["📝 <b>Eslatmalar</b>\n\nLoyihani tanlang:"]
    for p, _ in items:
        b.button(text=f"📝 {p.name[:28]}", callback_data=f"prj:notes:{p.id}")
    b.adjust(1)
    b.button(text="⬅ Menyuga", callback_data="menu:projects")
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ── GLOBAL RESOURCES ──────────────────────────────────────────────

@router.callback_query(F.data == "prj:res")
async def on_global_resources(callback: CallbackQuery) -> None:
    from telegram_bot.services.project_service import list_projects_with_meta

    items = await list_projects_with_meta(archived=False, limit=10)
    b = InlineKeyboardBuilder()
    lines = ["📦 <b>Resurslar</b>\n\nLoyihani tanlang:"]
    for p, _ in items:
        b.button(text=f"📦 {p.name[:28]}", callback_data=f"prj:res:{p.id}")
    b.adjust(1)
    b.button(text="⬅ Menyuga", callback_data="menu:projects")
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ── PLANNER ───────────────────────────────────────────────────────

@router.callback_query(F.data == "prj:plan")
async def on_planner(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_planner_service import generate_daily_plan

    b = InlineKeyboardBuilder()
    b.button(text="📅 Kunlik reja",   callback_data="prj:plan:daily")
    b.button(text="📆 Haftalik reja", callback_data="prj:plan:weekly")
    b.button(text="🗓 Oylik reja",    callback_data="prj:plan:monthly")
    b.button(text="✅ Chek-list",     callback_data="prj:plan:checklist")
    b.button(text="⬅ Menyuga",       callback_data="menu:projects")
    b.adjust(2, 2, 1)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📅 <b>Content Planner</b>\n\nReja turini tanlang:",
        reply_markup=b.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prj:plan:"))
async def on_plan_type(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_planner_service import (
        generate_daily_plan, generate_weekly_plan, generate_monthly_plan, get_publishing_checklist,
    )

    plan_type = callback.data.split(":", 2)[2]
    _fns = {
        "daily":     lambda: generate_daily_plan("YouTube kanal"),
        "weekly":    lambda: generate_weekly_plan("YouTube kanal"),
        "monthly":   lambda: generate_monthly_plan("YouTube kanal"),
        "checklist": lambda: get_publishing_checklist(),
    }
    text = _fns.get(plan_type, lambda: "")()
    b = InlineKeyboardBuilder()
    b.button(text="⬅ Planner", callback_data="prj:plan")
    b.button(text="⬅ Menyuga", callback_data="menu:projects")
    b.adjust(2)
    await callback.message.edit_text(text, reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ── SETTINGS ──────────────────────────────────────────────────────

@router.callback_query(F.data == "prj:settings")
async def on_settings(callback: CallbackQuery) -> None:
    b = InlineKeyboardBuilder()
    b.button(text="📂 Loyihalar",  callback_data="prj:list")
    b.button(text="📊 Dashboard",  callback_data="prj:dash")
    b.button(text="⬅ Menyuga",    callback_data="menu:projects")
    b.adjust(2, 1)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "⚙ <b>Loyiha Sozlamalari</b>\n\n"
        "Default sozlamalar:\n"
        "🌍 Til: O'zbek / English\n"
        "🎯 Tur: Shorts (60s)\n"
        "👥 Auditoriya: 6-12 yosh\n"
        "🔥 Prioritet: Medium\n\n"
        "<i>Har bir loyiha uchun sozlamalar alohida o'zgartiriladi.</i>",
        reply_markup=b.as_markup(),
    )
    await callback.answer()


# ── SEARCH ────────────────────────────────────────────────────────

@router.callback_query(F.data == "prj:search")
async def on_search_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ProjStates.waiting_for_search)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔍 <b>Loyiha Qidirish</b>\n\nNom, karakter yoki kategoriyani yozing:"
    )
    await callback.answer()


@router.message(ProjStates.waiting_for_search)
async def on_search_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.project_service import search_projects

    query = (message.text or "").strip()
    await state.clear()
    if not query:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    results = await search_projects(query, limit=8)
    b = InlineKeyboardBuilder()
    if not results:
        b.button(text="📂 Barcha loyihalar", callback_data="prj:list")
        await message.answer(f"🔍 <b>'{query}'</b> — topilmadi.", reply_markup=b.as_markup())
        return
    lines = [f"🔍 <b>'{query}'</b> — {len(results)} ta\n"]
    for p in results:
        icon = _STATUS_ICONS.get(p.status, "📁")
        lines.append(f"{icon} <b>{p.name[:38]}</b>")
        b.button(text=f"{icon} {p.name[:28]}", callback_data=f"prj:view:{p.id}")
    b.adjust(1)
    b.button(text="📂 Barcha", callback_data="prj:list")
    await message.answer("\n".join(lines), reply_markup=b.as_markup())
