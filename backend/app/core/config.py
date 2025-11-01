"""
Application Configuration
Uses pydantic-settings for environment variable management
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Application
    APP_NAME: str = "GP4U"
    VERSION: str = "2.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://gp4u:password@localhost:5432/gp4u"
    DATABASE_POOL_SIZE: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Arbitrage
    ARBITRAGE_MIN_SPREAD_PCT: float = 15.0
    ARBITRAGE_CACHE_TTL: int = 30

    # Provider API Keys (optional for MVP)
    RENDER_API_KEY: str = ""
    AKASH_API_KEY: str = ""
    IONET_API_KEY: str = ""
    VASTAI_API_KEY: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Web3
    WEB3_PROVIDER_URL: str = ""
    USDC_CONTRACT_ADDRESS: str = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
