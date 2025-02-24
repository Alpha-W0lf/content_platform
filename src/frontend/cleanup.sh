#!/bin/bash

# Exit on error (but not for process checks)
set -e

echo "🧹 Starting frontend cleanup process..."

# Function to kill processes by pattern and PID file
kill_process() {
    local pattern=$1
    local name=$2
    local pid_file=$3

    echo "Checking for $name processes..."

    # First try PID file if provided
    if [ -n "$pid_file" ] && [ -f "$pid_file" ]; then
        echo "Found PID file: $pid_file"
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "Stopping $name process (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 1
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "Warning: $name process still running, attempting force kill..."
                kill -9 "$pid" 2>/dev/null || true
            else
                echo "$name process stopped successfully"
            fi
        else
            echo "Process with PID $pid not found"
        fi
        echo "Removing PID file: $pid_file"
        rm -f "$pid_file"
    fi

    # Check for any running processes matching pattern
    local RUNNING=0
    pgrep -f "$pattern" > /dev/null 2>&1 && RUNNING=1 || true

    if [ $RUNNING -eq 1 ]; then
        echo "Found running $name processes, attempting to stop..."
        pkill -f "$pattern" 2>/dev/null || true
        sleep 1
        
        # Check if still running after first attempt
        pgrep -f "$pattern" > /dev/null 2>&1 && {
            echo "‼️ Warning: Some $name processes still running, attempting force kill..."
            pkill -9 -f "$pattern" 2>/dev/null || true
        } || echo "✅ $name processes stopped successfully"
    else
        echo "No running $name processes found"
    fi
}

# Kill Next.js development server
kill_process "next dev" "Next.js" "logs/frontend/next.pid"

# Final verification - this should not cause script to exit if no processes found
pgrep -f "next dev" > /dev/null 2>&1 && {
    echo "⚠️ WARNING: Next.js processes could not be stopped"
    exit 1
} || {
    echo "✅ Frontend processes successfully cleaned up"
}
