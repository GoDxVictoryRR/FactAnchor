import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration. All fields validated on startup."""

    # PostgreSQL
    POSTGRES_HOST: str = Field(default="pgbouncer", description="DB host (via pgBouncer)")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="factanchor")
    POSTGRES_USER: str = Field(default="factanchor_app")
    POSTGRES_PASSWORD: str = Field(default="CHANGE_ME_STRONG_PASSWORD")
    DATABASE_URL: Optional[str] = Field(default=None)
    DATABASE_URL_SYNC: Optional[str] = Field(default=None)

    # RabbitMQ
    RABBITMQ_URL: str = Field(default="amqp://guest:guest@rabbitmq:5672//")

    # Redis
    REDIS_URL: str = Field(default="redis://redis:6379/0")

    # Pinecone
    PINECONE_API_KEY: str = Field(default="CHANGE_ME")
    PINECONE_INDEX_NAME: str = Field(default="factanchor-claims")
    PINECONE_ENVIRONMENT: str = Field(default="us-east-1-aws")

    # LLM
    LLM_PROVIDER: str = Field(default="anthropic")
    LLM_MODEL: str = Field(default="claude-opus-4-6")
    LLM_API_KEY: str = Field(default="CHANGE_ME")
    LLM_MAX_TOKENS: int = Field(default=1024)

    # Auth
    JWT_SECRET_KEY: str = Field(default="CHANGE_ME_256_BIT_RANDOM_HEX")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRY_MINUTES: int = Field(default=60)
    API_KEY_HEADER: str = Field(default="X-FactAnchor-Key")

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_BURST: int = Field(default=10)

    # Initial Admin (Production Identity Management)
    INITIAL_ADMIN_EMAIL: Optional[str] = Field(default=None)
    INITIAL_ADMIN_PASSWORD: Optional[str] = Field(default=None)

    APP_ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    CORS_ORIGINS: str = Field(default="http://localhost:3000,https://fact-anchor.vercel.app")
    BACKEND_URL: str = Field(default="https://factanchor-api.onrender.com")

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            # Automatic conversion from direct postgres:// to asyncpg if needed
            url = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            return url.replace("+asyncpg+asyncpg", "+asyncpg") # Prevent double-injection
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        if self.DATABASE_URL_SYNC:
            return self.DATABASE_URL_SYNC
        if self.DATABASE_URL:
             return self.DATABASE_URL.replace("+asyncpg", "")
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
