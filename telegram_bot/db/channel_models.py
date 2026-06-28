"""YouTube Channel Analyzer DB models.

All tables share Base from models.py so a single create_all() creates everything.
Designed for scalability: each entity is independent with JSON blobs for lists.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from telegram_bot.db.models import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── ChannelRecord ─────────────────────────────────────────────────


class ChannelRecord(Base):
    """Saved channel analysis / search history entry."""

    __tablename__ = "ca_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(500))
    handle: Mapped[str] = mapped_column(String(200), default="")
    name: Mapped[str] = mapped_column(String(300), default="")
    subs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_views: Mapped[int] = mapped_column(Integer, default=0)
    video_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_views: Mapped[int] = mapped_column(Integer, default=0)
    country: Mapped[str] = mapped_column(String(5), default="")
    category: Mapped[str] = mapped_column(String(50), default="general")
    description: Mapped[str] = mapped_column(Text, default="")
    health_score: Mapped[int] = mapped_column(Integer, default=0)    # 0–100
    growth_trend: Mapped[str] = mapped_column(String(20), default="unknown")
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_ch_name", "name"),
        Index("ix_ch_handle", "handle"),
    )


# ── VideoRecord ───────────────────────────────────────────────────


class VideoRecord(Base):
    """Saved video analysis result."""

    __tablename__ = "ca_videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(500))
    channel_name: Mapped[str] = mapped_column(String(300), default="")
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[str] = mapped_column(String(20), default="")
    published_at: Mapped[str] = mapped_column(String(30), default="")
    tags: Mapped[str] = mapped_column(Text, default="[]")          # JSON list
    keywords: Mapped[str] = mapped_column(Text, default="[]")      # JSON list
    description: Mapped[str] = mapped_column(Text, default="")
    seo_score: Mapped[int] = mapped_column(Integer, default=0)
    hook_score: Mapped[int] = mapped_column(Integer, default=0)
    thumbnail_score: Mapped[int] = mapped_column(Integer, default=0)
    overall_score: Mapped[int] = mapped_column(Integer, default=0)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_vid_id", "video_id"),
        Index("ix_vid_channel", "channel_name"),
    )


# ── CompetitorRecord ──────────────────────────────────────────────


class CompetitorRecord(Base):
    """Saved competitor channel."""

    __tablename__ = "ca_competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(500), default="")
    niche: Mapped[str] = mapped_column(String(200), default="")     # search niche
    subs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_views: Mapped[int] = mapped_column(Integer, default=0)
    upload_freq: Mapped[str] = mapped_column(String(50), default="")
    category: Mapped[str] = mapped_column(String(50), default="general")
    strategy: Mapped[str] = mapped_column(Text, default="")
    strengths: Mapped[str] = mapped_column(Text, default="[]")      # JSON list
    weaknesses: Mapped[str] = mapped_column(Text, default="[]")     # JSON list
    notes: Mapped[str] = mapped_column(Text, default="")
    ranking: Mapped[int] = mapped_column(Integer, default=0)
    country: Mapped[str] = mapped_column(String(5), default="")
    language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_comp_name", "name"),
        Index("ix_comp_niche", "niche"),
    )


# ── AnalysisReport ────────────────────────────────────────────────


class AnalysisReport(Base):
    """Generated and saved analysis report."""

    __tablename__ = "ca_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_type: Mapped[str] = mapped_column(String(30), default="channel")  # channel|video|seo|competitor
    title: Mapped[str] = mapped_column(String(300))
    subject: Mapped[str] = mapped_column(String(500), default="")     # URL or name
    summary: Mapped[str] = mapped_column(Text, default="")
    scores: Mapped[str] = mapped_column(Text, default="{}")           # JSON dict
    strengths: Mapped[str] = mapped_column(Text, default="[]")        # JSON list
    weaknesses: Mapped[str] = mapped_column(Text, default="[]")       # JSON list
    recommendations: Mapped[str] = mapped_column(Text, default="[]")  # JSON list
    notes: Mapped[str] = mapped_column(Text, default="")
    project_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_rep_type", "report_type"),
        Index("ix_rep_created", "created_at"),
    )


# ── SEORecord ────────────────────────────────────────────────────


class SEORecord(Base):
    """Saved SEO analysis for a title / video."""

    __tablename__ = "ca_seo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(Text, default="[]")          # JSON list
    hashtags: Mapped[str] = mapped_column(Text, default="[]")      # JSON list
    keywords: Mapped[str] = mapped_column(Text, default="[]")      # JSON list
    search_intent: Mapped[str] = mapped_column(String(50), default="general")
    seo_score: Mapped[int] = mapped_column(Integer, default=0)
    suggestions: Mapped[str] = mapped_column(Text, default="[]")   # JSON list
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (Index("ix_seo_score", "seo_score"),)


# ── GrowthSnapshot ────────────────────────────────────────────────


class GrowthSnapshot(Base):
    """Historical channel metric snapshot for growth tracking."""

    __tablename__ = "ca_growth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_name: Mapped[str] = mapped_column(String(300))
    channel_url: Mapped[str] = mapped_column(String(500), default="")
    subs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_views: Mapped[int] = mapped_column(Integer, default=0)
    video_count: Mapped[int] = mapped_column(Integer, default=0)
    estimated_growth: Mapped[float] = mapped_column(Float, default=0.0)
    trend: Mapped[str] = mapped_column(String(20), default="unknown")  # up|down|stable
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_growth_channel", "channel_name"),
        Index("ix_growth_date", "snapshot_date"),
    )
