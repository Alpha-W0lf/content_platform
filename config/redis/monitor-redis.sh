#!/bin/bash

# Set log file location
LOG_FILE="/var/log/redis/health.log"
LAST_CHECK="/var/log/redis/last_check"

# Log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Initialize log
log "=== Redis Health Check Started ==="
log "Hostname: $(hostname)"
log "Redis port: 6379"

# Check if Redis password is set
if [ -z "$REDIS_PASSWORD" ]; then
    log "ERROR: REDIS_PASSWORD environment variable not set"
    exit 1
fi

# Function to test Redis connection and auth
test_redis() {
    local result
    
    # Test basic connection
    if ! result=$(redis-cli -h redis ping 2>&1); then
        log "ERROR: Redis connection failed - $result"
        return 1
    fi
    
    # Test authentication
    if ! result=$(redis-cli -h redis -a "$REDIS_PASSWORD" --no-auth-warning auth default "$REDIS_PASSWORD" 2>&1); then
        log "ERROR: Redis authentication failed - $result"
        return 1
    fi
    
    # Test ACL permissions
    if ! result=$(redis-cli -h redis -a "$REDIS_PASSWORD" --no-auth-warning acl whoami 2>&1); then
        log "ERROR: ACL check failed - $result"
        return 1
    fi
    
    # Get Redis info for diagnostics
    if ! result=$(redis-cli -h redis -a "$REDIS_PASSWORD" --no-auth-warning info 2>&1); then
        log "ERROR: Could not get Redis info - $result"
        return 1
    fi
    
    # Extract and log key metrics
    local version=$(echo "$result" | grep redis_version | cut -d: -f2)
    local connected_clients=$(echo "$result" | grep connected_clients | cut -d: -f2)
    local used_memory=$(echo "$result" | grep used_memory_human | cut -d: -f2)
    
    log "Redis version: $version"
    log "Connected clients: $connected_clients"
    log "Used memory: $used_memory"
    
    # Check recent authentication failures
    local auth_failures=$(redis-cli -h redis -a "$REDIS_PASSWORD" --no-auth-warning ACL LOG 10 2>&1 | grep -c "auth")
    if [ "$auth_failures" -gt 0 ]; then
        log "WARNING: Detected $auth_failures recent authentication failures"
        redis-cli -h redis -a "$REDIS_PASSWORD" --no-auth-warning ACL LOG 10 >> "$LOG_FILE"
    fi
    
    # Update last successful check
    date '+%s' > "$LAST_CHECK"
    return 0
}

# Main monitoring loop
while true; do
    if test_redis; then
        log "Health check passed"
    else
        log "Health check failed"
        # Optional: Add alerting or recovery actions here
    fi
    
    # Sleep for 30 seconds before next check
    sleep 30
done