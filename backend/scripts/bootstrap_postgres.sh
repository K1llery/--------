#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${BACKEND_DIR}/../.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "${BACKEND_DIR}/../.venv/bin/activate"
fi

cd "${BACKEND_DIR}"

alembic upgrade head
python scripts/seed_db.py --skip-create-tables

echo "PostgreSQL schema migrated and dataset seeded."
