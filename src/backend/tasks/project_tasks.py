# mypy: disable-error-code="import-untyped"
import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

import redis
from sqlalchemy import select
from typing_extensions import ParamSpec

from src.backend.core.database import AsyncSessionLocal
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus
from src.backend.tasks import celery_app
from src.backend.tasks.debug_utils import debug_task

logger = logging.getLogger(__name__)
P = ParamSpec("P")


@celery_app.task(name="redis_interaction_test")
@debug_task
def redis_interaction_test() -> str:
    """A task to test Redis interaction with enhanced debugging."""
    try:
        # Get Redis configuration from environment
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_url = os.getenv("CELERY_BROKER_URL")

        logger.debug(
            "Attempting Redis connection with URL pattern: "
            f"{redis_url and redis_url.split('@')[0] + '@...'}"
        )
        logger.debug(
            f"Redis password length: {len(redis_password) if redis_password else 0}"
        )

        # Try direct Redis connection
        r = redis.Redis(
            host="redis",
            port=6379,
            db=0,
            password=redis_password,
            username="default",
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
        )

        # Test connection with PING
        if not r.ping():
            raise redis.ConnectionError("Redis PING failed")

        # Try basic operations
        test_key = f"test:connection:{datetime.utcnow().isoformat()}"
        r.set(test_key, "testvalue", ex=60)  # 60 second expiry
        value = r.get(test_key)
        logger.info(f"Redis test successful - Key: {test_key}, Value: {value}")

        # Get Redis info for debugging
        redis_info = r.info()
        logger.debug(f"Redis version: {redis_info.get('redis_version')}")
        logger.debug(f"Connected clients: {redis_info.get('connected_clients')}")
        logger.debug(f"Used memory: {redis_info.get('used_memory_human')}")

        return "Success"

    except redis.AuthenticationError as e:
        logger.error(f"Redis authentication failed: {str(e)}")
        url_pattern = redis_url and redis_url.split("@")[0] + "@..."
        pwd_start = redis_password[:4] + "..." if redis_password else None
        logger.debug(
            "Redis connection details for debugging:",
            extra={
                "redis_url_pattern": url_pattern,
                "password_length": len(redis_password) if redis_password else 0,
                "password_starts_with": pwd_start,
            },
        )
        return f"Auth Error: {str(e)}"
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {str(e)}")
        return f"Connection Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Unexpected error in redis_interaction_test: {str(e)}")
        return f"Error: {str(e)}"


@celery_app.task(name="test_task")
@debug_task
def test_task(x: int, y: int) -> int:
    """A test task that adds two numbers."""
    logger.debug(f"test_task called with x={x}, y={y}")
    result = x + y
    logger.debug(f"test_task result: {result}")
    return result


@celery_app.task(bind=True, name="process_project")
@debug_task
async def process_project(self, project_id: str) -> None:
    """
    Process a project asynchronously with enhanced error handling and status updates.

    Args:
        self: The Celery task instance
        project_id: The UUID of the project to process
    """
    logger.info(f"Starting process_project for project_id: {project_id}")
    project: Optional[Project] = None

    # Create a new database session for this task
    async with AsyncSessionLocal() as db:
        try:
            # Get the project
            result = await db.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()

            if project is None:
                logger.error(f"Project not found: {project_id}")
                return

            # Update to PROCESSING
            project.status = ProjectStatus.PROCESSING
            await db.commit()
            await db.refresh(project)
            logger.info(f"Project {project_id} status updated to PROCESSING")

            # Simulate work (replace with actual processing)
            await asyncio.sleep(5)

            # Update to COMPLETED
            project.status = ProjectStatus.COMPLETED
            await db.commit()
            logger.info(f"Project {project_id} status updated to COMPLETED")

        except Exception as e:
            logger.exception(f"Error processing project {project_id}: {str(e)}")
            await db.rollback()

            if project:
                try:
                    project.status = ProjectStatus.ERROR
                    await db.commit()
                    logger.info(f"Project {project_id} status updated to ERROR")
                except Exception as commit_error:
                    logger.exception(
                        f"Failed to update project status to ERROR: {str(commit_error)}"
                    )

            # Re-raise the exception for Celery
            raise
