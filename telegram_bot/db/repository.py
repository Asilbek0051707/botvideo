"""Repository classes — thin async wrappers over sync SQLAlchemy."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from telegram_bot.db.models import Favourite, Project
from telegram_bot.db.session import SessionLocal


# ──────────────────────────── helpers ────────────────────────────


def _run(fn, *args, **kwargs):
    """Run a sync function in a thread pool and return awaitable."""
    return asyncio.to_thread(fn, *args, **kwargs)


# ──────────────────────────── ProjectRepo ────────────────────────


class ProjectRepo:
    """CRUD for Project rows."""

    # ── write ──

    @staticmethod
    def _create(
        name: str,
        category_id: str,
        category_name: str,
        character_id: str,
        character_name: str,
        notes: str = "",
    ) -> Project:
        with SessionLocal() as db:
            proj = Project(
                name=name,
                category_id=category_id,
                category_name=category_name,
                character_id=character_id,
                character_name=character_name,
                notes=notes,
            )
            db.add(proj)
            db.commit()
            db.refresh(proj)
            return proj

    async def create(self, **kwargs) -> Project:
        return await _run(self._create, **kwargs)

    @staticmethod
    def _update_notes(project_id: int, notes: str) -> bool:
        with SessionLocal() as db:
            proj = db.get(Project, project_id)
            if not proj:
                return False
            proj.notes = notes
            db.commit()
            return True

    async def update_notes(self, project_id: int, notes: str) -> bool:
        return await _run(self._update_notes, project_id, notes)

    @staticmethod
    def _delete(project_id: int) -> bool:
        with SessionLocal() as db:
            proj = db.get(Project, project_id)
            if not proj:
                return False
            db.delete(proj)
            db.commit()
            return True

    async def delete(self, project_id: int) -> bool:
        return await _run(self._delete, project_id)

    # ── read ──

    @staticmethod
    def _list_all() -> list[Project]:
        with SessionLocal() as db:
            return db.query(Project).order_by(Project.created_at.desc()).all()

    async def list_all(self) -> list[Project]:
        return await _run(self._list_all)

    @staticmethod
    def _get(project_id: int) -> Project | None:
        with SessionLocal() as db:
            return db.get(Project, project_id)

    async def get(self, project_id: int) -> Project | None:
        return await _run(self._get, project_id)

    @staticmethod
    def _count() -> int:
        with SessionLocal() as db:
            return db.query(Project).count()

    async def count(self) -> int:
        return await _run(self._count)


# ──────────────────────────── FavouriteRepo ──────────────────────


class FavouriteRepo:
    """CRUD for Favourite rows."""

    @staticmethod
    def _add(
        item_type: str,
        item_id: str,
        item_name: str,
        category_id: str | None = None,
        meta: dict | None = None,
    ) -> Favourite:
        with SessionLocal() as db:
            existing = (
                db.query(Favourite)
                .filter_by(item_type=item_type, item_id=item_id)
                .first()
            )
            if existing:
                return existing
            fav = Favourite(
                item_type=item_type,
                item_id=item_id,
                item_name=item_name,
                category_id=category_id,
                meta=json.dumps(meta or {}),
            )
            db.add(fav)
            db.commit()
            db.refresh(fav)
            return fav

    async def add(self, **kwargs) -> Favourite:
        return await _run(self._add, **kwargs)

    @staticmethod
    def _remove(item_type: str, item_id: str) -> bool:
        with SessionLocal() as db:
            fav = (
                db.query(Favourite)
                .filter_by(item_type=item_type, item_id=item_id)
                .first()
            )
            if not fav:
                return False
            db.delete(fav)
            db.commit()
            return True

    async def remove(self, item_type: str, item_id: str) -> bool:
        return await _run(self._remove, item_type, item_id)

    @staticmethod
    def _is_saved(item_type: str, item_id: str) -> bool:
        with SessionLocal() as db:
            return (
                db.query(Favourite)
                .filter_by(item_type=item_type, item_id=item_id)
                .first()
            ) is not None

    async def is_saved(self, item_type: str, item_id: str) -> bool:
        return await _run(self._is_saved, item_type, item_id)

    @staticmethod
    def _list_by_type(item_type: str) -> list[Favourite]:
        with SessionLocal() as db:
            return (
                db.query(Favourite)
                .filter_by(item_type=item_type)
                .order_by(Favourite.created_at.desc())
                .all()
            )

    async def list_characters(self) -> list[Favourite]:
        return await _run(self._list_by_type, "character")

    async def list_categories(self) -> list[Favourite]:
        return await _run(self._list_by_type, "category")

    @staticmethod
    def _list_all() -> list[Favourite]:
        with SessionLocal() as db:
            return db.query(Favourite).order_by(Favourite.created_at.desc()).all()

    async def list_all(self) -> list[Favourite]:
        return await _run(self._list_all)


# ──────────────────────────── singletons ─────────────────────────

project_repo = ProjectRepo()
favourite_repo = FavouriteRepo()
