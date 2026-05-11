from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class SQLiteRepository:
    """SQLite-backed repository preserving the existing list[dict] service contract."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=5)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS collections (
                    name TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _load_collection(self, name: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM collections WHERE name = ?",
                (name,),
            ).fetchone()
        if row is None:
            return []
        loaded = json.loads(row[0])
        return loaded if isinstance(loaded, list) else []

    def _save_collection(self, name: str, payload: list[dict[str, Any]]) -> None:
        serialized = json.dumps(payload, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO collections(name, payload, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(name) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (name, serialized),
            )

    def destinations(self) -> list[dict[str, Any]]:
        return self._load_collection("destinations")

    def featured_destinations(self) -> list[dict[str, Any]]:
        return self._load_collection("featured_destinations")

    def scenes(self) -> list[dict[str, Any]]:
        return self._load_collection("scenes")

    def buildings(self) -> list[dict[str, Any]]:
        return self._load_collection("buildings")

    def edges(self) -> list[dict[str, Any]]:
        return self._load_collection("edges")

    def facilities(self) -> list[dict[str, Any]]:
        return self._load_collection("facilities")

    def indoors(self) -> list[dict[str, Any]]:
        return self._load_collection("indoors")

    def foods(self) -> list[dict[str, Any]]:
        return self._load_collection("foods")

    def diaries(self) -> list[dict[str, Any]]:
        return self._load_collection("diaries")

    def diary_ratings(self) -> list[dict[str, Any]]:
        return self._load_collection("diary_ratings")

    def users(self) -> list[dict[str, Any]]:
        return self._load_collection("users")

    def save_users(self, payload: list[dict[str, Any]]) -> None:
        self._save_collection("users", payload)

    def sessions(self) -> list[dict[str, Any]]:
        return self._load_collection("sessions")

    def save_sessions(self, payload: list[dict[str, Any]]) -> None:
        self._save_collection("sessions", payload)

    def save_diaries(self, payload: list[dict[str, Any]]) -> None:
        self._save_collection("diaries", payload)

    def save_diary_ratings(self, payload: list[dict[str, Any]]) -> None:
        self._save_collection("diary_ratings", payload)

    def plans(self) -> list[dict[str, Any]]:
        return self._load_collection("plans")

    def save_plans(self, payload: list[dict[str, Any]]) -> None:
        self._save_collection("plans", payload)
