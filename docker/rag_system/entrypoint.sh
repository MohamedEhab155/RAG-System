#!/bin/bash
set -e

echo "=== Starting Container Setup ==="

echo "Running database migrations..."
cd /app/models/db_Schema/minirag

echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# ALWAYS create alembic.ini at runtime - this ensures it's there
echo ""
echo "Creating alembic.ini configuration..."
cat > alembic.ini << 'EOFCONFIG'
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://Admin_Mohamed:Mohamedehab@pgvector:5432/minirag

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOFCONFIG

echo "✅ alembic.ini created successfully"
echo ""
echo "Verifying alembic.ini content:"
head -5 alembic.ini
echo ""

echo "Running Alembic migrations..."
alembic upgrade head

cd /app

echo ""
echo "✅ Migrations completed successfully"
echo "Starting FastAPI..."
exec "$@"