from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_JWT_SECRET = "dev-only-secret-change-me-0123456789abcdef"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"
    log_json: bool = False
    database_url: str = "postgresql+asyncpg://todo:todo@localhost:5432/todo"
    db_use_nullpool: bool = False  # True when talking to PgBouncer
    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_max_overflow: int = Field(default=5, ge=0, le=100)
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_redis_url: str = "redis://localhost:6379/1"
    celery_broker_url: str = "redis://localhost:6379/2"
    jwt_secret: SecretStr = Field(default=SecretStr(DEV_JWT_SECRET), min_length=32)
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_expires_minutes: int = Field(default=60, ge=5, le=1440)
    rate_limit_per_minute: int = Field(default=120, ge=1)
    login_rate_limit_per_minute: int = Field(default=10, ge=1)
    list_cache_ttl_seconds: int = Field(default=30, ge=1, le=3600)
    trust_proxy_headers: bool = False

    @model_validator(mode="after")
    def _prod_needs_real_secret(self) -> "Settings":
        if self.env == "prod" and self.jwt_secret.get_secret_value() == DEV_JWT_SECRET:
            raise ValueError("JWT_SECRET must be set in prod")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
