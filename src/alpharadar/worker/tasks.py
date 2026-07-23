"""Celery task stubs for AlphaRadar."""

from typing import Any

from alpharadar.worker.celery_app import app


@app.task  # type: ignore[untyped-decorator]
def update_stock_prices(symbols: list[str]) -> dict[str, Any]:
    """Update stock prices for given symbols."""
    return {"status": "stub", "symbols": symbols}


@app.task  # type: ignore[untyped-decorator]
def evaluate_alerts() -> dict[str, str]:
    """Evaluate alerts for all monitored stocks."""
    return {"status": "stub"}


@app.task  # type: ignore[untyped-decorator]
def analyze_sentiment(symbols: list[str]) -> dict[str, Any]:
    """Analyze sentiment for given symbols."""
    return {"status": "stub", "symbols": symbols}
