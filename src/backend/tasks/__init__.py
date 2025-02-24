import logging

# Configure logging before creating the Celery app
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Create the Celery app
from celery import Celery

celery_app = Celery("content_platform")

try:
    celery_app.config_from_object(
        "celeryconfig"
    )  # Remove src.backend prefix since we're in the backend dir
    logger.debug("Celery config loaded successfully.")

    # Autodiscover tasks relative to current directory
    celery_app.autodiscover_tasks(["tasks.project_tasks"])

except ImportError as e:
    logger.error(f"Failed to import Celery config: {e}")
except Exception as e:
    logger.exception(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    celery_app.start()
