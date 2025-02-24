#!/bin/bash

# Exit on error
set -e

# Set PostgreSQL password for all psql commands
export PGPASSWORD=password

# Get the backend directory (we're already in it)
BACKEND_DIR="$(pwd)"
# Get project root (two levels up from backend directory)
PROJECT_ROOT="$(cd ../.. && pwd)"

# Create logs directory if it doesn't exist
mkdir -p "logs/backend"
mkdir -p "logs/celery"
mkdir -p "logs/redis"

# Run cleanup script first
./cleanup.sh

echo "👷‍♂️🏗️ Starting all services..."

# Start Redis server
echo "Starting Redis server..."
redis-server --port 6379 --daemonize yes --logfile logs/redis/redis.log || {
    echo "‼️ Failed to start Redis server"
    exit 1
}

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
until redis-cli ping &>/dev/null; do
    echo "⚠️ Redis is unavailable - sleeping"
    sleep 1
done
echo "✅ Redis is ready!"

# Wait for database to be ready
echo "⏳ Waiting for database..."
until pg_isready -h localhost -U tom -d content_platform; do
  echo "⚠️ Postgres is unavailable - sleeping"
  sleep 1
done
echo "✅ Database is ready!"

# Print Postgres version and server info
echo "Checking Postgres version and connection info..."
psql -h localhost -U tom -d content_platform -c "SELECT version();"

# Check authentication method
echo "Checking authentication configuration..."
psql -h localhost -U tom -d content_platform -c "SELECT rolname, rolpassword FROM pg_authid WHERE rolname = 'tom';"

# Check current user permissions
echo "Checking user permissions..."
psql -h localhost -U tom -d content_platform -c "\du"

# Run migrations from project root where alembic.ini is located
echo "Running database migrations..."
cd "$PROJECT_ROOT"
echo "Running migrations from $(pwd)"
alembic upgrade head

# Change back to backend directory
cd "$BACKEND_DIR"

# Start Celery worker in background with nohup
echo "Starting Celery worker..."
cd "$BACKEND_DIR"  # Change to backend directory for Celery
nohup celery -A tasks worker --loglevel=info > logs/celery/worker.log 2>&1 &
CELERY_PID=$!
disown $CELERY_PID

# Wait for Celery to be ready
echo "⏳ Waiting for Celery worker to start..."
sleep 5
if ps -p $CELERY_PID > /dev/null; then
    echo "✅ Celery worker started successfully (PID: $CELERY_PID)"
else
    echo "‼️ Error: Celery worker failed to start"
    cat logs/celery/worker.log  # Show error output if available
    exit 1
fi

# Change back to backend directory
cd "$BACKEND_DIR"

# Start the FastAPI application in background with nohup
echo "Starting FastAPI application..."
if [ "${DEBUG:-false}" = "true" ]; then
    echo "Starting in debug mode..."
    nohup python -m debugpy --listen 0.0.0.0:5678 -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend/uvicorn.log 2>&1 &
else
    nohup uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend/uvicorn.log 2>&1 &
fi
UVICORN_PID=$!

# Wait briefly and check if uvicorn started successfully
sleep 3
if ps -p $UVICORN_PID > /dev/null; then
    echo "✅ FastAPI application started successfully (PID: $UVICORN_PID)"
else
    echo "‼️ Error: FastAPI application failed to start"
    exit 1
fi

# Save PIDs to files for cleanup script
echo "$CELERY_PID" > "logs/celery.pid"
echo "$UVICORN_PID" > "logs/uvicorn.pid"

echo "✅✅ All services started successfully! ✅✅"
echo "PIDs:"
echo "  Celery:  $CELERY_PID"
echo "  Uvicorn: $UVICORN_PID"
echo ""
echo "Logs:"
echo "  Celery:  logs/celery/worker.log"
echo "  Uvicorn: logs/backend/uvicorn.log"
echo ""
echo "To check service status:"
echo "  Celery:  tail -f logs/celery/worker.log"
echo "  Uvicorn: tail -f logs/backend/uvicorn.log"
