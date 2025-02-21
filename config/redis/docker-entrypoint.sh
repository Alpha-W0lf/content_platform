#!/bin/bash
set -e

# Enable debug mode for more verbose output
set -x

# Redirect all output to log file while maintaining console output
exec 1> >(tee -a /var/log/redis/startup.log) 2>&1

echo "=== Starting Redis Stack Server ==="
echo "Time: $(date)"
echo "Redis Version: $(redis-server --version)"

# Debug: List mounted volumes and file permissions
echo "=== Mounted Volumes and Permissions ==="
df -h | grep redis
ls -la / | grep redis
ls -la /redis.conf || echo "redis.conf not found in root"
ls -la /tmp || echo "tmp directory not accessible"

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
echo "=== Redis Configuration Processing ==="
echo "Substituting environment variables in redis.conf..."
echo "Checking redis.conf read permissions:"
ls -l /redis.conf

echo "Checking redis.conf current contents (first 15 lines):"
head -n 15 /redis.conf

echo "Verifying environment variable substitution..."
echo "REDIS_PASSWORD length: ${#REDIS_PASSWORD}"
echo "envsubst version: $(envsubst --version)"

# Instead of moving, we'll copy the contents directly
echo "=== Updating Redis Configuration ==="
echo "Creating temporary config..."
envsubst < /redis.conf > /tmp/redis.conf.tmp || {
    echo "ERROR: Failed to create temporary config. Details:"
    echo "envsubst exit code: $?"
    echo "tmp directory permissions:"
    ls -la /tmp
    exit 1
}

echo "Verifying temporary config (first 15 lines):"
head -n 15 /tmp/redis.conf.tmp

echo "Updating main config..."
cat /tmp/redis.conf.tmp > /redis.conf || {
    echo "ERROR: Failed to update redis.conf. Details:"
    echo "Source file size: $(stat -f%z /tmp/redis.conf.tmp)"
    echo "Target file permissions:"
    ls -la /redis.conf
    echo "Target directory permissions:"
    ls -la $(dirname /redis.conf)
    echo "Current working directory: $(pwd)"
    echo "File systems:"
    df -h
    exit 1
}

echo "=== Final Configuration Verification ==="
echo "Checking final redis.conf contents (first 15 lines):"
head -n 15 /redis.conf

echo "=== ACL Configuration Details ==="
echo "Checking ACL-related lines:"
grep -A 5 "user default" /redis.conf || echo "No user configuration found"
grep -A 2 "requirepass" /redis.conf || echo "No requirepass configuration found"

# Test Redis configuration file
echo "=== Redis Configuration Test ==="
echo "Starting Redis configuration test with detailed output..."

# Start Redis in daemonized mode
if ! redis-server /redis.conf --daemonize yes; then
    echo "ERROR: Redis configuration test failed"
    echo "Full redis.conf contents for debugging:"
    cat /redis.conf
    echo "=== End of redis.conf ==="
    echo "Checking Redis server version and capabilities:"
    redis-server --version
    redis-server --help
    exit 1
fi

# Wait briefly to allow Redis to start and then check its health.
sleep 1
if ! redis-cli ping | grep -q PONG; then
    echo "ERROR: Redis did not respond to PING"
    exit 1
fi

# Shut down Redis gracefully
redis-cli shutdown

echo "Redis configuration test passed successfully."

# Initialize Redis with default user and ACL
echo "=== ACL Configuration Process ==="
{
    echo "Starting temporary Redis instance for ACL setup..."
    redis-server /redis.conf --protected-mode no &
    REDIS_PID=$!
    
    echo "Waiting for Redis to start..."
    RETRY_COUNT=0
    MAX_RETRIES=30
    until redis-cli ping &>/dev/null || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
        echo "Attempt $((RETRY_COUNT+1))/$MAX_RETRIES: Redis startup status:"
        ps aux | grep redis
        echo "Recent log entries:"
        tail -n 5 /var/log/redis/redis.log
        sleep 1
        RETRY_COUNT=$((RETRY_COUNT+1))
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "ERROR: Redis failed to start after $MAX_RETRIES attempts"
        echo "Redis process status:"
        ps aux | grep redis
        echo "Redis logs:"
        tail -n 50 /var/log/redis/redis.log
        kill $REDIS_PID
        exit 1
    fi
    
    echo "Setting up default user..."
    redis-cli ACL SETUSER default on ">${REDIS_PASSWORD}" ~* &* +@all || {
        echo "ERROR: Failed to set up default user"
        echo "ACL list current state:"
        redis-cli ACL LIST
        kill $REDIS_PID
        exit 1
    }
    
    # Verify authentication
    echo "Verifying authentication..."
    if redis-cli -a "$REDIS_PASSWORD" ping | grep -q "PONG"; then
        echo "Authentication test successful"
    else
        echo "ERROR: Authentication test failed"
        echo "Current ACL settings:"
        redis-cli ACL LIST
        kill $REDIS_PID
        exit 1
    fi
    
    # Clean shutdown
    echo "Shutting down temporary Redis instance..."
    redis-cli shutdown
    wait $REDIS_PID
    echo "Temporary Redis instance shutdown complete."
} || exit 1

# Start Redis Stack with full configuration
echo "Starting Redis Stack Server with full configuration..."
echo "Configuration file: /redis.conf"
echo "Log file: /var/log/redis/redis.log"

# Monitor Redis logs in background
tail -f /var/log/redis/redis.log | grep --line-buffered -E "Authentication|ACL|ERROR|DENIED" &

# Start Redis Stack Server
echo "Executing final Redis server command..."
exec redis-stack-server /redis.conf \
    --loglevel debug \
    --logfile /var/log/redis/redis.log \
    --requirepass "${REDIS_PASSWORD}" \
    --user default on "${REDIS_PASSWORD}" ~* &* +@all
