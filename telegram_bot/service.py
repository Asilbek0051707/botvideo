"""Sync helpers bridging the bot to the factory core (DB + queue).

Handlers call these via asyncio.to_thread so the event loop never blocks on DB.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select

from factory.core.config import settings
from factory.db.models import Job, JobSource, JobStatus, User
from factory.db.session import session_scope
from factory.services import jobs as job_service
from factory.services.queue import enqueue_pipeline


def get_or_create_user(telegram_id: int, name: str | None) -> uuid.UUID:
    with session_scope() as db:
        user = db.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id, display_name=name)
            db.add(user)
            db.flush()
        return user.id


def daily_count(user_id: uuid.UUID) -> int:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    with session_scope() as db:
        return int(
            db.execute(
                select(func.count()).select_from(Job).where(
                    Job.user_id == user_id, Job.created_at >= start
                )
            ).scalar_one()
        )


def submit_topic(topic: str, *, telegram_id: int, chat_id: int, name: str | None) -> dict:
    user_id = get_or_create_user(telegram_id, name)
    if telegram_id not in settings.admin_id_set:
        used = daily_count(user_id)
        if used >= settings.telegram_user_daily_limit:
            return {"ok": False, "reason": "limit", "used": used, "limit": settings.telegram_user_daily_limit}

    with session_scope() as db:
        job = job_service.create_job(
            db,
            topic=topic,
            source=JobSource.telegram,
            user_id=user_id,
            params={"chat_id": chat_id, "language": "en"},
        )
        task_id = enqueue_pipeline(job.id)
        job.celery_task_id = task_id
        db.commit()
        return {"ok": True, "job_id": str(job.id), "status": job.status.value}


def job_summary(job_id: str) -> str | None:
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        return None
    with session_scope() as db:
        job = job_service.get_job(db, jid)
        if not job:
            return None
        line = f"🎬 <b>{job.topic[:60]}</b>\nstatus: <b>{job.status.value}</b> ({job.progress}%)"
        if job.stage:
            line += f"\nstage: {job.stage}"
        if job.video and job.video.url:
            line += f"\n▶️ {job.video.url}"
        if job.error:
            line += f"\n⚠️ {job.error[:200]}"
        return line


def stats() -> dict:
    with session_scope() as db:
        rows = db.execute(select(Job.status, func.count()).group_by(Job.status)).all()
        return {status.value: int(count) for status, count in rows}


def recent(limit: int = 5) -> list[str]:
    with session_scope() as db:
        rows = db.execute(select(Job).order_by(Job.created_at.desc()).limit(limit)).scalars().all()
        return [f"{str(j.id)[:8]} · {j.status.value:9} · {j.topic[:40]}" for j in rows]


def cancel(job_id: str) -> bool:
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        return False
    with session_scope() as db:
        job = job_service.get_job(db, jid)
        if not job or job.status in (JobStatus.completed, JobStatus.failed, JobStatus.canceled):
            return False
        if job.celery_task_id:
            from factory.services.queue import celery_app

            celery_app.control.revoke(job.celery_task_id, terminate=True)
        job_service.set_status(db, job, JobStatus.canceled, stage="canceled")
        return True


def retry(job_id: str) -> bool:
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        return False
    with session_scope() as db:
        job = job_service.get_job(db, jid)
        if not job:
            return False
        job_service.set_status(db, job, JobStatus.queued, stage="requeued", progress=0)
        job.error = None
        task_id = enqueue_pipeline(job.id)
        job.celery_task_id = task_id
        db.commit()
        return True
