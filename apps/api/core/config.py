"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ENCRYPTION_KEY: str = ""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gabopay"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Providers
    AIRTEL_BASE_URL: str = "https://openapi.airtel.africa"
    AIRTEL_CLIENT_ID: str = ""
    AIRTEL_CLIENT_SECRET: str = ""
    AIRTEL_CALLBACK_URL: str = ""

    MOOV_BASE_URL: str = "https://api.moov.africa"
    MOOV_API_KEY: str = ""
    MOOV_CALLBACK_URL: str = ""

    CINETPAY_API_KEY: str = ""
    CINETPAY_SITE_ID: str = ""

    # Dashboard auth
    JWT_SECRET: str = "jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@gabopay.ga"

    # Fees & Limits
    PLATFORM_FEE_PERCENTAGE: float = 1.5
    MIN_CHARGE_AMOUNT: int = 500
    MAX_CHARGE_AMOUNT: int = 5000000

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.APP_ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()