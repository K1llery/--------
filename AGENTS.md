# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Commands
- **Backend test**: `cd backend && python -m pytest tests/ -x -q` (requires venv: `source ../.venv/bin/activate`)
- **Single test**: `cd backend && python -m pytest tests/test_algorithms.py::test_topk_selector_works -x`
- **Backend lint**: `cd backend && ruff check . && ruff format --check .`
- **Backend autofix**: `cd backend && ruff check --fix . && ruff format .`
- **Backend seed SQLite**: `cd backend && python scripts/init_sqlite.py --database-path ../storage/travel.db`
- **Backend run**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- **Frontend dev**: `cd frontend && npm run dev -- --host 0.0.0.0 --port 5173`
- **Frontend lint**: `cd frontend && npm run lint`
- **Frontend format**: `cd frontend && npm run format`
- **Frontend typecheck**: `cd frontend && npm run typecheck`

## Critical Architecture Facts
- Production data layer uses SQLite via `SQLiteRepository`, with one `collections` table storing JSON payloads per domain collection. JSON files in `datasets/prod/` are seed/test snapshots.
- `DatasetRepository` remains for tests and no-database demos; `SQLiteRepository` is the default runtime repository. Services are cached per-repository via `deps.py` helpers.
- `GraphBuilder` is extracted as a standalone service — `RoutePlanningService` and `NearbyFacilityService` both depend on it (no longer tight-coupled).
- Auth uses SHA-256 with salt stored in JSON, demo accounts fallback to password `demo123`.
- Tests use `tmp_path` fixture + `dependency_overrides` for dataset isolation — do NOT modify `datasets/prod/` in tests.
- API prefix is `/api` (configured in `config.py`), CORS origins default to `localhost:5173` and `127.0.0.1:5173`.
- AI integration lives under `/api/ai`: diary drafting uses Qwen-compatible DashScope chat completion, image generation uses Wan 2.7 and saves returned images locally before exposing `/media/generated/...`.
- Admin/Agents demo routes are intentionally not registered in the deployment build.
- Error handling: custom exception hierarchy (`BusinessError`, `NotFoundError`, `AuthenticationError`, `ConflictError`) in `core/exceptions.py`, registered via `core/error_handlers.py`. Services raise these directly; route layer does NOT catch/re-wrap.
- Logging: plain-text format (`asctime | level | name | message`) via `core/logging.py`, auto-configured at app startup.
- CI: GitHub Actions workflow at `.github/workflows/ci.yml` runs lint + format check + typecheck + build (frontend) and ruff + pytest (backend).

## Code Style
- Python: type hints required, `from __future__ import annotations` in service files, slots dataclasses for data structures.
- Python linting: ruff configured in `backend/pyproject.toml` (line-length 120, rules E/F/W/I/UP/B/SIM/RUF with project-specific ignores for CJK punctuation and FastAPI patterns).
- Frontend: Vue 3 `<script setup lang="ts">`, Pinia Options API stores, axios-based API client.
- Frontend linting: ESLint flat config (`eslint.config.js`) + Prettier (`.prettierrc.json`); `no-explicit-any` is warning-only for gradual migration.
- Naming: snake_case Python, camelCase TypeScript, Chinese strings in UI/error messages.
