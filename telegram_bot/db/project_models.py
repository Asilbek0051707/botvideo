"""Extended Project DB models — STEP 8 Project Management & AI Workspace.

Augments the existing Project model (models.py) with:
  ProjectMeta    — extra fields (priority, language, completion %, etc.)
  ProjectTask    — per-project task list
  ProjectNote    — per-project notes
  ProjectResource— linked assets / generated content
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from telegram_bot.db.models import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectMeta(Base):
    """Extended metadata for a project — one row per project_id."""

    __tablename__ = "prj_meta"

    id:                    Mapped[int]        = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id:            Mapped[int]        = mapped_column(Integer, unique=True)
    priority:              Mapped[str]        = mapped_column(String(20),  default="medium")
    # low | medium | high | urgent
    language:              Mapped[str]        = mapped_column(String(50),  default="")
    country:               Mapped[str]        = mapped_column(String(50),  default="")
    video_type:            Mapped[str]        = mapped_column(String(30),  default="shorts")
    # shorts | long | story | gaming | kids | educational | funny | other
    video_length:          Mapped[str]        = mapped_column(String(20),  default="")
    target_audience:       Mapped[str]        = mapped_column(String(100), default="")
    tags:                  Mapped[str]        = mapped_column(Text, default="[]")   # JSON list[str]
    estimated_publish_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completion_pct:        Mapped[int]        = mapped_column(Integer, default=0)
    is_archived:           Mapped[bool]       = mapped_column(Boolean, default=False)
    is_favorite:           Mapped[bool]       = mapped_column(Boolean, default=False)
    last_updated:          Mapped[datetime]   = mapped_column(DateTime, default=_now, onupdate=_now)

    __table_args__ = (
        Index("ix_prjm_pid",  "project_id"),
        Index("ix_prjm_prio", "priority"),
        Index("ix_prjm_arch", "is_archived"),
        Index("ix_prjm_fav",  "is_favorite"),
    )


class ProjectTask(Base):
    """A task inside a project (checklist item)."""

    __tablename__ = "prj_tasks"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int]      = mapped_column(Integer)
    title:      Mapped[str]      = mapped_column(String(300))
    status:     Mapped[str]      = mapped_column(String(20), default="todo")
    # todo | in_progress | done | cancelled
    priority:   Mapped[str]      = mapped_column(String(20), default="medium")
    deadline:   Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes:      Mapped[str]      = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    __table_args__ = (
        Index("ix_prjt_pid",    "project_id"),
        Index("ix_prjt_status", "status"),
    )


class ProjectNote(Base):
    """A note attached to a project."""

    __tablename__ = "prj_notes"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int]      = mapped_column(Integer)
    title:      Mapped[str]      = mapped_column(String(200), default="")
    content:    Mapped[str]      = mapped_column(Text)
    is_pinned:  Mapped[bool]     = mapped_column(Boolean, default=False)
    tags:       Mapped[str]      = mapped_column(Text, default="[]")  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    __table_args__ = (
        Index("ix_prjn_pid",    "project_id"),
        Index("ix_prjn_pinned", "is_pinned"),
    )


class ProjectResource(Base):
    """A resource (script, prompt, asset link, etc.) linked to a project."""

    __tablename__ = "prj_resources"

    id:            Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id:    Mapped[int]      = mapped_column(Integer)
    resource_type: Mapped[str]      = mapped_column(String(30), default="note")
    # script | thumbnail | image | animation | video | music | sfx | voice |
    # seo | tags | hashtags | prompt | idea | description | report | other
    title:         Mapped[str]      = mapped_column(String(300))
    url:           Mapped[str]      = mapped_column(String(1000), default="")
    content:       Mapped[str]      = mapped_column(Text, default="")
    notes:         Mapped[str]      = mapped_column(Text, default="")
    created_at:    Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        Index("ix_prjr_pid",  "project_id"),
        Index("ix_prjr_type", "resource_type"),
    )
