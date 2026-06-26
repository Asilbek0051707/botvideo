"""SQLAlchemy ORM models for bot-local data."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Project(Base):
    """A video production project created by the admin."""

    __tablename__ = "bot_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200))
    category_id: Mapped[str] = mapped_column(String(50))
    category_name: Mapped[str] = mapped_column(String(100))
    character_id: Mapped[str] = mapped_column(String(100))
    character_name: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str] = mapped_column(Text, default="")
    saved_prompts: Mapped[str] = mapped_column(Text, default="{}")   # JSON string
    saved_materials: Mapped[str] = mapped_column(Text, default="[]") # JSON string
    saved_ideas: Mapped[str] = mapped_column(Text, default="[]")     # JSON string
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Favourite(Base):
    """A saved favourite — character, category, material, or project."""

    __tablename__ = "bot_favourites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_type: Mapped[str] = mapped_column(String(20))   # character|category|project
    item_id: Mapped[str] = mapped_column(String(200))    # composite key, e.g. "marvel:spider_man"
    item_name: Mapped[str] = mapped_column(String(200))
    category_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    meta: Mapped[str] = mapped_column(Text, default="{}")  # extra JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
