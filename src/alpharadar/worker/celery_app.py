"""Celery application configuration for AlphaRadar."""

import os

from celery import Celery

from alpharadar.worker.schedules import beat_schedule

app = Celery("alpharadar")

_redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app.conf.update(
    broker_url=_redis_url,
    result_backend=_redis_url,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Argentina/Buenos_Aires",
    task_time_limit=300,
    task_soft_time_limit=240,
    include=["alpharadar.worker.tasks"],
    beat_schedule=beat_schedule,
)
