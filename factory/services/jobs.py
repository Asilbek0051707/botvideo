"""Job service — the single place that mutates job state.

Used by the API (create/read) and the worker (state transitions, assets, events).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from factory.core.logging import get_logger
from factory.db.models import Asset, AssetKind, Event, Job, JobSource, JobStatus, Video

log = get_logger(__name__)


def create_job(
    db: Session,
    *,
    topic: str,
    style: str = "documentary",
    source: JobSource = JobSource.api,
    user_id: uuid.UUID | None = None,
    channel_id: uuid.UUID | None = None,
    params: dict | None = None,
) -> Job:
    job = Job(
        topic=topic.strip(),
        style=style,
        source=source,
        user_id=user_id,
        channel_id=channel_id,
        params=params or {},
        status=JobStatus.queued,
        progress=0,
    )
    db.add(job)
    db.flush()
    add_event(db, job.id, "job.created", {"topic": topic, "source": source.value})
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: uuid.UUID | str) -> Job | None:
    stmt = (
        select(Job)
        .where(Job.id == _as_uuid(job_id))
        .options(selectinload(Job.video), selectinload(Job.assets))
    )
    return db.execute(stmt).scalar_one_or_none()


def list_jobs(
    db: Session,
    *,
    user_id: uuid.UUID | None = None,
    status: JobStatus | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Job], int]:
    base = select(Job)
    if user_id:
        base = base.where(Job.user_id == user_id)
    if status:
        base = base.where(Job.status == status)
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = (
        db.execute(base.order_by(Job.created_at.desc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return list(rows), int(total)


def set_status(
    db: Session,
    job: Job,
    status: JobStatus,
    *,
    stage: str | None = None,
    progress: int | None = None,
) -> Job:
    job.status = status
    if stage is not None:
        job.stage = stage
    if progress is not None:
        job.progress = max(0, min(100, progress))
    if status == JobStatus.scripting and job.started_at is None:
        job.started_at = datetime.now(timezone.utc)
    if status in (JobStatus.completed, JobStatus.failed, JobStatus.canceled):
        job.finished_at = datetime.now(timezone.utc)
    add_event(db, job.id, "job.status", {"status": status.value, "stage": stage, "progress": job.progress})
    db.commit()
    db.refresh(job)
    log.info("job.status", job_id=str(job.id), status=status.value, stage=stage, progress=job.progress)
    return job


def mark_failed(db: Session, job: Job, error: str) -> Job:
    job.error = error[:4000]
    return set_status(db, job, JobStatus.failed, stage="error", progress=job.progress)


def add_asset(
    db: Session,
    job_id: uuid.UUID,
    kind: AssetKind,
    storage_key: str,
    url: str | None = None,
    meta: dict | None = None,
) -> Asset:
    asset = Asset(job_id=job_id, kind=kind, storage_key=storage_key, url=url, meta=meta or {})
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def attach_video(db: Session, job: Job, **fields) -> Video:
    video = Video(job_id=job.id, **fields)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def add_event(db: Session, job_id: uuid.UUID | None, type_: str, data: dict | None = None) -> None:
    db.add(Event(job_id=job_id, type=type_, data=data or {}))


def _as_uuid(value: uuid.UUID | str) -> uuid.UUID:
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
