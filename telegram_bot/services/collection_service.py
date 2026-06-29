"""Collection Service — manage named asset collections.

A collection is a labeled set of Asset references
(e.g. 'Marvel Pack', 'Minecraft Resources', 'Thumbnail Inspiration').
"""
from __future__ import annotations

import asyncio


# ─────────────────────────────────────────────────────────────────
# Collection CRUD
# ─────────────────────────────────────────────────────────────────

# Built-in starter collections shown when the DB is empty
PRESET_COLLECTIONS: list[tuple[str, str]] = [
    ("Marvel Pack",            "marvel"),
    ("Disney Pack",            "disney"),
    ("Minecraft Pack",         "minecraft"),
    ("Tiles Hop Pack",         "tiles_hop"),
    ("Story Pack",             "story"),
    ("Thumbnail Inspiration",  "thumbnail"),
    ("AI Prompt Collection",   "ai_prompt"),
    ("Gaming Resources",       "gaming"),
]


def _create_collection_sync(name: str, description: str = "", category: str = "general") -> int:
    from telegram_bot.db.material_models import AssetCollection
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        c = AssetCollection(name=name[:200], description=description, category=category[:50])
        db.add(c)
        db.commit()
        db.refresh(c)
        return c.id


async def create_collection(name: str, description: str = "", category: str = "general") -> int:
    return await asyncio.to_thread(_create_collection_sync, name, description, category)


def _list_collections_sync(limit: int = 10) -> list:
    from telegram_bot.db.material_models import AssetCollection
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(AssetCollection)
            .order_by(AssetCollection.created_at.desc())
            .limit(limit)
            .all()
        )


async def list_collections(limit: int = 10) -> list:
    return await asyncio.to_thread(_list_collections_sync, limit)


def _delete_collection_sync(collection_id: int) -> bool:
    from telegram_bot.db.material_models import AssetCollection, CollectionAsset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        db.query(CollectionAsset).filter_by(collection_id=collection_id).delete()
        c = db.get(AssetCollection, collection_id)
        if not c:
            return False
        db.delete(c)
        db.commit()
        return True


async def delete_collection(collection_id: int) -> bool:
    return await asyncio.to_thread(_delete_collection_sync, collection_id)


# ─────────────────────────────────────────────────────────────────
# Collection ↔ Asset membership
# ─────────────────────────────────────────────────────────────────

def _add_to_collection_sync(collection_id: int, asset_id: int) -> bool:
    from telegram_bot.db.material_models import CollectionAsset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        existing = (
            db.query(CollectionAsset)
            .filter_by(collection_id=collection_id, asset_id=asset_id)
            .first()
        )
        if existing:
            return False
        db.add(CollectionAsset(collection_id=collection_id, asset_id=asset_id))
        db.commit()
        return True


async def add_to_collection(collection_id: int, asset_id: int) -> bool:
    return await asyncio.to_thread(_add_to_collection_sync, collection_id, asset_id)


def _remove_from_collection_sync(collection_id: int, asset_id: int) -> bool:
    from telegram_bot.db.material_models import CollectionAsset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        deleted = (
            db.query(CollectionAsset)
            .filter_by(collection_id=collection_id, asset_id=asset_id)
            .delete()
        )
        db.commit()
        return bool(deleted)


async def remove_from_collection(collection_id: int, asset_id: int) -> bool:
    return await asyncio.to_thread(_remove_from_collection_sync, collection_id, asset_id)


def _list_collection_assets_sync(collection_id: int, limit: int = 20) -> list:
    from telegram_bot.db.material_models import Asset, CollectionAsset
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        ca_list = (
            db.query(CollectionAsset)
            .filter_by(collection_id=collection_id)
            .limit(limit)
            .all()
        )
        result = []
        for ca in ca_list:
            a = db.get(Asset, ca.asset_id)
            if a:
                result.append(a)
        return result


async def list_collection_assets(collection_id: int, limit: int = 20) -> list:
    return await asyncio.to_thread(_list_collection_assets_sync, collection_id, limit)


def _count_collection_assets_sync(collection_id: int) -> int:
    from telegram_bot.db.material_models import CollectionAsset
    from telegram_bot.db.session import SessionLocal
    from sqlalchemy import func

    with SessionLocal() as db:
        return (
            db.query(func.count(CollectionAsset.id))
            .filter_by(collection_id=collection_id)
            .scalar()
            or 0
        )


async def count_collection_assets(collection_id: int) -> int:
    return await asyncio.to_thread(_count_collection_assets_sync, collection_id)
