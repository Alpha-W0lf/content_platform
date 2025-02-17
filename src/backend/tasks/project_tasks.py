# mypy: disable-error-code="import-untyped"
from typing import Any  # noqa: F401

from celery import Celery, shared_task
from celery.app.task import Task
from typing_extensions import ParamSpec

from src.backend.models.project import Project  # noqa: F401
from src.backend.schemas.project import ProjectStatus  # noqa: F401

P = ParamSpec("P")

celery = Celery(
    "project_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)


@celery.task(name="test_task")
def test_task(x: int, y: int) -> int:
    """A test task that adds two numbers.

    Args:
        x: First number to add
        y: Second number to add

    Returns:
        The sum of x and y
    """
    return x + y


@shared_task(bind=True)
def process_project(self: Task[P, None], project_id: str) -> None:
    """
    Process a project asynchronously.
    Args:
        self: The Celery task instance
        project_id: The UUID of the project to process
    """
    # Unused imports are kept because they will be used in the TODO implementation
    # TODO: Implement actual project processing logic
    pass
