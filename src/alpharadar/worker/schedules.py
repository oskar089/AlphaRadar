"""Celery beat schedule for periodic tasks."""

from celery.schedules import crontab

beat_schedule = {
    "update-prices-15min": {
        "task": "alpharadar.worker.tasks.update_stock_prices",
        "schedule": crontab(minute="*/15", hour="9-16", day_of_week="1-5"),
        "args": (["AAPL", "GOOGL", "MSFT"],),
    },
    "evaluate-alerts-5min": {
        "task": "alpharadar.worker.tasks.evaluate_alerts",
        "schedule": crontab(minute="*/5", hour="9-16", day_of_week="1-5"),
    },
    "analyze-sentiment-hourly": {
        "task": "alpharadar.worker.tasks.analyze_sentiment",
        "schedule": crontab(minute=0, hour="9-16", day_of_week="1-5"),
        "args": (["AAPL", "GOOGL", "MSFT"],),
    },
}
