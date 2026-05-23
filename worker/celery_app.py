"""Celery entrypoint: `celery -A worker.celery_app.celery worker ...`

Reuses the shared app from `factory.services.queue` and registers task bodies +
the beat schedule.
"""

from __future__ import annotations

from celery.schedules import crontab

from factory.core.logging import configure_logging
from factory.services.queue import celery_app as celery

configure_logging()

# Importing registers @celery.task bodies against the shared app.
import worker.tasks  # noqa: E402,F401

celery.conf.beat_schedule = {
    "cleanup-temp-dirs": {
        "task": "factory.maintenance.cleanup_temp",
        "schedule": crontab(minute="*/30"),
    },
}

__all__ = ["celery"]
