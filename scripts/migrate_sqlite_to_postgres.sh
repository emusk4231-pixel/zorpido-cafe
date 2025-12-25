#!/usr/bin/env bash
set -euo pipefail

# Usage: set DATABASE_URL to your Postgres URL and run this script from the project root.
# Example:
#   export DATABASE_URL="postgres://user:pass@host:5432/dbname"
#   ./scripts/migrate_sqlite_to_postgres.sh

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set. Set it to your Postgres connection string and retry."
  echo "Example: export DATABASE_URL='postgres://user:pass@host:5432/dbname'"
  exit 1
fi

echo "Dumping current data from Django (excluding contenttypes, auth.permissions, sessions, admin log entries)..."
python manage.py dumpdata --natural-primary --natural-foreign --exclude auth.permission --exclude contenttypes --exclude sessions --exclude admin.logentry > /tmp/zorpido_data.json

echo "Installing dependencies (ensure virtualenv active if needed)..."
pip install -r requirements.txt

echo "Running migrations on Postgres DB pointed to DATABASE_URL..."
export DATABASE_URL
python manage.py migrate --noinput

echo "Loading data into Postgres (may raise integrity errors for certain objects)..."
python manage.py loaddata /tmp/zorpido_data.json

echo "Migration complete. Temporary export is /tmp/zorpido_data.json — remove it if no longer needed."
