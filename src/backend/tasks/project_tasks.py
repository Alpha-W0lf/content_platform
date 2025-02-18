# mypy: disable-error-code="import-untyped"
import logging
from typing import Any  # noqa: F401

from typing_extensions import ParamSpec

from src.backend.models.project import Project  # noqa: F401
from src.backend.schemas.project import ProjectStatus  # noqa: F401
from src.backend.tasks import celery_app

P = ParamSpec("P")

logger = logging.getLogger(__name__)


@celery_app.task(name="test_task")
def test_task(x: int, y: int) -> int:
    """A test task that adds two numbers.

    Args:
        x: First number to add
        y: Second number to add

    Returns:
        The sum of x and y
    """
    logger.debug(f"test_task called with x={x}, y={y}")
    result = x + y
    logger.debug(f"test_task result: {result}")
    return result


@celery_app.task(bind=True)
def process_project(self, project_id: str) -> None:
    """
    Process a project asynchronously.
    Args:
        self: The Celery task instance
        project_id: The UUID of the project to process
    """
    logger.debug(f"process_project called with project_id={project_id}")
    # Unused imports are kept because they will be used in the TODO implementation
    # TODO: Implement actual project processing logic
    pass
