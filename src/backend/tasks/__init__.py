from celery import Celery

from src.backend.core.config import settings

celery_app = Celery("content_platform")
celery_app.config_from_object(settings)

if __name__ == "__main__":
    celery_app.start()
