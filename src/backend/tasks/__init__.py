from celery import Celery

celery = Celery("content_platform", include=["src.backend.tasks.project_tasks"])

# Load the configuration from the celeryconfig module
celery.config_from_object("src.backend.celeryconfig")

if __name__ == "__main__":
    celery.start()
