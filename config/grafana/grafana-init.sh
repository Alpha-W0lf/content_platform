#!/bin/bash
set -e
# Debug logging for wget calls
log_and_wget() {
    echo "DEBUG: Attempting to fetch URL: $1" >&2
    wget "$1"
    RETVAL=$?
    if [ $RETVAL -ne 0 ]; then
        echo "ERROR: wget failed with exit code $RETVAL for URL: $1" >&2
    fi
    return $RETVAL
}
set -e

# Wait for PostgreSQL to be ready by checking Grafana's health endpoint.
echo "Waiting for Grafana to be ready..."
until wget --spider -q "http://localhost:3000/api/health"; do
  sleep 2
done

echo "Grafana is ready, starting..."
exec /run.sh
