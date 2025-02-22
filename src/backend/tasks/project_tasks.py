# mypy: disable-error-code="import-untyped"
import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, cast

import redis
from celery import Task
from sqlalchemy import select
from typing_extensions import ParamSpec

from src.backend.core.database import AsyncSessionLocal
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus
from src.backend.tasks import celery_app
from src.backend.tasks.debug_utils import debug_task

logger = logging.getLogger(__name__)
P = ParamSpec("P")


@celery_app.task(name="test_broker_settings")
@debug_task
def test_broker_settings() -> Dict[str, Any]:
    """
    Test Redis broker settings and authentication independently.
    Returns a dictionary with test results and diagnostics.
    """
    results: Dict[str, Any] = {  # Explicitly type hint results variable
        "status": "unknown",
        "redis_info": {},
        "connection_test": False,
        "auth_test": False,
        "diagnostics": [],  # Initialize diagnostics as a list
    }

    try:
        # Get broker URL components from Celery app
        broker_url = celery_app.conf.broker_url
        results["diagnostics"].append(
            f"Broker URL pattern: {broker_url.split('@')[0]}@..."
        )

        # Test direct Redis connection
        redis_client = cast(
            redis.Redis[Any],
            redis.Redis.from_url(
                url=broker_url,
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=5,
            ),
        )

        # Test basic connection
        if redis_client.ping():
            results["connection_test"] = True
            results["diagnostics"].append("Basic connection test (PING) successful")

        # Test authentication with credentials
        try:
            # Get credentials from URL
            credentials = broker_url.split("@")[0].split(":")
            if len(credentials) >= 3:
                username = credentials[1].split("//")[1]
                password = credentials[2]
                redis_client.execute_command("AUTH", username, password)
                results["auth_test"] = True
                results["diagnostics"].append("Authentication test successful")
        except redis.AuthenticationError as auth_err:
            results["diagnostics"].append(
                f"Authentication test failed: {str(auth_err)}"
            )
            raise

        # Get Redis info
        redis_info = redis_client.info()
        results["redis_info"] = {
            "version": redis_info.get("redis_version"),
            "clients": redis_info.get("connected_clients"),
            "memory_used": redis_info.get("used_memory_human"),
            "role": redis_info.get("role"),
            "connected_slaves": redis_info.get("connected_slaves", 0),
        }

        # Test pub/sub (important for Celery)
        pubsub = redis_client.pubsub()
        test_channel = "test_channel"
        pubsub.subscribe(test_channel)
        redis_client.publish(test_channel, "test message")
        message = pubsub.get_message(timeout=1)
        if message and message.get("type") == "subscribe":
            results["diagnostics"].append("Pub/Sub test successful")
        else:
            results["diagnostics"].append("Pub/Sub test failed or timed out")
        pubsub.unsubscribe(test_channel)

        # Overall status
        results["status"] = "success"
        logger.info("Broker settings test completed successfully")

    except redis.AuthenticationError as e:
        results["status"] = "auth_error"
        results["diagnostics"].append(f"Authentication error: {str(e)}")
        logger.error(f"Redis authentication error: {str(e)}")

    except redis.ConnectionError as e:
        results["status"] = "connection_error"
        results["diagnostics"].append(f"Connection error: {str(e)}")
        logger.error(f"Redis connection error: {str(e)}")

    except Exception as e:
        results["status"] = "error"
        results["diagnostics"].append(f"Unexpected error: {str(e)}")
        logger.exception("Unexpected error in test_broker_settings")

    finally:
        # Add current Celery configuration for debugging
        conf = celery_app.conf
        results["celery_config"] = {
            "broker_connection_retry": conf.broker_connection_retry,
            "broker_connection_max_retries": (conf.broker_connection_max_retries),
            "broker_connection_timeout": conf.broker_connection_timeout,
            "broker_heartbeat": conf.broker_heartbeat,
            "broker_pool_limit": conf.broker_pool_limit,
        }

    return results


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


@celery_app.task(name="celery_debug_task")
@debug_task
def celery_debug_task(arg1: int, arg2: int) -> int:
    """Test task that confirms celery is working."""
    return arg1 + arg2


@celery_app.task(bind=True, name="process_project")
@debug_task
def process_project(self: Task, project_id: str) -> None:
    """
    Process a project with enhanced error handling and status updates.

    Args:
        self: The Celery task instance
        project_id: The UUID of the project to process
    """
    logger.info(f"Starting process_project for project_id: {project_id}")

    # Run the async parts in an event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_process_project_async(project_id))
    finally:
        loop.close()


async def _process_project_async(project_id: str) -> None:
    """Async implementation of project processing"""
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
