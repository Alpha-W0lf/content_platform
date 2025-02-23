from typing import Optional

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Content Platform"
    API_VERSION: str = "v0.0"
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://tom:@127.0.0.1:5432/content_platform"
    )
    TEST_DATABASE_URL: str = Field(default="postgresql+asyncpg://testuser:testpass@localhost:5432/test_content_platform")
    REDIS_PASSWORD: str = Field(default="testpassword")

    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/0")
    CLERK_SECRET_KEY: Optional[str] = None
    HEYGEN_API_KEY: Optional[str] = None

    # Add Clerk public configurations
    next_public_clerk_publishable_key: Optional[str] = None
    next_public_api_url: Optional[str] = None
    next_public_clerk_sign_in_url: Optional[str] = None
    next_public_clerk_sign_up_url: Optional[str] = None
    next_public_clerk_after_sign_in_url: Optional[str] = None
    next_public_clerk_after_sign_up_url: Optional[str] = None

    # Add Heygen credentials
    heygen_email: Optional[str] = None
    heygen_password: Optional[str] = None

    @field_validator("CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", mode="before")
    def set_celery_urls(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v and "REDIS_URL" in info.data:
            redis_url = info.data.get("REDIS_URL")
            if redis_url is not None:
                return str(redis_url)
        return v or ""

    model_config = {
        "extra": "allow", # This will allow extra fields in the environment variables
        "env_file": "../.env",
    }


settings = Settings()
