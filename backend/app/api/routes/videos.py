"""Read-only video catalog (render history / dashboard feed)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import ApiKeyDep, DbDep
from factory.db.models import Video
from factory.schemas import VideoOut

router = APIRouter(prefix="/videos", tags=["videos"], dependencies=[ApiKeyDep])


@router.get("", response_model=list[VideoOut])
def list_videos(
    db: Session = DbDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[VideoOut]:
    rows = (
        db.execute(select(Video).order_by(Video.created_at.desc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return [VideoOut.model_validate(v) for v in rows]


@router.get("/{video_id}", response_model=VideoOut)
def get_video(video_id: uuid.UUID, db: Session = DbDep) -> VideoOut:
    video = db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="video not found")
    return VideoOut.model_validate(video)
