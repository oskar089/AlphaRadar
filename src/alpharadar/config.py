from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = (
        "postgresql+asyncpg://alpharadar:alpharadar@localhost:5432/alpharadar"
    )
    redis_url: str = "redis://localhost:6379/0"
    portfolio_persistence: str = "memory"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # API Keys
    yahoo_finance_api_key: str = ""
    alpha_vantage_api_key: str = ""
    telegram_bot_token: str = ""

    # Analysis weights
    weight_technical: float = 0.4
    weight_fundamental: float = 0.4
    weight_sentiment: float = 0.2

    # Thresholds
    buy_threshold: float = 70.0
    sell_threshold: float = 30.0

    # Scheduler intervals (seconds)
    price_update_interval: int = 900  # 15 min
    fundamental_update_interval: int = 86400  # 24h
    news_update_interval: int = 1800  # 30 min

    # Notification
    email_enabled: bool = False
    telegram_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_recommendation_weights(self) -> Self:
        if self.weight_technical + self.weight_fundamental <= 0.0:
            raise ValueError(
                "weight_technical + weight_fundamental must be greater than zero "
                "for deterministic sentiment fallback"
            )
        return self


settings = Settings()
