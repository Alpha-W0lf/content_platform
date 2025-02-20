import logging
from typing import Any, Dict, cast

import redis

from src.backend.tasks import celery_app
from src.backend.tasks.debug_utils import debug_task

logger = logging.getLogger(__name__)


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
