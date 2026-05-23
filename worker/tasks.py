"""The end-to-end render pipeline task.

topic -> orchestrator(plan) -> voice -> text-to-video -> assemble + captions
      -> upload -> persist video/assets -> notify (telegram / webhook).
"""

from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path

import httpx

from factory.agents import Orchestrator, VoiceAgent
from factory.core.config import settings
from factory.core.logging import get_logger
from factory.db.models import AssetKind, JobStatus
from factory.db.session import session_scope
from factory.render import RenderPipeline
from factory.services import jobs as job_service
from factory.services.notify import send_webhook, telegram_send_message, telegram_send_video
from factory.services.queue import PIPELINE_TASK, celery_app
from factory.storage import get_storage

log = get_logger("worker")

RETRYABLE = (httpx.HTTPError, ConnectionError, TimeoutError, OSError)


@celery_app.task(
    bind=True,
    name=PIPELINE_TASK,
    acks_late=True,
    max_retries=2,
    default_retry_delay=30,
)
def run_pipeline(self, job_id: str) -> dict:
    workdir = Path(tempfile.mkdtemp(prefix=f"job_{job_id}_"))
    started = time.time()
    try:
        with session_scope() as db:
            job = job_service.get_job(db, job_id)
            if job is None:
                log.warning("pipeline.job_missing", job_id=job_id)
                return {"job_id": job_id, "status": "missing"}
            if job.status == JobStatus.canceled:
                return {"job_id": job_id, "status": "canceled"}

            params = job.params or {}
            target = int(params.get("duration_sec") or settings.target_duration_sec)
            language = params.get("language", "en")

            # 1) Plan (script + scenes + SEO)
            job_service.set_status(db, job, JobStatus.scripting, stage="planning", progress=5)
            plan = Orchestrator().build_plan(
                job.topic, style=job.style, language=language, target_duration=target
            )
            job.script = plan.model_dump()
            db.commit()

            # 2) Voiceover
            job_service.set_status(db, job, JobStatus.voicing, stage="tts", progress=25)
            audio_bytes, ext = VoiceAgent().synthesize(
                plan.full_narration, voice=params.get("voice"), fallback_seconds=plan.total_duration
            )
            audio_path = workdir / f"voice.{ext}"
            audio_path.write_bytes(audio_bytes)

            # 3) Render (text-to-video per scene -> assemble -> captions -> mux)
            def progress_cb(done: int, total: int) -> None:
                pct = 40 + int(40 * done / max(1, total))
                with session_scope() as inner:
                    j = job_service.get_job(inner, job_id)
                    if j:
                        job_service.set_status(inner, j, JobStatus.rendering, stage=f"render {done}/{total}", progress=pct)

            job_service.set_status(db, job, JobStatus.rendering, stage="render", progress=40)
            result = RenderPipeline().render(plan, audio_path, workdir, progress_cb=progress_cb)

            # 4) Upload artifacts
            job_service.set_status(db, job, JobStatus.uploading, stage="upload", progress=85)
            storage = get_storage()
            base = f"jobs/{job_id}"
            video_url = storage.put_file(result.video_path, f"{base}/final.mp4", "video/mp4")
            thumb_url = storage.put_file(result.thumbnail_path, f"{base}/thumbnail.jpg", "image/jpeg")
            srt_url = storage.put_file(result.srt_path, f"{base}/captions.srt", "text/plain")
            audio_url = storage.put_file(audio_path, f"{base}/voice.{ext}")

            job_service.add_asset(db, job.id, AssetKind.final_video, f"{base}/final.mp4", video_url,
                                  {"duration": result.duration})
            job_service.add_asset(db, job.id, AssetKind.thumbnail, f"{base}/thumbnail.jpg", thumb_url)
            job_service.add_asset(db, job.id, AssetKind.subtitle, f"{base}/captions.srt", srt_url)
            job_service.add_asset(db, job.id, AssetKind.audio, f"{base}/voice.{ext}", audio_url)

            # 5) Persist the video record
            job_service.attach_video(
                db, job,
                title=plan.title,
                description=plan.description,
                tags=plan.tags,
                duration_sec=result.duration,
                width=result.width,
                height=result.height,
                storage_key=f"{base}/final.mp4",
                url=video_url,
                thumbnail_url=thumb_url,
                captions_url=srt_url,
            )

            job_service.set_status(db, job, JobStatus.completed, stage="done", progress=100)
            _notify_done(params, plan.title, video_url, job_id)

            log.info("pipeline.completed", job_id=job_id, seconds=round(time.time() - started, 1),
                     duration=result.duration)
            return {"job_id": job_id, "status": "completed", "video_url": video_url}

    except RETRYABLE as exc:
        log.warning("pipeline.retryable_error", job_id=job_id, error=str(exc), retry=self.request.retries)
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            _fail(job_id, f"transient error after retries: {exc}")
            return {"job_id": job_id, "status": "failed"}
    except Exception as exc:  # deterministic failure — don't burn GPU retrying
        log.error("pipeline.failed", job_id=job_id, error=str(exc))
        _fail(job_id, str(exc))
        return {"job_id": job_id, "status": "failed"}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _fail(job_id: str, error: str) -> None:
    with session_scope() as db:
        job = job_service.get_job(db, job_id)
        if job and job.status not in (JobStatus.completed, JobStatus.canceled):
            job_service.mark_failed(db, job, error)
            params = job.params or {}
            if params.get("chat_id"):
                telegram_send_message(params["chat_id"], f"❌ Render failed: {error[:300]}")
            if params.get("webhook_url"):
                send_webhook(params["webhook_url"], "job.failed", {"job_id": job_id, "error": error})


def _notify_done(params: dict, title: str, video_url: str, job_id: str) -> None:
    if params.get("chat_id"):
        if not telegram_send_video(params["chat_id"], video_url, caption=f"✅ {title}"):
            telegram_send_message(params["chat_id"], f"✅ <b>{title}</b>\n{video_url}")
    if params.get("webhook_url"):
        send_webhook(params["webhook_url"], "job.completed",
                     {"job_id": job_id, "title": title, "video_url": video_url})


@celery_app.task(name="factory.maintenance.cleanup_temp")
def cleanup_temp(max_age_sec: int = 3600) -> int:
    """Remove stale per-job temp dirs left by crashed renders."""
    removed = 0
    root = Path(tempfile.gettempdir())
    now = time.time()
    for d in root.glob("job_*"):
        try:
            if d.is_dir() and (now - d.stat().st_mtime) > max_age_sec:
                shutil.rmtree(d, ignore_errors=True)
                removed += 1
        except OSError:
            continue
    log.info("maintenance.cleanup_temp", removed=removed)
    return removed
