from celery import Celery
import logging

from src.backend.core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

celery_app = Celery("content_platform")
celery_app.config_from_object(settings)

logger.debug(f"Celery broker URL: {celery_app.conf.broker_url}")
logger.debug(f"Celery result backend: {celery_app.conf.result_backend}")


if __name__ == "__main__":
    celery_app.start()
