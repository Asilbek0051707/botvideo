"""Shared Celery application + enqueue helpers.

Defined here (not in `worker/`) so the API and bot can enqueue tasks by name
without importing heavy render/GPU code. The worker registers the task bodies
against the same `celery_app` instance.
"""

from __future__ import annotations

from celery import Celery

from factory.core.config import settings

PIPELINE_TASK = "factory.pipeline.run"

celery_app = Celery(
    "factory",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_default_queue="default",
    task_track_started=True,
    task_acks_late=True,                 # redeliver if a worker dies mid-render
    worker_prefetch_multiplier=1,        # fair dispatch for long render tasks
    task_reject_on_worker_lost=True,
    result_expires=60 * 60 * 24,
    timezone="UTC",
    broker_connection_retry_on_startup=True,
    task_routes={
        PIPELINE_TASK: {"queue": "render"},
        "factory.maintenance.*": {"queue": "default"},
    },
)


def pipeline_queue() -> str:
    """GPU text-to-video jobs go to the dedicated GPU worker; everything else to CPU."""
    return "gpu" if settings.t2v_provider == "gpu" else "render"


def enqueue_pipeline(job_id: str) -> str:
    result = celery_app.send_task(PIPELINE_TASK, args=[str(job_id)], queue=pipeline_queue())
    return result.id
