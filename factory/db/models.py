"""SQLAlchemy ORM models — the persistent domain.

users ──< channels ──< jobs ──< videos
                          │
                          ├──< assets   (images, audio, clips, subtitles, logs)
                          └──< events   (audit / analytics timeline)
users ──< subscriptions
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from factory.db.base import Base, JSONType


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class JobStatus(str, enum.Enum):
    queued = "queued"
    scripting = "scripting"
    voicing = "voicing"
    rendering = "rendering"
    assembling = "assembling"
    uploading = "uploading"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


class JobSource(str, enum.Enum):
    api = "api"
    telegram = "telegram"
    scheduler = "scheduler"
    dashboard = "dashboard"


class AssetKind(str, enum.Enum):
    image = "image"
    audio = "audio"
    video_clip = "video_clip"
    final_video = "final_video"
    thumbnail = "thumbnail"
    subtitle = "subtitle"
    log = "log"


class PlanTier(str, enum.Enum):
    free = "free"
    creator = "creator"
    studio = "studio"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, index=True)
    telegram_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    plan: Mapped[PlanTier] = mapped_column(SAEnum(PlanTier), default=PlanTier.free, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    channels: Mapped[list[Channel]] = relationship(back_populates="user", cascade="all, delete-orphan")
    jobs: Mapped[list[Job]] = relationship(back_populates="user")
    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="user")


class Channel(Base, TimestampMixin):
    __tablename__ = "channels"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    niche: Mapped[str | None] = mapped_column(String(120))
    language: Mapped[str] = mapped_column(String(12), default="en", nullable=False)
    voice: Mapped[str | None] = mapped_column(String(80))
    branding: Mapped[dict] = mapped_column(JSONType, default=dict)  # colors, logo, font, intro/outro

    user: Mapped[User] = relationship(back_populates="channels")
    jobs: Mapped[list[Job]] = relationship(back_populates="channel")


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    channel_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("channels.id"), index=True)

    topic: Mapped[str] = mapped_column(Text, nullable=False)
    style: Mapped[str] = mapped_column(String(60), default="documentary")
    source: Mapped[JobSource] = mapped_column(SAEnum(JobSource), default=JobSource.api, nullable=False)

    status: Mapped[JobStatus] = mapped_column(
        SAEnum(JobStatus), default=JobStatus.queued, nullable=False, index=True
    )
    stage: Mapped[str | None] = mapped_column(String(60))
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0..100
    params: Mapped[dict] = mapped_column(JSONType, default=dict)  # voice, duration, lang, etc.
    script: Mapped[dict | None] = mapped_column(JSONType)         # produced script + scenes
    error: Mapped[str | None] = mapped_column(Text)
    celery_task_id: Mapped[str | None] = mapped_column(String(80), index=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User | None] = relationship(back_populates="jobs")
    channel: Mapped[Channel | None] = relationship(back_populates="jobs")
    video: Mapped[Video | None] = relationship(back_populates="job", uselist=False)
    assets: Mapped[list[Asset]] = relationship(back_populates="job", cascade="all, delete-orphan")
    events: Mapped[list[Event]] = relationship(back_populates="job", cascade="all, delete-orphan")


class Video(Base, TimestampMixin):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSONType, default=list)
    duration_sec: Mapped[float | None] = mapped_column()
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    storage_key: Mapped[str | None] = mapped_column(String(512))
    url: Mapped[str | None] = mapped_column(String(1024))
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024))
    captions_url: Mapped[str | None] = mapped_column(String(1024))

    job: Mapped[Job] = relationship(back_populates="video")


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    kind: Mapped[AssetKind] = mapped_column(SAEnum(AssetKind), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1024))
    meta: Mapped[dict] = mapped_column(JSONType, default=dict)

    job: Mapped[Job] = relationship(back_populates="assets")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(60), nullable=False)
    data: Mapped[dict] = mapped_column(JSONType, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job: Mapped[Job | None] = relationship(back_populates="events")


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan: Mapped[PlanTier] = mapped_column(SAEnum(PlanTier), default=PlanTier.free, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active")
    provider: Mapped[str | None] = mapped_column(String(40))     # stripe, lemonsqueezy, ...
    external_id: Mapped[str | None] = mapped_column(String(120))
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="subscriptions")
