"""Asset Library Service — CRUD for saved assets, favorites, and search history.

All public functions are async (asyncio.to_thread wraps sync DB calls).
Replace store/retrieve patterns with remote storage if needed — same signatures.
"""
from __future__ import annotations

import asyncio


# ─────────────────────────────────────────────────────────────────
# Asset CRUD
# ─────────────────────────────────────────────────────────────────

def _save_asset_sync(
    title: str,
    description: str,
    category: str,
    char_name: str,
    asset_type: str,
    source_name: str,
    source_url: str,
    notes: str = "",
) -> int:
    from telegram_bot.db.material_models import Asset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        a = Asset(
            title=title[:300],
            description=description,
            category=category[:50],
            char_name=char_name[:200],
            asset_type=asset_type[:30],
            source_name=source_name[:200],
            source_url=source_url[:1000],
            notes=notes,
        )
        db.add(a)
        db.commit()
        db.refresh(a)
        return a.id


async def save_asset(
    title: str,
    description: str = "",
    category: str = "general",
    char_name: str = "",
    asset_type: str = "unknown",
    source_name: str = "",
    source_url: str = "",
    notes: str = "",
) -> int:
    return await asyncio.to_thread(
        _save_asset_sync, title, description, category,
        char_name, asset_type, source_name, source_url, notes
    )


def _list_assets_sync(
    asset_type: str | None = None,
    category: str | None = None,
    limit: int = 10,
) -> list:
    from telegram_bot.db.material_models import Asset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(Asset)
        if asset_type:
            q = q.filter_by(asset_type=asset_type)
        if category:
            q = q.filter_by(category=category)
        return q.order_by(Asset.created_at.desc()).limit(limit).all()


async def list_assets(
    asset_type: str | None = None,
    category: str | None = None,
    limit: int = 10,
) -> list:
    return await asyncio.to_thread(_list_assets_sync, asset_type, category, limit)


def _search_assets_sync(query: str, limit: int = 8) -> list:
    from telegram_bot.db.material_models import Asset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(Asset)
            .filter(
                Asset.title.ilike(f"%{query}%")
                | Asset.char_name.ilike(f"%{query}%")
                | Asset.notes.ilike(f"%{query}%")
                | Asset.category.ilike(f"%{query}%")
            )
            .order_by(Asset.created_at.desc())
            .limit(limit)
            .all()
        )


async def search_assets(query: str, limit: int = 8) -> list:
    return await asyncio.to_thread(_search_assets_sync, query, limit)


def _delete_asset_sync(asset_id: int) -> bool:
    from telegram_bot.db.material_models import Asset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        a = db.get(Asset, asset_id)
        if not a:
            return False
        db.delete(a)
        db.commit()
        return True


async def delete_asset(asset_id: int) -> bool:
    return await asyncio.to_thread(_delete_asset_sync, asset_id)


# ─────────────────────────────────────────────────────────────────
# Favorites
# ─────────────────────────────────────────────────────────────────

def _toggle_favorite_sync(asset_id: int) -> bool:
    from telegram_bot.db.material_models import Asset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        a = db.get(Asset, asset_id)
        if not a:
            return False
        a.is_favorite = not a.is_favorite
        db.commit()
        return a.is_favorite


async def toggle_favorite(asset_id: int) -> bool:
    return await asyncio.to_thread(_toggle_favorite_sync, asset_id)


def _list_favorites_sync(limit: int = 10) -> list:
    from telegram_bot.db.material_models import Asset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(Asset)
            .filter_by(is_favorite=True)
            .order_by(Asset.created_at.desc())
            .limit(limit)
            .all()
        )


async def list_favorites(limit: int = 10) -> list:
    return await asyncio.to_thread(_list_favorites_sync, limit)


# ─────────────────────────────────────────────────────────────────
# Search History
# ─────────────────────────────────────────────────────────────────

def _save_history_sync(user_id: int, query: str, asset_type: str, result_count: int = 0) -> None:
    from telegram_bot.db.material_models import SearchHistory
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        h = SearchHistory(
            user_id=user_id,
            query=query[:500],
            asset_type=asset_type[:30],
            result_count=result_count,
        )
        db.add(h)
        db.commit()


async def save_search_history(user_id: int, query: str, asset_type: str, result_count: int = 0) -> None:
    await asyncio.to_thread(_save_history_sync, user_id, query, asset_type, result_count)


def _list_history_sync(user_id: int, limit: int = 10) -> list:
    from telegram_bot.db.material_models import SearchHistory
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(SearchHistory)
            .filter_by(user_id=user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
            .all()
        )


async def list_search_history(user_id: int, limit: int = 10) -> list:
    return await asyncio.to_thread(_list_history_sync, user_id, limit)


def _clear_history_sync(user_id: int) -> int:
    from telegram_bot.db.material_models import SearchHistory
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        count = db.query(SearchHistory).filter_by(user_id=user_id).delete()
        db.commit()
        return count


async def clear_search_history(user_id: int) -> int:
    return await asyncio.to_thread(_clear_history_sync, user_id)


# ─────────────────────────────────────────────────────────────────
# Statistics
# ─────────────────────────────────────────────────────────────────

def _count_assets_sync() -> dict[str, int]:
    from telegram_bot.db.material_models import Asset
    from telegram_bot.db.session import SessionLocal
    from sqlalchemy import func

    with SessionLocal() as db:
        total = db.query(func.count(Asset.id)).scalar() or 0
        favs  = db.query(func.count(Asset.id)).filter_by(is_favorite=True).scalar() or 0
        return {"total": total, "favorites": favs}


async def count_assets() -> dict[str, int]:
    return await asyncio.to_thread(_count_assets_sync)
