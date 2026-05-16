from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.repositories.sqlite_repository import SQLiteRepository

logger = logging.getLogger(__name__)


class DatasetRepository:
    """JSON 文件数据仓库，带 mtime 级别读缓存。"""

    def __init__(self, dataset_dir: Path) -> None:
        self.dataset_dir = dataset_dir
        self._cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}

    def _load_json(self, name: str) -> list[dict[str, Any]]:
        path = self.dataset_dir / name
        if not path.exists():
            return []
        mtime = path.stat().st_mtime
        cached = self._cache.get(name)
        if cached is not None and cached[0] == mtime:
            return cached[1]
        data = json.loads(path.read_text(encoding="utf-8"))
        self._cache[name] = (mtime, data)
        logger.debug("Loaded %s (%d items, mtime=%.0f)", name, len(data), mtime)
        return data

    def _write_json(self, name: str, payload: list[dict[str, Any]]) -> None:
        path = self.dataset_dir / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        # 写入后立即失效对应缓存
        self._cache.pop(name, None)

    def destinations(self) -> list[dict[str, Any]]:
        return self._load_json("destinations.json")

    def featured_destinations(self) -> list[dict[str, Any]]:
        return self._load_json("featured_destinations.json")

    def scenes(self) -> list[dict[str, Any]]:
        return self._load_json("scenes.json")

    def buildings(self) -> list[dict[str, Any]]:
        return self._load_json("buildings.json")

    def edges(self) -> list[dict[str, Any]]:
        return self._load_json("edges.json")

    def facilities(self) -> list[dict[str, Any]]:
        return self._load_json("facilities.json")

    def indoors(self) -> list[dict[str, Any]]:
        return self._load_json("indoors.json")

    def foods(self) -> list[dict[str, Any]]:
        return self._load_json("foods.json")

    def diaries(self) -> list[dict[str, Any]]:
        return self._load_json("diaries.json")

    def diary_ratings(self) -> list[dict[str, Any]]:
        return self._load_json("diary_ratings.json")

    def destination_interactions(self) -> list[dict[str, Any]]:
        return self._load_json("destination_interactions.json")

    def save_destination_interactions(self, payload: list[dict[str, Any]]) -> None:
        self._write_json("destination_interactions.json", payload)

    def users(self) -> list[dict[str, Any]]:
        return self._load_json("users.json")

    def save_users(self, payload: list[dict[str, Any]]) -> None:
        self._write_json("users.json", payload)

    def sessions(self) -> list[dict[str, Any]]:
        return self._load_json("sessions.json")

    def save_sessions(self, payload: list[dict[str, Any]]) -> None:
        self._write_json("sessions.json", payload)

    def save_diaries(self, payload: list[dict[str, Any]]) -> None:
        self._write_json("diaries.json", payload)

    def save_diary_ratings(self, payload: list[dict[str, Any]]) -> None:
        self._write_json("diary_ratings.json", payload)

    def plans(self) -> list[dict[str, Any]]:
        return self._load_json("plans.json")

    def save_plans(self, payload: list[dict[str, Any]]) -> None:
        self._write_json("plans.json", payload)


@lru_cache
def get_json_repository() -> DatasetRepository:
    return DatasetRepository(get_settings().dataset_dir)


@lru_cache
def get_sqlite_repository() -> SQLiteRepository:
    return SQLiteRepository(get_settings().sqlite_path)


@lru_cache
def get_repository() -> DatasetRepository | SQLiteRepository:
    settings = get_settings()
    if settings.storage_backend == "sqlite":
        return get_sqlite_repository()
    return get_json_repository()
