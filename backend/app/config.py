"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Argus"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "sqlite:///./argus.db"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = True

    # Cache TTLs (seconds)
    cache_ttl_quote: int = 300  # 5 minutes
    cache_ttl_ohlcv_daily: int = 3600  # 1 hour
    cache_ttl_ohlcv_weekly: int = 86400  # 24 hours
    cache_ttl_indicators: int = 300  # 5 minutes
    cache_ttl_screener: int = 300  # 5 minutes
    cache_ttl_universe: int = 86400  # 24 hours
    cache_ttl_off_hours_multiplier: int = 12  # Multiply TTL when market closed

    # Market Data
    market_data_timeout: int = 30
    market_data_max_retries: int = 3

    # Scheduler
    scheduler_enabled: bool = True
    refresh_interval_minutes: int = 5

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
