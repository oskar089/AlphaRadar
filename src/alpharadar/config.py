from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/alpharadar"
    redis_url: str = "redis://localhost:6379"

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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
