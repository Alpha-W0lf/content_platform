from celery import Celery

# Initialize Celery app
celery = Celery("content_platform")

# Load Celery config
celery.config_from_object("src.backend.celeryconfig")

# Optional: Add any task modules here
celery.autodiscover_tasks(["src.backend.tasks"])
