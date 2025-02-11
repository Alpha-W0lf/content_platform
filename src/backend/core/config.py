from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Content Platform"
    API_VERSION: str = "v0.0"
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CLERK_SECRET_KEY: Optional[str] = None
    HEYGEN_API_KEY: Optional[str] = None
    REDIS_URL: Optional[str] = None

    @field_validator('CELERY_BROKER_URL', 'CELERY_RESULT_BACKEND', mode='before')
    def set_celery_urls(cls, v, info):
        # Get the field being validated
        field_name = info.field_name
        # Get current field values
        field_values = info.data
        
        if 'REDIS_URL' in field_values and field_values['REDIS_URL']:
            return field_values['REDIS_URL']
        return v

    class Config:
        env_file = ".env"

settings = Settings()
