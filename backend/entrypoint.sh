#!/bin/sh

# Stop the script if any command fails
set -e

if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database..."
    until pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; do
        sleep 1
    done
fi

echo "Applying database migrations..."
alembic -c /app/backend/alembic.ini upgrade head

echo "Starting application..."
# 'exec' replaces the shell script process with the CMD (uvicorn)
# "$@" represents the arguments passed from the Dockerfile CMD
exec "$@"
