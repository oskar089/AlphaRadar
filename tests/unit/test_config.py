from pathlib import Path

import pytest
from pydantic import ValidationError

from alpharadar.config import Settings


def test_env_example_loads_with_application_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "DATABASE_URL",
        "REDIS_URL",
        "YAHOO_FINANCE_API_KEY",
        "ALPHA_VANTAGE_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "WEIGHT_TECHNICAL",
        "WEIGHT_FUNDAMENTAL",
        "WEIGHT_SENTIMENT",
        "BUY_THRESHOLD",
        "SELL_THRESHOLD",
        "EMAIL_ENABLED",
        "TELEGRAM_ENABLED",
    ):
        monkeypatch.delenv(name, raising=False)

    env_example = Path(__file__).parents[2] / ".env.example"

    loaded = Settings(_env_file=env_example)

    assert loaded.database_url == "postgresql+asyncpg://alpharadar:@localhost:5432/alpharadar"
    assert loaded.redis_url == "redis://:@localhost:6379"
    assert loaded.weight_technical == 0.4


def test_settings_reject_zero_fallback_weights() -> None:
    with pytest.raises(
        ValidationError,
        match=r"weight_technical \+ weight_fundamental must be greater than zero",
    ):
        Settings(
            weight_technical=0.0,
            weight_fundamental=0.0,
            weight_sentiment=1.0,
        )


def test_settings_has_portfolio_persistence_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PORTFOLIO_PERSISTENCE", raising=False)
    settings = Settings()
    assert hasattr(settings, "portfolio_persistence")
    assert settings.portfolio_persistence == "memory"


def test_settings_portfolio_persistence_memory() -> None:
    settings = Settings(portfolio_persistence="memory")
    assert settings.portfolio_persistence == "memory"


def test_settings_portfolio_persistence_postgresql() -> None:
    settings = Settings(portfolio_persistence="postgresql")
    assert settings.portfolio_persistence == "postgresql"


def test_settings_has_celery_broker_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CELERY_BROKER_URL", raising=False)
    settings = Settings()
    assert hasattr(settings, "celery_broker_url")
    assert "redis" in settings.celery_broker_url


def test_settings_has_celery_result_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CELERY_RESULT_BACKEND", raising=False)
    settings = Settings()
    assert hasattr(settings, "celery_result_backend")
    assert "redis" in settings.celery_result_backend


def test_settings_database_url_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(_env_file=None)
    assert settings.database_url == "postgresql+asyncpg://alpharadar:alpharadar@localhost:5432/alpharadar"


def test_settings_redis_url_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("REDIS_URL", raising=False)
    settings = Settings(_env_file=None)
    assert settings.redis_url == "redis://localhost:6379/0"
