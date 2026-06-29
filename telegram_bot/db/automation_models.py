"""Automation Engine DB models — STEP 10.

Tables:
  auto_runs        — every automation execution
  auto_workflows   — named, reusable step chains
  auto_packages    — saved full-generate results
  auto_convs       — AI assistant conversation sessions
  auto_settings    — single-row admin config
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from telegram_bot.db.models import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AutomationRun(Base):
    """One row for every automation execution (quick/package/project/chat)."""

    __tablename__ = "auto_runs"

    id:            Mapped[int]             = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic:         Mapped[str]             = mapped_column(String(300))
    run_type:      Mapped[str]             = mapped_column(String(30), index=True)
    # quick | package | project | workflow | assistant | planner
    provider_slug: Mapped[str]             = mapped_column(String(50), default="local")
    status:        Mapped[str]             = mapped_column(String(20), default="done", index=True)
    # done | failed | partial
    result_json:   Mapped[str]             = mapped_column(Text, default="{}")
    error_msg:     Mapped[str]             = mapped_column(String(500), default="")
    duration_ms:   Mapped[int]             = mapped_column(Integer, default=0)
    is_favorite:   Mapped[bool]            = mapped_column(Boolean, default=False, index=True)
    created_at:    Mapped[datetime]        = mapped_column(DateTime, default=_now, index=True)


class WorkflowTemplate(Base):
    """User-defined or built-in workflow step chains."""

    __tablename__ = "auto_workflows"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:        Mapped[str]      = mapped_column(String(100))
    description: Mapped[str]      = mapped_column(String(300), default="")
    steps_json:  Mapped[str]      = mapped_column(Text, default="[]")
    # [{"key": "script", "params": {}}, {"key": "title", ...}, ...]
    is_default:  Mapped[bool]     = mapped_column(Boolean, default=False)
    is_active:   Mapped[bool]     = mapped_column(Boolean, default=True, index=True)
    created_at:  Mapped[datetime] = mapped_column(DateTime, default=_now)


class AutomationPackage(Base):
    """Full generated content packages (saved by user or auto-saved)."""

    __tablename__ = "auto_packages"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic:       Mapped[str]      = mapped_column(String(300), index=True)
    content_json:Mapped[str]      = mapped_column(Text, default="{}")
    run_id:      Mapped[int]      = mapped_column(Integer, default=0)
    is_favorite: Mapped[bool]     = mapped_column(Boolean, default=False, index=True)
    created_at:  Mapped[datetime] = mapped_column(DateTime, default=_now, index=True)


class AssistantConversation(Base):
    """AI assistant conversation sessions."""

    __tablename__ = "auto_convs"

    id:             Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id:     Mapped[str]      = mapped_column(String(100), unique=True, index=True)
    messages_json:  Mapped[str]      = mapped_column(Text, default="[]")
    # [{"role": "user"|"assistant", "content": "..."}]
    provider_slug:  Mapped[str]      = mapped_column(String(50), default="")
    total_messages: Mapped[int]      = mapped_column(Integer, default=0)
    created_at:     Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at:     Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)


class AutomationSettings(Base):
    """Single-row settings for the automation engine (id always = 1)."""

    __tablename__ = "auto_settings"

    id:                  Mapped[int]   = mapped_column(Integer, primary_key=True, default=1)
    default_provider:    Mapped[str]   = mapped_column(String(50), default="local")
    language:            Mapped[str]   = mapped_column(String(10), default="en")
    creativity:          Mapped[float] = mapped_column(Float, default=0.7)
    output_style:        Mapped[str]   = mapped_column(String(20), default="detailed")
    # concise | detailed | creative
    max_results:         Mapped[int]   = mapped_column(Integer, default=5)
    default_workflow_id: Mapped[int]   = mapped_column(Integer, default=0)
    updated_at:          Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)
