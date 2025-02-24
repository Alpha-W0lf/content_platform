#!/bin/bash

# Exit on error
set -e

echo "🧹🗑️🧼 Starting cleanup process..."

# Set PostgreSQL password for all psql commands
export PGPASSWORD=password

# Function to kill processes by pattern
kill_process() {
    local pattern=$1
    local name=$2
    if pgrep -f "$pattern" > /dev/null; then
        echo "Stopping $name processes..."
        pkill -f "$pattern" || true
        sleep 1
        if pgrep -f "$pattern" > /dev/null; then
            echo "Warning: Some $name processes are still running"
            echo "Attempting force kill..."
            pkill -9 -f "$pattern" || true
        else
            echo "$name processes stopped successfully"
        fi
    else
        echo "No $name processes found running"
    fi
}

# Function to clean up Redis resources
cleanup_redis() {
    echo "Cleaning up Redis resources..."
    
    # Check for and kill duplicate Redis instances
    echo "1. Checking for duplicate Redis instances..."
    redis_count=$(pgrep -f "redis-server" | wc -l | tr -d ' ')
    if [ "$redis_count" -gt 1 ]; then
        echo "Found $redis_count Redis instances. Cleaning up extras..."
        pgrep -f "redis-server" | sort | tail -n +2 | while read -r pid; do
            echo "Killing extra Redis instance (PID: $pid)"
            kill "$pid" 2>/dev/null || kill -9 "$pid"
        done
    fi
    
    # Handle high memory fragmentation
    echo "2. Checking memory fragmentation..."
    fragmentation=$(redis-cli info memory | grep "mem_fragmentation_ratio:" | cut -d: -f2)
    if [ -n "$fragmentation" ] && (( $(echo "$fragmentation > 1.5" | bc -l) )); then
        echo "High memory fragmentation detected ($fragmentation). Running aggressive cleanup..."
        redis-cli memory purge
        redis-cli config set activedefrag yes
        redis-cli config set active-defrag-threshold-lower 10
        redis-cli config set active-defrag-threshold-upper 100
    fi
    
    # Kill idle connections (over 5 minutes)
    echo "3. Checking for idle Redis connections..."
    redis-cli client list | awk -F'[ =]' '/idle/ && $6 > 300 {print $2}' | while read -r client_id; do
        echo "Killing idle client: $client_id"
        redis-cli client kill id "$client_id"
    done
    
    # Check memory fragmentation and flush if necessary
    echo "4. Checking memory fragmentation..."
    fragmentation=$(redis-cli info memory | grep "mem_fragmentation_ratio:" | cut -d: -f2)
    if (( $(echo "$fragmentation > 1.5" | bc -l) )); then
        echo "High memory fragmentation detected ($fragmentation). Running memory cleanup..."
        redis-cli memory purge
    fi
    
    # Clear all blocked/waiting clients
    echo "5. Clearing blocked/waiting clients..."
    redis-cli client list | grep -E "blocked|waiting" | cut -d' ' -f2 | while read -r client_id; do
        echo "Killing blocked/waiting client: $client_id"
        redis-cli client kill id "$client_id"
    done

    # Identify and clean up key space waste
    echo "6. Cleaning up key space..."
    redis-cli memory stats | grep -E "keys|overhead"
    redis-cli --scan --pattern "*" | while read -r key; do
        ttl=$(redis-cli ttl "$key")
        if [ "$ttl" -eq -1 ]; then  # Keys without TTL
            redis-cli expire "$key" 3600  # Set 1 hour expiry
        fi
    done
}

# Function to clean up PostgreSQL resources
cleanup_postgres() {
    echo "Cleaning up PostgreSQL resources..."
    
    # Handle low connection usage by adjusting max_connections
    echo "1. Optimizing connection settings..."
    current_max=$(psql -h localhost -U tom -d content_platform -tAc "SHOW max_connections;")
    active_count=$(psql -h localhost -U tom -d content_platform -tAc "SELECT count(*) FROM pg_stat_activity;")
    if [ -n "$current_max" ] && [ -n "$active_count" ]; then
        usage_ratio=$(echo "scale=2; $active_count / $current_max * 100" | bc)
        if [ $(echo "$usage_ratio < 10" | bc -l) -eq 1 ]; then
            new_max=$(( active_count * 3 ))  # Set to 3x current usage
            echo "Reducing max_connections from $current_max to $new_max"
            psql -h localhost -U tom -d content_platform -c "ALTER SYSTEM SET max_connections = $new_max;"
            echo "Connection settings updated. Will take effect after PostgreSQL restart."
        fi
    fi
    
    # Terminate idle connections over 30 minutes
    echo "2. Terminating idle connections..."
    psql -h localhost -U tom -d content_platform -c "
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE state = 'idle'
        AND state_change < NOW() - INTERVAL '30 minutes'
        AND pid <> pg_backend_pid();"
        
    # Cancel long-running queries (over 30 seconds)
    echo "3. Canceling long-running queries..."
    psql -h localhost -U tom -d content_platform -c "
        SELECT pg_cancel_backend(pid)
        FROM pg_stat_activity
        WHERE state = 'active'
        AND NOW() - query_start > INTERVAL '30 seconds'
        AND pid <> pg_backend_pid();"
    
    # Optimize connection settings if usage is low
    echo "4. Optimizing connection settings..."
    current_max=$(psql -h localhost -U tom -d content_platform -tAc "SHOW max_connections;")
    active_count=$(psql -h localhost -U tom -d content_platform -tAc "SELECT count(*) FROM pg_stat_activity;")
    if [ "$active_count" -lt $(( current_max / 10 )) ]; then
        new_max=$(( active_count * 2 ))
        echo "Reducing max_connections from $current_max to $new_max"
        psql -h localhost -U tom -d content_platform -c "ALTER SYSTEM SET max_connections = $new_max;"
    fi
        
    # Vacuum analyze to reclaim space
    echo "5. Running VACUUM ANALYZE..."
    psql -h localhost -U tom -d content_platform -c "VACUUM ANALYZE;"
}

# Function to check and kill memory-hungry processes
cleanup_memory_usage() {
    local pid=$1
    local name=$2
    local threshold=524288  # 512MB - matches check_services.sh
    
    if [ -n "$pid" ] && ps -p "$pid" > /dev/null; then
        mem_usage=$(ps -o rss= -p "$pid" | tr -d ' ')
        if [ "$mem_usage" -gt "$threshold" ]; then
            echo "⚠️ $name (PID: $pid) using excessive memory ($(( mem_usage / 1024 ))MB). Restarting..."
            kill "$pid"
            return 1
        fi
    fi
    return 0
}

# Function to cleanup duplicate processes
cleanup_duplicates() {
    local service=$1
    local count=$(pgrep -f "$service" | wc -l | tr -d ' ')
    if [ "$count" -gt 1 ]; then
        echo "Found duplicate $service processes. Cleaning up..."
        oldest_pids=$(pgrep -f "$service" | sort | tail -n +2)
        for pid in $oldest_pids; do
            echo "Killing duplicate $service process (PID: $pid)"
            kill $pid 2>/dev/null || kill -9 $pid
        done
    fi
}

# Function to aggressively clean up duplicate Celery processes
cleanup_celery_duplicates() {
    echo "Cleaning up duplicate Celery processes..."
    celery_count=$(pgrep -f "celery" | wc -l | tr -d ' ')
    if [ "$celery_count" -gt 1 ]; then
        echo "Found $celery_count Celery processes. Cleaning up..."
        # Kill all Celery processes
        pkill -f "celery" || true
        sleep 2
        # Force kill any remaining
        pkill -9 -f "celery" || true
        echo "Celery processes cleaned up. Will be restarted by start.sh"
    fi
}

echo "Performing thorough resource cleanup..."

# Run enhanced cleanups first
if redis-cli ping &>/dev/null; then
    cleanup_redis
fi

if pg_isready -h localhost -U tom -d content_platform &>/dev/null; then
    cleanup_postgres
fi

# Add aggressive Celery cleanup
cleanup_celery_duplicates

# Kill uvicorn processes
kill_process "uvicorn src.backend.main:app" "uvicorn"

# Kill debugpy processes
kill_process "debugpy --listen" "debugpy"

# Kill celery worker processes
kill_process "celery -A src.backend" "celery"

# Kill any hanging alembic processes
kill_process "alembic upgrade" "alembic"

# Cleanup local PostgreSQL server
if pg_ctl status -D /usr/local/var/postgres &>/dev/null; then
    echo "Stopping PostgreSQL server..."
    # First terminate existing connections to the database
    psql -h localhost -U tom -d postgres -c "
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = 'content_platform' 
        AND pid <> pg_backend_pid();" &>/dev/null || echo "Warning: Could not terminate existing connections"
    
    # Then stop the server
    pg_ctl stop -D /usr/local/var/postgres -m fast || true
    if pg_ctl status -D /usr/local/var/postgres &>/dev/null; then
        echo "Warning: PostgreSQL server still running, attempting force stop..."
        pg_ctl stop -D /usr/local/var/postgres -m immediate || true
    else
        echo "PostgreSQL server stopped successfully"
    fi
else
    echo "No PostgreSQL server found running"
fi

# Cleanup any local Redis server (if running outside Docker)
if pgrep redis-server > /dev/null; then
    echo "Stopping local Redis server..."
    redis-cli shutdown || true
fi

# Small delay to ensure processes are cleaned up
sleep 2

# Verify no processes are still running
FAILED=0

check_process() {
    local pattern=$1
    local name=$2
    if pgrep -f "$pattern" > /dev/null; then
        echo "ERROR: $name processes are still running!"
        FAILED=1
    fi
}

check_process "uvicorn src.backend.main:app" "Uvicorn"
check_process "debugpy --listen" "Debugpy"
check_process "celery -A src.backend" "Celery"
check_process "alembic upgrade" "Alembic"

# Check PostgreSQL
if pg_ctl status -D /usr/local/var/postgres &>/dev/null; then
    echo "‼️ ERROR: PostgreSQL server is still running!"
    FAILED=1
fi

# Check for memory-hungry processes before killing them
echo "Checking for memory-intensive processes..."
if [ -f "logs/celery.pid" ]; then
    CELERY_PID=$(cat logs/celery.pid)
    cleanup_memory_usage "$CELERY_PID" "Celery"
fi

if [ -f "logs/uvicorn.pid" ]; then
    UVICORN_PID=$(cat logs/uvicorn.pid)
    cleanup_memory_usage "$UVICORN_PID" "Uvicorn"
fi

# Add duplicate process cleanup
for service in "celery" "uvicorn" "redis-server"; do
    cleanup_duplicates "$service"
done

if [ $FAILED -eq 1 ]; then
    echo "⚠️ WARNING: Some processes could not be stopped"
    exit 1
else
    echo "✅ All processes successfully cleaned up"
fi

echo "🧹🗑️🧼 Resource cleanup complete! Run check_services.sh to verify."