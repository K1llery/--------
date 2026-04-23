#!/usr/bin/env bash
set -euo pipefail

DB_HOST="${TRAVEL_DB_HOST:-localhost}"
DB_PORT="${TRAVEL_DB_PORT:-5432}"
DB_NAME="${TRAVEL_DB_NAME:-travel_system}"
DB_USER="${TRAVEL_DB_USER:-travel_app}"
DB_PASSWORD="${TRAVEL_DB_PASSWORD:-travel_app}"

if ! command -v psql >/dev/null 2>&1; then
  echo "psql not found. Please install postgresql-client first." >&2
  exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo not found. Please create DB/user manually with a postgres superuser." >&2
  exit 1
fi

echo "Creating role/database via local postgres superuser (may prompt for sudo password)..."
sudo -u postgres psql -v ON_ERROR_STOP=1 -d postgres <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    EXECUTE format('CREATE ROLE %I WITH LOGIN PASSWORD %L', '${DB_USER}', '${DB_PASSWORD}');
  ELSE
    EXECUTE format('ALTER ROLE %I WITH LOGIN PASSWORD %L', '${DB_USER}', '${DB_PASSWORD}');
  END IF;
END
\$\$;

DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}') THEN
    EXECUTE format('CREATE DATABASE %I OWNER %I', '${DB_NAME}', '${DB_USER}');
  END IF;
END
\$\$;

GRANT ALL PRIVILEGES ON DATABASE "${DB_NAME}" TO "${DB_USER}";
SQL

echo "Verifying connection..."
PGPASSWORD="${DB_PASSWORD}" psql -w -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -c '\\conninfo'

echo
echo "Local PostgreSQL initialization completed."
echo "Suggested backend/.env values:"
echo "TRAVEL_STORAGE_BACKEND=postgres"
echo "TRAVEL_DATABASE_URL=postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
