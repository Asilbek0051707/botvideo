"""Trend Analyzer DB models — trends, keywords, ideas, settings.

Shares the same Base as models.py so one create_all() creates all tables.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from telegram_bot.db.models import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Trend ─────────────────────────────────────────────────────────


class Trend(Base):
    """A single trend record (character, topic, game, movie, etc.)."""

    __tablename__ = "bot_trends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50))       # cartoon|gaming|anime|meme|general
    score: Mapped[int] = mapped_column(Integer, default=0)  # 0–100 viral score
    growth_pct: Mapped[float] = mapped_column(Float, default=0.0)
    popularity: Mapped[str] = mapped_column(String(20), default="medium")   # low|medium|high
    difficulty: Mapped[str] = mapped_column(String(20), default="medium")   # low|medium|high
    audience: Mapped[str] = mapped_column(String(100), default="kids")
    video_types: Mapped[str] = mapped_column(Text, default="[]")      # JSON list
    related_chars: Mapped[str] = mapped_column(Text, default="[]")    # JSON list
    related_music: Mapped[str] = mapped_column(Text, default="[]")    # JSON list
    keywords: Mapped[str] = mapped_column(Text, default="[]")         # JSON list
    country: Mapped[str] = mapped_column(String(5), default="ALL")
    language: Mapped[str] = mapped_column(String(10), default="en")
    source: Mapped[str] = mapped_column(String(50), default="manual") # manual|yt-dlp|ddg
    status: Mapped[str] = mapped_column(String(20), default="active") # active|archived
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_trend_category", "category"),
        Index("ix_trend_status", "status"),
        Index("ix_trend_score", "score"),
    )


# ── TrendKeyword ──────────────────────────────────────────────────


class TrendKeyword(Base):
    """A keyword entry in the keyword engine."""

    __tablename__ = "bot_trend_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(200))
    related_keywords: Mapped[str] = mapped_column(Text, default="[]")   # JSON list
    search_intent: Mapped[str] = mapped_column(String(50), default="general")
    priority: Mapped[int] = mapped_column(Integer, default=5)            # 1–10
    trend_level: Mapped[str] = mapped_column(String(20), default="medium")  # low|medium|high|viral
    category: Mapped[str] = mapped_column(String(50), default="general")
    language: Mapped[str] = mapped_column(String(10), default="en")
    country: Mapped[str] = mapped_column(String(5), default="ALL")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_kw_keyword", "keyword"),
        Index("ix_kw_category", "category"),
        Index("ix_kw_priority", "priority"),
    )


# ── VideoIdea ─────────────────────────────────────────────────────


class VideoIdea(Base):
    """A generated or saved video idea."""

    __tablename__ = "bot_video_ideas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")
    character: Mapped[str] = mapped_column(String(200), default="")
    category: Mapped[str] = mapped_column(String(50), default="general")
    trend_score: Mapped[int] = mapped_column(Integer, default=0)
    keywords: Mapped[str] = mapped_column(Text, default="[]")   # JSON list
    status: Mapped[str] = mapped_column(String(20), default="saved")  # saved|done|archived
    notes: Mapped[str] = mapped_column(Text, default="")
    project_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_idea_character", "character"),
        Index("ix_idea_status", "status"),
    )


# ── TrendSettings ─────────────────────────────────────────────────


class TrendSettings(Base):
    """Per-bot trend analyzer settings (single row)."""

    __tablename__ = "bot_trend_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    refresh_interval: Mapped[int] = mapped_column(Integer, default=24)          # hours
    language: Mapped[str] = mapped_column(String(10), default="en")
    countries: Mapped[str] = mapped_column(Text, default='["US","GB","UZ"]')    # JSON list
    categories: Mapped[str] = mapped_column(Text, default='["cartoon","gaming","anime"]')  # JSON
    default_filter: Mapped[str] = mapped_column(String(20), default="popular")  # popular|newest|score
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
