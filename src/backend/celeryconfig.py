# src/backend/celeryconfig.py
import logging

# Use localhost without authentication for testing.
broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/0"

# Basic logging configuration (adjust as needed).
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Rest of your Celery configuration --- (Keep other settings as before)
# Connection settings
broker_connection_retry = True
broker_connection_retry_on_startup = True
broker_connection_max_retries = 10
broker_connection_timeout = 30
broker_heartbeat = 10
broker_pool_limit = 10

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
