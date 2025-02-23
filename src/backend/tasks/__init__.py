import logging

from celery import Celery

# Configure logging.  Best practice is to do this *before* creating the Celery app.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Or your preferred level
handler = logging.StreamHandler()  # Log to console
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


celery_app = Celery("content_platform")

try:
    celery_app.config_from_object("src.backend.celeryconfig")
    logger.debug("Celery config loaded successfully.")

    # Autodiscover tasks
    celery_app.autodiscover_tasks(["src.backend.tasks.project_tasks"])  # Correct path

except ImportError as e:
    logger.error(f"Failed to import Celery config: {e}")
except Exception as e:
    logger.exception(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    celery_app.start()
