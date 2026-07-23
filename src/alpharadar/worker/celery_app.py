"""Celery application configuration for AlphaRadar."""

from celery import Celery

from alpharadar.worker.schedules import beat_schedule

app = Celery("alpharadar")

app.conf.update(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/0",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Argentina/Buenos_Aires",
    task_time_limit=300,
    task_soft_time_limit=240,
    include=["alpharadar.worker.tasks"],
    beat_schedule=beat_schedule,
)
