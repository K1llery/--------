from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def seed_sqlite_from_json(dataset_dir: Path, database_path: Path) -> None:
    """Load every JSON dataset file into the SQLite collections table."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path, timeout=5) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS collections (
                name TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        for file_path in sorted(dataset_dir.glob("*.json")):
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                continue
            connection.execute(
                """
                INSERT INTO collections(name, payload, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(name) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (file_path.stem, json.dumps(payload, ensure_ascii=False)),
            )
