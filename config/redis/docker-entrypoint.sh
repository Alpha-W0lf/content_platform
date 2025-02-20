#!/bin/sh
set -ex

echo "Before setting up logging directory..."
# Setup logging directory with proper permissions
echo "Setting up logging directory..."
mkdir -p /var/log/redis
echo "After mkdir /var/log/redis"
LOG_FILE="/var/log/redis/redis-debug.log"
touch "$LOG_FILE"
echo "After touch logfile"
chown -R redis:redis /var/log/redis
echo "After chown /var/log/redis"

# Create and set permissions for data directory
echo "Setting up data directory..."
mkdir -p /data
echo "After mkdir /data"
chown -R redis:redis /data
echo "After chown /data"

# Substitute environment variables in redis.conf
echo "Substituting environment variables in redis.conf..."
echo "REDIS_PASSWORD (before envsubst): $REDIS_PASSWORD"
envsubst < /redis.conf > /tmp/redis.conf
echo "After envsubst"
echo "Contents of /tmp/redis.conf (after envsubst):"
cat /tmp/redis.conf
echo "After cat /tmp/redis.conf"
mv /tmp/redis.conf /redis.conf
echo "After mv /tmp/redis.conf"
echo "Contents of /redis.conf (final):"
cat /redis.conf
echo "After cat /redis.conf"

# Check Redis binary
REDIS_SERVER="/usr/bin/redis-stack-server"
echo "Checking Redis binary at $REDIS_SERVER..."
if [ ! -x "$REDIS_SERVER" ]; then
    echo "ERROR: $REDIS_SERVER not found or not executable"
    ls -l /usr/bin/redis* || true
    ls -l /opt/redis-stack/bin/redis* || true
    exit 1
fi

echo "Before getting Redis version..."
# Log Redis version
echo "Getting Redis version..."
"$REDIS_SERVER" -v || {
    echo "ERROR: Cannot get Redis version"
    exit 1
}
echo "After getting Redis version..."

echo "Before checking Redis configuration file..."
# Check configuration file
echo "Checking Redis configuration file..."
ls -l /redis.conf || {
    echo "ERROR: /redis.conf not found"
    exit 1
}
echo "After checking Redis configuration file..."

# Log the final configuration before starting Redis
echo "Logging final Redis configuration to /var/log/redis/final_redis.conf"
cat /redis.conf > /var/log/redis/final_redis.conf
echo "After logging final Redis configuration..."
# Start Redis Stack Server with configuration
echo "Starting Redis Stack Server..."
exec "$REDIS_SERVER" /redis.conf "$@" 2>&1 | tee -a "$LOG_FILE"
sleep infinity
