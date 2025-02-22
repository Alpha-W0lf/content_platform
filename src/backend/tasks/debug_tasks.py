# mypy: disable-error-code="import-untyped"
import logging

from src.backend.tasks import celery_app
from src.backend.tasks.debug_utils import debug_task

logger = logging.getLogger(__name__)


@celery_app.task(name="celery_debug_task")
@debug_task
def celery_debug_task(arg1: int, arg2: int) -> int:
    """Test task that confirms celery is working."""
    return arg1 + arg2
