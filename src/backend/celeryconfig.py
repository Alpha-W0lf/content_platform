import logging
import os
from typing import Any

import redis
from celery.signals import celeryd_after_setup


def validate_env(var_name: str, var_type: type) -> Any:
    """Validate and cast environment variable to specified type."""
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"{var_name} environment variable is required")
    return value


# Redis connection settings with enhanced validation - TEST
REDIS_PASSWORD = validate_env("REDIS_PASSWORD", str)

# Construct broker and backend URLs with explicit username
broker_url = f"redis://default:{REDIS_PASSWORD}@redis:6379/0"
result_backend = f"redis://default:{REDIS_PASSWORD}@redis:6379/0"

# Connection settings
broker_connection_retry = True
broker_connection_retry_on_startup = True
broker_connection_max_retries = 10
broker_connection_timeout = 30
broker_heartbeat = 10
broker_pool_limit = 10


# Redis connection test on worker startup
@celeryd_after_setup.connect
def test_redis_connection(sender: Any, instance: Any, **kwargs: Any) -> None:
    logger = logging.getLogger("celery.tasks")
    try:
        redis_client = redis.Redis(
            host="redis",
            port=6379,
            db=0,
            username="default",
            password=REDIS_PASSWORD,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        redis_info = redis_client.info()
        version_info = redis_info.get("redis_version", "unknown")
        logger.info(
            "Redis connection test successful on worker startup. "
            f"Version: {version_info}"
        )
    except redis.AuthenticationError as e:
        logger.error(f"Redis authentication failed on worker startup: {str(e)}")
        # Safe to use len() since we validated REDIS_PASSWORD is not None
        logger.debug(
            "Redis connection details - "
            f"Password length: {len(REDIS_PASSWORD)}, "
            f"URL pattern: {broker_url.split('@')[0]}@..."
        )
        raise
    except redis.ConnectionError as e:
        logger.error(f"Redis connection failed on worker startup: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected Redis error on worker startup: {str(e)}")
        raise


# Enhanced logging configuration
worker_hijack_root_logger = True  # Changed to True to properly handle redirected logs
worker_log_color = True
worker_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s] [%(name)s] %(message)s"
)
worker_task_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s] "
    "[%(task_id)s] [%(name)s] "
    "%(message)s"
)

# Debug logging setup
logging.basicConfig(level=logging.DEBUG, format=worker_log_format)
logger = logging.getLogger("celery")
logger.setLevel(logging.DEBUG)

# Prevent duplicate logging
for handler in logging.root.handlers:
    handler.addFilter(lambda record: record.name != "celery")

# Print connection details for debugging
print(f"Celery broker URL pattern: {broker_url.split('@')[0]}@...")
print(f"Celery result backend URL pattern: {result_backend.split('@')[0]}@...")
print(f"Redis password length: {len(REDIS_PASSWORD)}")
print("Redis user: default")  # Removed unnecessary f-string

# Task execution settings
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
enable_utc = True
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 10

# Task routing and queue settings
task_default_queue = "default"
task_queues = {
    "default": {
        "exchange": "default",
        "routing_key": "default",
    }
}

# Additional task settings
task_track_started = True
task_time_limit = 900  # 15 minutes
task_soft_time_limit = 600  # 10 minutes
worker_send_task_events = True
task_send_sent_event = True

# Redis visibility settings
broker_transport_options = {"visibility_timeout": 43200}  # 12 hours

# Error handling settings
task_reject_on_worker_lost = True
task_acks_late = True
