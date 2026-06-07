#!/bin/sh

# Stop execution if any command fails
set -e

echo "Waiting for postgres database..."
python -c "
import time
import psycopg2
import sys
from app.db.config import settings

url = settings.DATABASE_URL
print(f'Trying to connect to database...')
for i in range(30):
    try:
        conn = psycopg2.connect(url)
        conn.close()
        print('PostgreSQL database is ready!')
        sys.exit(0)
    except Exception as e:
        print(f'Database is not ready yet, retrying in 1 second... ({i+1}/30)')
        time.sleep(1)
sys.exit(1)
"

echo "Running database migrations (alembic upgrade head)..."
alembic upgrade head

echo "Running database seeder (python -m app.db.seed)..."
python -m app.db.seed

echo "Starting FastAPI server..."
exec python main.py
