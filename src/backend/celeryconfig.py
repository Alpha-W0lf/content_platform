broker_url = 'redis://redis:6379/0'
result_backend = 'redis://redis:6379/0'
broker_connection_retry_on_startup = True  # Add this to handle the deprecation warning
broker_connection_retry = True  # Keep existing behavior

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True

worker_prefetch_multiplier = 1  # Prevent worker from prefetching multiple tasks
worker_max_tasks_per_child = 10  # Restart worker after 10 tasks to prevent memory leaks