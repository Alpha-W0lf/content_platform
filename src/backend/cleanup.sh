#!/bin/bash

# Exit on error
set -e

echo "🧹 Starting cleanup process..."

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

if [ $FAILED -eq 1 ]; then
    echo "⚠️ WARNING: Some processes could not be stopped"
    exit 1
else
    echo "✅ All processes successfully cleaned up"
fi