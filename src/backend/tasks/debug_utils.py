import logging
import os
from functools import wraps
from typing import cast  # Import cast moved to its own line
from typing import Any, Callable, Dict, Optional, ParamSpec, TypeVar

import redis
from celery import Task  # Import Task from celery
from celery.signals import (
    after_setup_logger,
    before_task_publish,
    task_failure,
    task_postrun,
    task_prerun,
    worker_process_init,
    worker_ready,
)

logger = logging.getLogger("celery.tasks.debug")


def setup_task_logger(loglevel: int = logging.DEBUG) -> None:
    """Configure task-specific logger"""
    handler = logging.FileHandler("/app/celery_logs/worker.log")
    handler.setLevel(loglevel)
    formatter = logging.Formatter(
        "[%(asctime)s: %(levelname)s/%(processName)s] "
        "[%(task_name)s(%(task_id)s)] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(loglevel)


@after_setup_logger.connect
def setup_loggers(logger: Any, *args: Any, **kwargs: Any) -> None:
    setup_task_logger()


P = ParamSpec("P")
R = TypeVar("R")


def debug_task(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to add debug logging to Celery tasks"""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        celery_task: Task[Any, Any] = cast(  # Type hint and cast for celery_task
            Task[Any, Any], args[0]
        )
        task_info = (
            f"Task {celery_task.name}[{celery_task.request.id}] - "
            f"Started execution with args: {args[1:]}, kwargs: {kwargs}"
        )
        logger.debug(task_info)

        try:
            # Test Redis connection before task execution
            redis_url = os.getenv("CELERY_BROKER_URL", "")  # Default to empty string
            if not redis_url:
                raise ValueError("CELERY_BROKER_URL not set")

            redis_client = redis.from_url(redis_url)
            redis_client.ping()
            logger.debug(
                "Redis connection test successful for task " + celery_task.name
            )
        except Exception as e:
            logger.error(
                f"Redis connection test failed for task {celery_task.name}: {str(e)}"
            )
            raise

        result = func(*args, **kwargs)
        logger.debug(
            f"Task {celery_task.name}[{celery_task.request.id}] - "
            f"Completed successfully with result: {result}"
        )
        return result

    return wrapper


@worker_ready.connect
def on_worker_ready(**kwargs: Any) -> None:
    logger.info("Celery worker is ready")
    # Test Redis connection
    try:
        redis_url = os.getenv("CELERY_BROKER_URL", "")  # Default to empty string
        if not redis_url:
            raise ValueError("CELERY_BROKER_URL not set")

        redis_client = redis.from_url(redis_url)
        redis_info = redis_client.info()
        logger.info(
            "Redis connection test successful. "
            f"Server version: {redis_info.get('redis_version')}"
        )
    except Exception as e:
        logger.error(f"Redis connection test failed on worker startup: {str(e)}")


@worker_process_init.connect
def on_worker_init(**kwargs: Any) -> None:
    logger.info("Initializing worker process")
    redis_password = os.getenv("REDIS_PASSWORD", "")
    broker_url = os.getenv("CELERY_BROKER_URL", "")
    logger.debug(f"Redis password length: {len(redis_password)}")
    logger.debug(f"Redis URL format check: {'redis://' in broker_url}")


@task_failure.connect
def on_task_failure(
    sender: Optional[Any] = None,
    task_id: Optional[str] = None,
    exception: Optional[Exception] = None,
    args: Optional[tuple[Any, ...]] = None,
    kwargs: Optional[dict[str, Any]] = None,
    **kwds: Any,
) -> None:
    if sender and task_id:
        error_msg = (
            f"Task {sender.name}[{task_id}] failed: {exception}\n"
            f"Args: {args}\nKwargs: {kwargs}"
        )
        logger.error(error_msg)


@before_task_publish.connect
def on_task_publish(
    sender: Optional[Any] = None,
    headers: Optional[Dict[Any, Any]] = None,
    **kwargs: Any,
) -> None:
    if sender and headers:
        logger.debug(f"Publishing task {sender}: {headers.get('id')}")


@task_prerun.connect
def on_task_prerun(
    task_id: Optional[str] = None, task: Optional[Any] = None, *args: Any, **kwargs: Any
) -> None:
    if task and task_id:
        logger.debug(
            f"Task {task.name}[{task_id}] - "
            f"About to run with args: {args}, kwargs: {kwargs}"
        )


@task_postrun.connect
def on_task_postrun(
    task_id: Optional[str] = None,
    task: Optional[Any] = None,
    retval: Any = None,
    state: Optional[str] = None,
    *args: Any,
    kwargs: Optional[dict[str, Any]] = None,
) -> None:
    if task and task_id:
        logger.debug(
            f"Task {task.name}[{task_id}] - Completed with "
            f"state: {state}, result: {retval}"
        )
