"""Request/response models for the REST API."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from factory.db.models import AssetKind, JobSource, JobStatus


class JobCreate(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500, examples=["3 facts about the deep ocean"])
    style: str = Field("documentary", examples=["documentary", "energetic", "calm", "meme"])
    voice: str | None = Field(None, examples=["narrator", "Rachel"])
    language: str = Field("en", max_length=12)
    duration_sec: int | None = Field(None, ge=10, le=180)
    channel_id: uuid.UUID | None = None
    params: dict = Field(default_factory=dict, description="Free-form pipeline overrides")


class VideoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str | None = None
    tags: list = Field(default_factory=list)
    duration_sec: float | None = None
    width: int | None = None
    height: int | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    captions_url: str | None = None


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    kind: AssetKind
    url: str | None = None
    meta: dict = Field(default_factory=dict)


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    topic: str
    style: str
    source: JobSource
    status: JobStatus
    stage: str | None = None
    progress: int = 0
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class JobDetail(JobOut):
    params: dict = Field(default_factory=dict)
    script: dict | None = None
    video: VideoOut | None = None
    assets: list[AssetOut] = Field(default_factory=list)


class JobList(BaseModel):
    items: list[JobOut]
    total: int
    limit: int
    offset: int
