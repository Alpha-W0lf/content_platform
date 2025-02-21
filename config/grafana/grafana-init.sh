#!/bin/bash
set -e

# Start Grafana in the background
/run.sh "$@" &
GRAFANA_PID=$!

# Wait for Grafana to be ready
echo "Waiting for Grafana to be ready..."
max_attempts=30
attempt=0

until wget --spider -q "http://localhost:3000/api/health" || [ $attempt -ge $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts: Waiting for Grafana to start..."
    sleep 2
done

if [ $attempt -ge $max_attempts ]; then
    echo "ERROR: Grafana failed to start after $max_attempts attempts"
    kill $GRAFANA_PID
    exit 1
fi

echo "Grafana is ready!"

# Wait for the Grafana process
wait $GRAFANA_PID
