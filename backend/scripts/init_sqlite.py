from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def parse_args() -> argparse.Namespace:
    from app.core.config import get_settings

    settings = get_settings()
    parser = argparse.ArgumentParser(description="Seed SQLite from datasets/prod JSON files")
    parser.add_argument("--dataset-dir", type=Path, default=settings.dataset_dir)
    parser.add_argument("--database-path", type=Path, default=settings.sqlite_path)
    return parser.parse_args()


def main() -> None:
    from app.scripts.seed_sqlite import seed_sqlite_from_json

    args = parse_args()
    dataset_dir = args.dataset_dir.resolve()
    database_path = args.database_path.resolve()
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {dataset_dir}")
    seed_sqlite_from_json(dataset_dir, database_path)
    print(f"SQLite seed completed: {database_path}")


if __name__ == "__main__":
    main()
