"""Projects router — 📁 list and manage projects."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.db.repository import project_repo
from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard

router = Router(name="projects")

_ITEMS: list[tuple[str, str]] = [
    ("📁 My Projects",     "proj:my"),
    ("➕ New Project",     "proj:new"),
    ("🗂 Saved Materials", "proj:saved"),
]

_STATUS_ICONS = {"draft": "📝", "active": "🔄", "complete": "✅"}


def _projects_menu_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:projects")
    return builder.as_markup()


def _project_list_keyboard(projects):
    builder = InlineKeyboardBuilder()
    for proj in projects:
        icon = _STATUS_ICONS.get(proj.status, "📁")
        builder.button(
            text=f"{icon} {proj.name[:30]}",
            callback_data=f"projview:{proj.id}",
        )
    builder.adjust(1)
    add_nav_row(builder, current="proj:my")
    return builder.as_markup()


def _project_detail_keyboard(project_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🗑 Delete",     callback_data=f"projdel:{project_id}"),
        InlineKeyboardButton(text="📋 Back to list",callback_data="proj:my"),
    )
    add_nav_row(builder, current=f"projview:{project_id}", parent="proj:my")
    return builder.as_markup()


@router.callback_query(F.data == "menu:projects")
async def on_projects_menu(callback: CallbackQuery) -> None:
    count = await project_repo.count()
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📁 <b>Projects</b>\n\n"
        f"You have <b>{count}</b> project(s).\n\n"
        "Create a project from any character page,\n"
        "or browse your existing ones:",
        reply_markup=_projects_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "proj:my")
async def on_my_projects(callback: CallbackQuery) -> None:
    projects = await project_repo.list_all()
    if not projects:
        await callback.message.edit_text(  # type: ignore[union-attr]
            "📁 <b>My Projects</b>\n\n"
            "<i>No projects yet.\n\n"
            "Open any character page and tap <b>📁 New Project</b> to create one.</i>",
            reply_markup=get_nav_keyboard(current="proj:my", parent="menu:projects"),
        )
    else:
        builder = InlineKeyboardBuilder()
        for proj in projects:
            icon = _STATUS_ICONS.get(proj.status, "📁")
            builder.button(
                text=f"{icon} {proj.name[:32]}",
                callback_data=f"projview:{proj.id}",
            )
        builder.adjust(1)
        add_nav_row(builder, current="proj:my", parent="menu:projects")
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"📁 <b>My Projects</b>\n{len(projects)} project(s):",
            reply_markup=builder.as_markup(),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("projview:"))
async def on_project_view(callback: CallbackQuery) -> None:
    proj_id = int(callback.data.split(":")[1])
    proj = await project_repo.get(proj_id)
    if not proj:
        await callback.answer("Project not found", show_alert=True)
        return

    created = proj.created_at.strftime("%Y-%m-%d") if proj.created_at else "?"
    icon = _STATUS_ICONS.get(proj.status, "📁")
    text = (
        f"{icon} <b>{proj.name}</b>\n\n"
        f"📂 <b>Category:</b> {proj.category_name}\n"
        f"👤 <b>Character:</b> {proj.character_name}\n"
        f"📅 <b>Created:</b> {created}\n"
        f"🔖 <b>Status:</b> {proj.status}\n"
    )
    if proj.notes:
        text += f"\n📝 <b>Notes:</b>\n{proj.notes}"

    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=_project_detail_keyboard(proj_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("projdel:"))
async def on_project_delete(callback: CallbackQuery) -> None:
    proj_id = int(callback.data.split(":")[1])
    proj = await project_repo.get(proj_id)
    name = proj.name if proj else f"#{proj_id}"
    deleted = await project_repo.delete(proj_id)
    if deleted:
        await callback.answer(f"🗑 Deleted: {name}")
    else:
        await callback.answer("Not found", show_alert=True)
        return

    # Refresh project list
    projects = await project_repo.list_all()
    if not projects:
        await callback.message.edit_text(  # type: ignore[union-attr]
            "📁 <b>My Projects</b>\n\n<i>No projects yet.</i>",
            reply_markup=get_nav_keyboard(current="proj:my", parent="menu:projects"),
        )
    else:
        builder = InlineKeyboardBuilder()
        for p in projects:
            icon = _STATUS_ICONS.get(p.status, "📁")
            builder.button(text=f"{icon} {p.name[:32]}", callback_data=f"projview:{p.id}")
        builder.adjust(1)
        add_nav_row(builder, current="proj:my", parent="menu:projects")
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"📁 <b>My Projects</b>\n{len(projects)} project(s):",
            reply_markup=builder.as_markup(),
        )


@router.callback_query(F.data == "proj:new")
async def on_new_project(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "➕ <b>New Project</b>\n\n"
        "To create a project, open any character page and tap\n"
        "<b>📁 New Project</b>.\n\n"
        "The project will be automatically named after the character.",
        reply_markup=get_nav_keyboard(current="proj:new", parent="menu:projects"),
    )
    await callback.answer()


@router.callback_query(F.data == "proj:saved")
async def on_saved_materials(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🗂 <b>Saved Materials</b>\n\n⏳ Coming in the next step.",
        reply_markup=get_nav_keyboard(current="proj:saved", parent="menu:projects"),
    )
    await callback.answer()
