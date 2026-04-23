from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "News Aggregator API"
    database_url: str = f"sqlite:///{BASE_DIR / 'news_aggregator.db'}"
    refresh_interval_minutes: int = 10
    request_timeout_seconds: int = 15
    frontend_origin: str = "http://127.0.0.1:5173"
    news_recency_days: int = 14
    medical_feed_recency_days: int = 45
    pubmed_default_recency_days: int = 120

    model_config = SettingsConfigDict(env_prefix="NEWS_APP_", env_file=".env")


settings = Settings()
