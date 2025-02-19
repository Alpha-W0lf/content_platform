#!/bin/sh
set -ex

# Setup logging directory with proper permissions
echo "Setting up logging directory..."
mkdir -p /var/log/redis
chmod 777 /var/log/redis
LOG_FILE="/var/log/redis/redis-debug.log"
touch "$LOG_FILE"
chmod 666 "$LOG_FILE"

# Create and set permissions for data directory
echo "Setting up data directory..."
mkdir -p /data
chmod 777 /data

# Substitute environment variables in redis.conf
echo "Substituting environment variables in redis.conf..."
envsubst < /redis.conf > /tmp/redis.conf
mv /tmp/redis.conf /redis.conf

# Check Redis binary
REDIS_SERVER="/usr/bin/redis-stack-server"
echo "Checking Redis binary at $REDIS_SERVER..."
if [ ! -x "$REDIS_SERVER" ]; then
    echo "ERROR: $REDIS_SERVER not found or not executable"
    ls -l /usr/bin/redis* || true
    ls -l /opt/redis-stack/bin/redis* || true
    exit 1
fi

# Log Redis version
echo "Getting Redis version..."
"$REDIS_SERVER" -v || {
    echo "ERROR: Cannot get Redis version"
    exit 1
}

# Check configuration file
echo "Checking Redis configuration file..."
ls -l /redis.conf || {
    echo "ERROR: /redis.conf not found"
    exit 1
}

# Start Redis Stack Server with configuration
echo "Starting Redis Stack Server..."
exec "$REDIS_SERVER" /redis.conf "$@" 2>&1 | tee -a "$LOG_FILE" 