#!/bin/bash
set -e

# Redirect all output to log file while maintaining console output
exec 1> >(tee -a /var/log/redis/startup.log) 2>&1

echo "=== Starting Redis Stack Server ==="
echo "Time: $(date)"
echo "Redis Version: $(redis-server --version)"

# Verify environment variables
echo "Checking environment variables..."
if [ -z "$REDIS_PASSWORD" ]; then
    echo "ERROR: REDIS_PASSWORD is not set"
    exit 1
fi

echo "Redis password length: ${#REDIS_PASSWORD}"
echo "Password starts with: ${REDIS_PASSWORD:0:4}..."

# Setup logging directory with proper permissions
echo "Setting up logging directory..."
mkdir -p /var/log/redis
LOG_FILE="/var/log/redis/redis-debug.log"
touch "$LOG_FILE"
chown -R root:root /var/log/redis

# Create and set permissions for data directory
echo "Setting up data directory..."
mkdir -p /data
chown -R root:root /data

# Substitute environment variables in redis.conf
echo "Substituting environment variables in redis.conf..."
envsubst < /redis.conf > /tmp/redis.conf
mv /tmp/redis.conf /redis.conf

# Test Redis configuration file
echo "Testing Redis configuration..."
echo "Starting Redis configuration test: redis-server /redis.conf --test-memory 1024"
redis-server /redis.conf --test-memory 1024 || {
    echo "ERROR: Redis configuration test failed"
    echo "Redis configuration test failed with error."
    exit 1
}
echo "Redis configuration test passed successfully."

# Initialize Redis with default user and ACL
echo "Initializing Redis ACLs..."
{
    redis-server /redis.conf --protected-mode no &
    REDIS_PID=$!
    
    # Wait for Redis to start
    echo "Waiting for Redis to start..."
    until redis-cli ping &>/dev/null; do
        sleep 1
    done
    
    echo "Setting up default user..."
    redis-cli ACL SETUSER default on ">${REDIS_PASSWORD}" ~* &* +@all || {
        echo "ERROR: Failed to set up default user"
        kill $REDIS_PID
        exit 1
    }
    
    # Verify authentication
    echo "Verifying authentication..."
    if redis-cli -a "$REDIS_PASSWORD" ping | grep -q "PONG"; then
        echo "Authentication test successful"
    else
        echo "ERROR: Authentication test failed"
        kill $REDIS_PID
        exit 1
    fi
    
    # Clean shutdown
    redis-cli shutdown
    wait $REDIS_PID
    echo "Temporary Redis instance shutdown complete."
} || exit 1

# Add delay before mv command
echo "Waiting 2 seconds before moving redis.conf..."
sleep 2

# Start Redis Stack with full configuration
echo "Starting Redis Stack Server with full configuration..."
echo "Configuration file: /redis.conf"
echo "Log file: /var/log/redis/redis.log"

# Monitor Redis logs in background
tail -f /var/log/redis/redis.log | grep --line-buffered -E "Authentication|ACL|ERROR|DENIED" &

# Start Redis Stack Server
exec redis-stack-server /redis.conf \
    --loglevel debug \
    --logfile /var/log/redis/redis.log \
    --requirepass "${REDIS_PASSWORD}" \
    --user default on "${REDIS_PASSWORD}" ~* &* +@all
