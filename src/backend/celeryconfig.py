broker_url = "redis://:password@redis:6379/0"
result_backend = "redis://:password@redis:6379/0"
broker_connection_retry_on_startup = True
broker_connection_retry = True
broker_connection_max_retries = 10  # Add max retries
broker_connection_timeout = 30  # Add timeout in seconds

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
enable_utc = True

worker_prefetch_multiplier = 1  # Prevent worker from prefetching multiple tasks
worker_max_tasks_per_child = 10  # Restart worker after 10 tasks to prevent memory leaks
