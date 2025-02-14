from celery import Celery
from src.backend.core.config import settings

celery = Celery(
    "content_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['src.backend.tasks.project_tasks']
)

# Optional configurations
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

if __name__ == '__main__':
    celery.start()