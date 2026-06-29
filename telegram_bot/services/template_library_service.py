"""Template Library Service — save, list, search, and delete generated content.

Handles persistence for all AI Generator outputs.
All functions are async (use asyncio.to_thread for sync DB operations).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────
# GeneratedContent CRUD
# ─────────────────────────────────────────────────────────────────

def _save_generated_sync(
    gen_type: str, sub_type: str, topic: str, content: str, project_id: int | None = None
) -> int:
    from telegram_bot.db.ai_generator_models import GeneratedContent
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        item = GeneratedContent(
            gen_type=gen_type[:30],
            sub_type=sub_type[:50],
            topic=topic[:300],
            content=content,
            is_saved=True,
            project_id=project_id,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item.id


async def save_generated(
    gen_type: str, sub_type: str, topic: str, content: str, project_id: int | None = None
) -> int:
    return await asyncio.to_thread(_save_generated_sync, gen_type, sub_type, topic, content, project_id)


def _list_generated_sync(gen_type: str | None = None, limit: int = 10) -> list:
    from telegram_bot.db.ai_generator_models import GeneratedContent
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(GeneratedContent).filter_by(is_saved=True)
        if gen_type:
            q = q.filter_by(gen_type=gen_type)
        return q.order_by(GeneratedContent.created_at.desc()).limit(limit).all()


async def list_generated(gen_type: str | None = None, limit: int = 10) -> list:
    return await asyncio.to_thread(_list_generated_sync, gen_type, limit)


def _search_generated_sync(query: str, limit: int = 8) -> list:
    from telegram_bot.db.ai_generator_models import GeneratedContent
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(GeneratedContent)
            .filter(GeneratedContent.is_saved == True)  # noqa: E712
            .filter(GeneratedContent.topic.ilike(f"%{query}%"))
            .order_by(GeneratedContent.created_at.desc())
            .limit(limit)
            .all()
        )


async def search_generated(query: str, limit: int = 8) -> list:
    return await asyncio.to_thread(_search_generated_sync, query, limit)


def _delete_generated_sync(item_id: int) -> bool:
    from telegram_bot.db.ai_generator_models import GeneratedContent
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        item = db.get(GeneratedContent, item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True


async def delete_generated(item_id: int) -> bool:
    return await asyncio.to_thread(_delete_generated_sync, item_id)


# ─────────────────────────────────────────────────────────────────
# AITemplate CRUD
# ─────────────────────────────────────────────────────────────────

def _save_template_sync(
    template_type: str, name: str, content: str, category: str = "general"
) -> int:
    from telegram_bot.db.ai_generator_models import AITemplate
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        tmpl = AITemplate(
            template_type=template_type[:30],
            name=name[:200],
            category=category[:50],
            content=content,
        )
        db.add(tmpl)
        db.commit()
        db.refresh(tmpl)
        return tmpl.id


async def save_template(
    template_type: str, name: str, content: str, category: str = "general"
) -> int:
    return await asyncio.to_thread(_save_template_sync, template_type, name, content, category)


def _list_templates_sync(template_type: str | None = None, limit: int = 10) -> list:
    from telegram_bot.db.ai_generator_models import AITemplate
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(AITemplate).filter_by(is_active=True)
        if template_type:
            q = q.filter_by(template_type=template_type)
        return q.order_by(AITemplate.usage_count.desc()).limit(limit).all()


async def list_templates(template_type: str | None = None, limit: int = 10) -> list:
    return await asyncio.to_thread(_list_templates_sync, template_type, limit)


def _search_templates_sync(query: str, limit: int = 8) -> list:
    from telegram_bot.db.ai_generator_models import AITemplate
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(AITemplate)
            .filter(AITemplate.is_active == True)  # noqa: E712
            .filter(AITemplate.name.ilike(f"%{query}%"))
            .order_by(AITemplate.usage_count.desc())
            .limit(limit)
            .all()
        )


async def search_templates(query: str, limit: int = 8) -> list:
    return await asyncio.to_thread(_search_templates_sync, query, limit)


def _delete_template_sync(tmpl_id: int) -> bool:
    from telegram_bot.db.ai_generator_models import AITemplate
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        tmpl = db.get(AITemplate, tmpl_id)
        if not tmpl:
            return False
        tmpl.is_active = False   # soft delete
        db.commit()
        return True


async def delete_template(tmpl_id: int) -> bool:
    return await asyncio.to_thread(_delete_template_sync, tmpl_id)


def _count_saved_sync() -> dict[str, int]:
    from telegram_bot.db.ai_generator_models import GeneratedContent, AITemplate
    from telegram_bot.db.session import SessionLocal
    from sqlalchemy import func

    with SessionLocal() as db:
        gen_count = db.query(func.count(GeneratedContent.id)).filter_by(is_saved=True).scalar() or 0
        tmpl_count = db.query(func.count(AITemplate.id)).filter_by(is_active=True).scalar() or 0
        return {"generated": gen_count, "templates": tmpl_count}


async def count_saved() -> dict[str, int]:
    return await asyncio.to_thread(_count_saved_sync)
