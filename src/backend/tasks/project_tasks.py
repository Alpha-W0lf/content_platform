# mypy: disable-error-code="import-untyped"
import logging
import sys
from typing import Any  # noqa: F401

import redis
from typing_extensions import ParamSpec

from src.backend.models.project import Project  # noqa: F401
from src.backend.schemas.project import ProjectStatus  # noqa: F401
from src.backend.tasks import celery_app

print("Loading project_tasks.py")

P = ParamSpec("P")

logger = logging.getLogger(__name__)


@celery_app.task(name="redis_interaction_test")
def redis_interaction_test() -> str:
    """
    A simple task to test Redis interaction.
    """
    logger.debug("redis_interaction_test called")
    try:
        r = redis.Redis(
            host="redis",
            port=6379,
            db=0,
            password=celery_app.conf.broker_transport_options.get(
                "password"
            ),  # Use password from Celery config
        )
        logger.debug("Redis connection established")
        r.set("testkey", "testvalue")
        logger.debug("Set key 'testkey' to 'testvalue'")
        value = r.get("testkey")
        logger.debug(f"Got value for 'testkey': {value}")
        return value.decode("utf-8") if value else "None"
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        return "Error"
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return "Error"


@celery_app.task(name="test_task")
def test_task(x: int, y: int) -> int:
    """A test task that adds two numbers."""
    logger.debug(f"test_task called with x={x}, y={y}")
    logger.info(f"sys.path: {sys.path}")  # Print sys.path
    result = x + y
    logger.debug(f"test_task result: {result}")
    return result


@celery_app.task(bind=True, name="process_project")
def process_project(self, project_id: str) -> None:
    """
    Process a project asynchronously.
    """
    logger.debug(f"process_project called with project_id={project_id}")
    logger.debug(f"Task ID: {self.request.id}")
    # Unused imports are kept because they will be used in the TODO implementation
    # TODO: Implement actual project processing logic
    pass
