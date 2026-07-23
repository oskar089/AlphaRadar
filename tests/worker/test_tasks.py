"""Tests for Celery worker configuration and task stubs."""

from celery import Celery

from alpharadar.worker.celery_app import app


def test_celery_app_is_created() -> None:
    assert app is not None
    assert isinstance(app, Celery)


def test_celery_app_name() -> None:
    assert app.main == "alpharadar"


def test_celery_broker_url() -> None:
    assert "redis" in app.conf.broker_url


def test_celery_result_backend() -> None:
    assert "redis" in app.conf.result_backend


def test_celery_broker_and_backend_are_consistent() -> None:
    assert app.conf.broker_url == app.conf.result_backend


def test_celery_json_serialization() -> None:
    assert app.conf.task_serializer == "json"
    assert app.conf.result_serializer == "json"
    assert app.conf.accept_content == ["json"]


def test_celery_timezone() -> None:
    assert app.conf.timezone == "America/Argentina/Buenos_Aires"


def test_celery_task_time_limits() -> None:
    assert app.conf.task_time_limit == 300
    assert app.conf.task_soft_time_limit == 240


def test_celery_autodiscover_tasks() -> None:
    assert "alpharadar.worker.tasks" in app.conf.include


def test_celery_beat_schedule_loaded() -> None:
    assert "update-prices-15min" in app.conf.beat_schedule
    assert "evaluate-alerts-5min" in app.conf.beat_schedule
    assert "analyze-sentiment-hourly" in app.conf.beat_schedule


def test_update_stock_prices_task_registered() -> None:
    from alpharadar.worker.tasks import update_stock_prices

    assert update_stock_prices is not None
    assert hasattr(update_stock_prices, "delay")


def test_evaluate_alerts_task_registered() -> None:
    from alpharadar.worker.tasks import evaluate_alerts

    assert evaluate_alerts is not None
    assert hasattr(evaluate_alerts, "delay")


def test_analyze_sentiment_task_registered() -> None:
    from alpharadar.worker.tasks import analyze_sentiment

    assert analyze_sentiment is not None
    assert hasattr(analyze_sentiment, "delay")
