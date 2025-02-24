import os
from typing import Optional

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Content Platform"
    API_VERSION: str = "v0.0"
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://tom:password@localhost:5432/content_platform"
    )
    TEST_DATABASE_URL: str = Field(
        default="postgresql+asyncpg://tom:password@localhost:5432/test_content_platform"
    )
    # No default for REDIS_PASSWORD. It MUST be in .env or explicitly set.
    REDIS_PASSWORD: Optional[str] = Field(None)
    # For local development, we *expect* to be using localhost.
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    CLERK_SECRET_KEY: Optional[str] = None  # Optional, but good practice

    # These are *FRONTEND* variables.  They do NOT belong in the backend config.
    # next_public_clerk_publishable_key: Optional[str] = None
    # next_public_api_url: Optional[str] = None
    # next_public_clerk_sign_in_url: Optional[str] = None
    # next_public_clerk_sign_up_url: Optional[str] = None
    # next_public_clerk_after_sign_in_url: Optional[str] = None
    # next_public_clerk_after_sign_up_url: Optional[str] = None

    # Same with these - they should be in .env.local in the frontend
    # heygen_email: Optional[str] = None
    # heygen_password: Optional[str] = None

    @field_validator("CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", mode="before")
    def set_celery_urls(cls, v: Optional[str], info: ValidationInfo) -> str:
        if v:
            return v  # Use provided value if it exists

        # Get REDIS_URL from environment or default to localhost without authentication
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        return str(redis_url)

    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env in the *current* directory
        env_file_encoding="utf-8",
        extra="allow",  # Allow extra environment variables (good practice)
    )


settings = Settings()  # type: ignore[call-arg]
