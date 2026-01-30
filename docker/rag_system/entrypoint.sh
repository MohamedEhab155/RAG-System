#!/bin/sh
set -e

echo "Running database migrations..."
cd /app/models/db_Schema/minirag/ && alembic upgrade head

echo "Starting FastAPI..."
cd /app && exec "$@"