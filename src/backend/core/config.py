from typing import Optional

from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Content Platform"
    API_VERSION: str = "v0.0"
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@postgres:5432/content_platform"
    )
    TEST_DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/0")
    CLERK_SECRET_KEY: Optional[str] = None
    HEYGEN_API_KEY: Optional[str] = None

    @field_validator("TEST_DATABASE_URL", mode="before")
    def set_test_database_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v:
            # If TEST_DATABASE_URL is not set, derive it from DATABASE_URL
            base_url: str = info.data.get("DATABASE_URL", "")
            return base_url.replace("content_platform", "test_content_platform")
        return v

    @field_validator("CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", mode="before")
    def set_celery_urls(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v and "REDIS_URL" in info.data:
            redis_url = info.data.get("REDIS_URL")
            if redis_url:
                return redis_url
        return v or ""

    class Config:
        env_file = ".env"


settings = Settings()
