# mypy: disable-error-code="import-untyped"
from celery import Celery

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
