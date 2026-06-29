"""Asset Library DB models — STEP 7 Material Search Engine.

Stores metadata only — no copyrighted files.
References (URLs, source names, licenses) are stored instead.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from telegram_bot.db.models import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Asset(Base):
    """A saved reference to an online asset — title + URL + metadata."""

    __tablename__ = "mat_assets"

    id:           Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    title:        Mapped[str]   = mapped_column(String(300))
    description:  Mapped[str]   = mapped_column(Text, default="")
    category:     Mapped[str]   = mapped_column(String(50),  default="general")
    char_name:    Mapped[str]   = mapped_column(String(200), default="")
    asset_type:   Mapped[str]   = mapped_column(String(30),  default="unknown")
    # png | gif | mp4 | webm | svg | music | sfx | voice | bg | overlay |
    # particles | transition | icon | font | prompt | thumb_ref | capcut |
    # premiere | ae | gameplay | animation_ref
    source_name:  Mapped[str]   = mapped_column(String(200), default="")
    source_url:   Mapped[str]   = mapped_column(String(1000), default="")
    license_type: Mapped[str]   = mapped_column(String(50),  default="unknown")
    # free | cc0 | cc-by | paid | unknown
    tags:         Mapped[str]   = mapped_column(Text, default="[]")   # JSON list[str]
    rating:       Mapped[float] = mapped_column(Float, default=0.0)
    notes:        Mapped[str]   = mapped_column(Text, default="")
    is_favorite:  Mapped[bool]  = mapped_column(Boolean, default=False)
    project_id:   Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at:   Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_mat_type",  "asset_type"),
        Index("ix_mat_cat",   "category"),
        Index("ix_mat_char",  "char_name"),
        Index("ix_mat_fav",   "is_favorite"),
        Index("ix_mat_ts",    "created_at"),
    )


class AssetCollection(Base):
    """A named set of assets (e.g. 'Marvel Pack', 'Minecraft Resources')."""

    __tablename__ = "mat_collections"

    id:          Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:        Mapped[str]  = mapped_column(String(200))
    description: Mapped[str]  = mapped_column(Text, default="")
    category:    Mapped[str]  = mapped_column(String(50), default="general")
    tags:        Mapped[str]  = mapped_column(Text, default="[]")  # JSON
    created_at:  Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (Index("ix_col_name", "name"),)


class CollectionAsset(Base):
    """Many-to-many: Asset ↔ AssetCollection."""

    __tablename__ = "mat_collection_assets"

    id:            Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    collection_id: Mapped[int] = mapped_column(Integer)
    asset_id:      Mapped[int] = mapped_column(Integer)
    added_at:      Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_ca_col", "collection_id"),
        Index("ix_ca_ast", "asset_id"),
    )


class SearchHistory(Base):
    """Per-user search history for the Material Finder."""

    __tablename__ = "mat_search_history"

    id:           Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:      Mapped[int] = mapped_column(Integer)
    query:        Mapped[str] = mapped_column(String(500))
    asset_type:   Mapped[str] = mapped_column(String(30), default="search")
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at:   Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_sh_user", "user_id"),
        Index("ix_sh_ts",   "created_at"),
    )


class PromptTemplate(Base):
    """Reusable AI prompt templates stored in the asset library."""

    __tablename__ = "mat_prompt_templates"

    id:            Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:          Mapped[str]  = mapped_column(String(200))
    category:      Mapped[str]  = mapped_column(String(50),  default="general")
    prompt_type:   Mapped[str]  = mapped_column(String(30),  default="image")
    # image | video | voice | animation | thumbnail | background
    template_text: Mapped[str]  = mapped_column(Text)
    variables:     Mapped[str]  = mapped_column(Text, default="[]")  # JSON list[str]
    usage_count:   Mapped[int]  = mapped_column(Integer, default=0)
    is_active:     Mapped[bool] = mapped_column(Boolean, default=True)
    created_at:    Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_pt_type", "prompt_type"),
        Index("ix_pt_cat",  "category"),
        Index("ix_pt_act",  "is_active"),
    )
