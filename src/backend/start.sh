#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
until pg_isready -h postgres -U user -d content_platform; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
python -m debugpy --listen 0.0.0.0:5678 -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload