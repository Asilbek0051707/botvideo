"""Project Management Service — full CRUD for tasks, notes, resources, metadata.

Uses the existing project_repo (repository.py) for Project rows.
All new functionality targets the new prj_* tables.
All public functions are async.
"""
from __future__ import annotations

import asyncio
import json


# ─────────────────────────────────────────────────────────────────
# PROJECT META
# ─────────────────────────────────────────────────────────────────

def _get_or_create_meta_sync(project_id: int):
    from telegram_bot.db.project_models import ProjectMeta
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        m = db.query(ProjectMeta).filter_by(project_id=project_id).first()
        if not m:
            m = ProjectMeta(project_id=project_id)
            db.add(m)
            db.commit()
            db.refresh(m)
        return m


async def get_or_create_meta(project_id: int):
    return await asyncio.to_thread(_get_or_create_meta_sync, project_id)


def _update_meta_sync(project_id: int, **kwargs) -> bool:
    from telegram_bot.db.project_models import ProjectMeta
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        m = db.query(ProjectMeta).filter_by(project_id=project_id).first()
        if not m:
            m = ProjectMeta(project_id=project_id)
            db.add(m)
        for k, v in kwargs.items():
            if hasattr(m, k):
                setattr(m, k, v)
        db.commit()
        return True


async def update_meta(project_id: int, **kwargs) -> bool:
    return await asyncio.to_thread(_update_meta_sync, project_id, **kwargs)


def _list_projects_with_meta_sync(
    archived: bool = False,
    favorite: bool = False,
    limit: int = 20,
):
    from telegram_bot.db.models import Project
    from telegram_bot.db.project_models import ProjectMeta
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        projects = (
            db.query(Project)
            .order_by(Project.created_at.desc())
            .limit(200)
            .all()
        )
        result = []
        for p in projects:
            m = db.query(ProjectMeta).filter_by(project_id=p.id).first()
            is_arch = m.is_archived if m else False
            is_fav  = m.is_favorite if m else False
            if archived and not is_arch:
                continue
            if not archived and is_arch:
                continue
            if favorite and not is_fav:
                continue
            result.append((p, m))
            if len(result) >= limit:
                break
        return result


async def list_projects_with_meta(
    archived: bool = False,
    favorite: bool = False,
    limit: int = 20,
) -> list:
    return await asyncio.to_thread(_list_projects_with_meta_sync, archived, favorite, limit)


def _search_projects_sync(query: str, limit: int = 10):
    from telegram_bot.db.models import Project
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(Project)
            .filter(
                Project.name.ilike(f"%{query}%")
                | Project.character_name.ilike(f"%{query}%")
                | Project.category_name.ilike(f"%{query}%")
                | Project.notes.ilike(f"%{query}%")
            )
            .order_by(Project.created_at.desc())
            .limit(limit)
            .all()
        )


async def search_projects(query: str, limit: int = 10):
    return await asyncio.to_thread(_search_projects_sync, query, limit)


def _update_project_status_sync(project_id: int, status: str) -> bool:
    from telegram_bot.db.models import Project
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        p = db.get(Project, project_id)
        if not p:
            return False
        p.status = status
        db.commit()
        return True


async def update_project_status(project_id: int, status: str) -> bool:
    return await asyncio.to_thread(_update_project_status_sync, project_id, status)


def _get_project_stats_sync() -> dict:
    from telegram_bot.db.models import Project
    from telegram_bot.db.project_models import ProjectMeta, ProjectTask, ProjectNote, ProjectResource
    from telegram_bot.db.session import SessionLocal
    from sqlalchemy import func

    with SessionLocal() as db:
        total    = db.query(func.count(Project.id)).scalar() or 0
        by_status = {}
        for row in db.query(Project.status, func.count(Project.id)).group_by(Project.status).all():
            by_status[row[0]] = row[1]
        archived = db.query(func.count(ProjectMeta.id)).filter_by(is_archived=True).scalar() or 0
        tasks    = db.query(func.count(ProjectTask.id)).scalar() or 0
        done_t   = db.query(func.count(ProjectTask.id)).filter_by(status="done").scalar() or 0
        notes    = db.query(func.count(ProjectNote.id)).scalar() or 0
        resources= db.query(func.count(ProjectResource.id)).scalar() or 0
        return {
            "total": total,
            "by_status": by_status,
            "archived": archived,
            "tasks_total": tasks,
            "tasks_done": done_t,
            "notes": notes,
            "resources": resources,
        }


async def get_project_stats() -> dict:
    return await asyncio.to_thread(_get_project_stats_sync)


# ─────────────────────────────────────────────────────────────────
# TASKS
# ─────────────────────────────────────────────────────────────────

def _add_task_sync(project_id: int, title: str, priority: str = "medium") -> int:
    from telegram_bot.db.project_models import ProjectTask
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        t = ProjectTask(project_id=project_id, title=title[:300], priority=priority)
        db.add(t)
        db.commit()
        db.refresh(t)
        return t.id


async def add_task(project_id: int, title: str, priority: str = "medium") -> int:
    return await asyncio.to_thread(_add_task_sync, project_id, title, priority)


def _list_tasks_sync(project_id: int) -> list:
    from telegram_bot.db.project_models import ProjectTask
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(ProjectTask)
            .filter_by(project_id=project_id)
            .order_by(ProjectTask.created_at.asc())
            .all()
        )


async def list_tasks(project_id: int) -> list:
    return await asyncio.to_thread(_list_tasks_sync, project_id)


def _update_task_status_sync(task_id: int, status: str) -> bool:
    from telegram_bot.db.project_models import ProjectTask
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        t = db.get(ProjectTask, task_id)
        if not t:
            return False
        t.status = status
        db.commit()
        return True


async def update_task_status(task_id: int, status: str) -> bool:
    return await asyncio.to_thread(_update_task_status_sync, task_id, status)


def _delete_task_sync(task_id: int) -> bool:
    from telegram_bot.db.project_models import ProjectTask
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        t = db.get(ProjectTask, task_id)
        if not t:
            return False
        db.delete(t)
        db.commit()
        return True


async def delete_task(task_id: int) -> bool:
    return await asyncio.to_thread(_delete_task_sync, task_id)


def _calculate_completion_sync(project_id: int) -> int:
    from telegram_bot.db.project_models import ProjectTask
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        total = db.query(ProjectTask).filter_by(project_id=project_id).count()
        done  = db.query(ProjectTask).filter_by(project_id=project_id, status="done").count()
        if total == 0:
            return 0
        return int(done / total * 100)


async def calculate_completion(project_id: int) -> int:
    return await asyncio.to_thread(_calculate_completion_sync, project_id)


# ─────────────────────────────────────────────────────────────────
# NOTES
# ─────────────────────────────────────────────────────────────────

def _add_note_sync(project_id: int, title: str, content: str, pinned: bool = False) -> int:
    from telegram_bot.db.project_models import ProjectNote
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        n = ProjectNote(
            project_id=project_id,
            title=title[:200],
            content=content,
            is_pinned=pinned,
        )
        db.add(n)
        db.commit()
        db.refresh(n)
        return n.id


async def add_note(project_id: int, title: str, content: str, pinned: bool = False) -> int:
    return await asyncio.to_thread(_add_note_sync, project_id, title, content, pinned)


def _list_notes_sync(project_id: int, limit: int = 10) -> list:
    from telegram_bot.db.project_models import ProjectNote
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(ProjectNote)
            .filter_by(project_id=project_id)
            .order_by(ProjectNote.is_pinned.desc(), ProjectNote.created_at.desc())
            .limit(limit)
            .all()
        )


async def list_notes(project_id: int, limit: int = 10) -> list:
    return await asyncio.to_thread(_list_notes_sync, project_id, limit)


def _delete_note_sync(note_id: int) -> bool:
    from telegram_bot.db.project_models import ProjectNote
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        n = db.get(ProjectNote, note_id)
        if not n:
            return False
        db.delete(n)
        db.commit()
        return True


async def delete_note(note_id: int) -> bool:
    return await asyncio.to_thread(_delete_note_sync, note_id)


# ─────────────────────────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────────────────────────

def _add_resource_sync(
    project_id: int,
    resource_type: str,
    title: str,
    url: str = "",
    content: str = "",
    notes: str = "",
) -> int:
    from telegram_bot.db.project_models import ProjectResource
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        r = ProjectResource(
            project_id=project_id,
            resource_type=resource_type[:30],
            title=title[:300],
            url=url[:1000],
            content=content,
            notes=notes,
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        return r.id


async def add_resource(
    project_id: int,
    resource_type: str,
    title: str,
    url: str = "",
    content: str = "",
    notes: str = "",
) -> int:
    return await asyncio.to_thread(
        _add_resource_sync, project_id, resource_type, title, url, content, notes
    )


def _list_resources_sync(project_id: int, resource_type: str | None = None, limit: int = 20) -> list:
    from telegram_bot.db.project_models import ProjectResource
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(ProjectResource).filter_by(project_id=project_id)
        if resource_type:
            q = q.filter_by(resource_type=resource_type)
        return q.order_by(ProjectResource.created_at.desc()).limit(limit).all()


async def list_resources(project_id: int, resource_type: str | None = None, limit: int = 20) -> list:
    return await asyncio.to_thread(_list_resources_sync, project_id, resource_type, limit)


def _delete_resource_sync(resource_id: int) -> bool:
    from telegram_bot.db.project_models import ProjectResource
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        r = db.get(ProjectResource, resource_id)
        if not r:
            return False
        db.delete(r)
        db.commit()
        return True


async def delete_resource(resource_id: int) -> bool:
    return await asyncio.to_thread(_delete_resource_sync, resource_id)
