#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h postgres -p 5432 -U user; do
  sleep 2
done

echo "PostgreSQL is ready, starting Grafana..."
exec /run.sh