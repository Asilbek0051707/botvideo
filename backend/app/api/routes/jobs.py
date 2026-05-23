"""Render job endpoints — create, fetch, list, cancel."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import ApiKeyDep, DbDep
from factory.core.config import settings
from factory.db.models import JobSource, JobStatus
from factory.schemas import JobCreate, JobDetail, JobList, JobOut
from factory.services import jobs as job_service
from factory.services.queue import enqueue_pipeline

router = APIRouter(prefix="/jobs", tags=["jobs"], dependencies=[ApiKeyDep])


@router.post("", response_model=JobDetail, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = DbDep) -> JobDetail:
    params = dict(payload.params)
    params.update(
        {
            "voice": payload.voice,
            "language": payload.language,
            "duration_sec": payload.duration_sec or settings.target_duration_sec,
        }
    )
    job = job_service.create_job(
        db,
        topic=payload.topic,
        style=payload.style,
        source=JobSource.api,
        channel_id=payload.channel_id,
        params=params,
    )
    task_id = enqueue_pipeline(job.id)
    job.celery_task_id = task_id
    db.commit()
    db.refresh(job)
    return JobDetail.model_validate(job)


@router.get("", response_model=JobList)
def list_jobs(
    db: Session = DbDep,
    status_filter: JobStatus | None = Query(default=None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> JobList:
    items, total = job_service.list_jobs(db, status=status_filter, limit=limit, offset=offset)
    return JobList(
        items=[JobOut.model_validate(j) for j in items], total=total, limit=limit, offset=offset
    )


@router.get("/{job_id}", response_model=JobDetail)
def get_job(job_id: uuid.UUID, db: Session = DbDep) -> JobDetail:
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobDetail.model_validate(job)


@router.post("/{job_id}/cancel", response_model=JobOut)
def cancel_job(job_id: uuid.UUID, db: Session = DbDep) -> JobOut:
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status in (JobStatus.completed, JobStatus.failed, JobStatus.canceled):
        raise HTTPException(status_code=409, detail=f"job already {job.status.value}")
    if job.celery_task_id:
        from factory.services.queue import celery_app

        celery_app.control.revoke(job.celery_task_id, terminate=True)
    job_service.set_status(db, job, JobStatus.canceled, stage="canceled")
    return JobOut.model_validate(job)
