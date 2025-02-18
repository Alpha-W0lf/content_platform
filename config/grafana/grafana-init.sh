#!/bin/bash
set -e

# Wait for PostgreSQL to be ready by checking Grafana's health endpoint.
echo "Waiting for Grafana to be ready..."
until wget --spider -q "http://localhost:3000/api/health"; do
  sleep 2
done

echo "Grafana is ready, starting..."
exec /run.sh
