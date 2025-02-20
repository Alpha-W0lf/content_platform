import logging
import os
import sys

from celery import Celery

print("Loading __init__.py in src/backend/tasks")
print(f"__file__: {__file__}")
print(f"Current working directory: {os.getcwd()}")
print(f"sys.path: {sys.path}")


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log the file path and additional environment variables
logger.debug(f"__file__: {__file__}")
logger.debug(f"REDIS_PASSWORD (before Celery init): {os.getenv('REDIS_PASSWORD')}")

# Log current working directory
logger.debug(f"Current working directory: {os.getcwd()}")


celery_app = Celery("content_platform")


try:
    celery_app.config_from_object("src.backend.celeryconfig")
    logger.debug("Celery config loaded successfully.")
    logger.debug(f"Celery broker URL: {celery_app.conf.broker_url}")
    logger.debug(f"Celery result backend: {celery_app.conf.result_backend}")

    # Log Redis-related environment variables (again, after config load)
    logger.debug(f"REDIS_PASSWORD (after Celery init): {os.getenv('REDIS_PASSWORD')}")
    logger.debug(f"REDIS_URL (from .env.backend): {os.getenv('REDIS_URL')}")

    # Autodiscover tasks
    celery_app.autodiscover_tasks(["src.backend.tasks.project_tasks"])


except ImportError as e:
    logger.error(f"Failed to import Celery config: {e}")
except Exception as e:
    logger.exception(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    celery_app.start()
