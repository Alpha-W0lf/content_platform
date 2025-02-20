#!/bin/bash
set -e

# Initialize log file
LOG_FILE="/app/celery_logs/healthcheck.log"
echo "=== Worker Health Check $(date) ===" >> $LOG_FILE

# Check Redis connection
echo "Testing Redis connection..." >> $LOG_FILE
if redis-cli -h redis -p 6379 -a "${REDIS_PASSWORD}" --no-auth-warning ping > /dev/null; then
    echo "Redis connection successful" >> $LOG_FILE
else
    echo "Redis connection failed" >> $LOG_FILE
    exit 1
fi

# Check Redis authentication
echo "Testing Redis authentication..." >> $LOG_FILE
if redis-cli -h redis -p 6379 -a "${REDIS_PASSWORD}" --no-auth-warning auth default "${REDIS_PASSWORD}" > /dev/null; then
    echo "Redis authentication successful" >> $LOG_FILE
else
    echo "Redis authentication failed" >> $LOG_FILE
    exit 1
fi

# Check Celery worker status
echo "Checking Celery worker status..." >> $LOG_FILE
if celery -A src.backend.tasks inspect ping -d celery@$HOSTNAME; then
    echo "Celery worker is responding" >> $LOG_FILE
else
    echo "Celery worker is not responding" >> $LOG_FILE
    exit 1
fi

# Print Redis info for debugging
echo "Redis server info:" >> $LOG_FILE
redis-cli -h redis -p 6379 -a "${REDIS_PASSWORD}" --no-auth-warning info | grep -E "redis_version|connected_clients|used_memory_human" >> $LOG_FILE

# Print recent task history
echo "Recent task history:" >> $LOG_FILE
celery -A src.backend.tasks inspect active -d celery@$HOSTNAME >> $LOG_FILE 2>&1

exit 0