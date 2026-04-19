from __future__ import annotations

from datetime import datetime

from app.algorithms.compression import HuffmanCodec
from app.algorithms.search import InvertedIndex
from app.algorithms.topk import TopKSelector
from app.repositories.data_loader import DatasetRepository


class DiarySearchService:
    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository
        self.inverted = InvertedIndex()
        self._built = False
        self._items_by_id: dict[int, dict] = {}
        self._items_by_id_str: dict[str, dict] = {}

    def _rebuild_index(self, diaries: list[dict]) -> None:
        self.inverted = InvertedIndex()
        self.inverted.build(diaries, ["title", "content", "destination_name"], "id")
        self._items_by_id = {int(item["id"]): item for item in diaries}
        self._items_by_id_str = {str(item_id): item for item_id, item in self._items_by_id.items()}
        self._built = True

    def _ensure_index(self) -> None:
        if self._built:
            return
        self._rebuild_index(self.repository.diaries())

    def search(self, query: str) -> list[dict]:
        self._ensure_index()
        ids = self.inverted.search([query])
        matched = [self._items_by_id_str[item_id] for item_id in ids if item_id in self._items_by_id_str]
        if matched:
            return matched
        normalized = query.strip().lower()
        return [
            item
            for item in self._items_by_id.values()
            if normalized in item["title"].lower()
            or normalized in item["content"].lower()
            or normalized in item["destination_name"].lower()
        ]

    def recommend(self, top_k: int = 10) -> list[dict]:
        selector = TopKSelector(lambda item: item["views"] + item["rating"] * 10)
        return selector.select(self.repository.diaries(), top_k)

    def get_by_id(self, diary_id: int) -> dict | None:
        self._ensure_index()
        return self._items_by_id.get(diary_id)

    def create(self, user: dict, payload: dict) -> dict:
        diaries = self.repository.diaries()
        diary = {
            "id": max((item["id"] for item in diaries), default=0) + 1,
            "title": payload["title"],
            "destination_name": payload["destination_name"],
            "content": payload["content"],
            "views": 0,
            "rating": 4.5,
            "media_urls": payload.get("media_urls") or ([payload["cover_image_url"]] if payload.get("cover_image_url") else []),
            "author_id": user["id"],
            "author_name": user["display_name"],
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        diaries.append(diary)
        self.repository.save_diaries(diaries)
        self._built = False
        return diary

    def increment_view(self, diary_id: int) -> dict | None:
        diaries = self.repository.diaries()
        for item in diaries:
            if int(item["id"]) != diary_id:
                continue
            item["views"] = int(item.get("views") or 0) + 1
            self.repository.save_diaries(diaries)
            self._built = False
            return item
        return None

    def rate(self, diary_id: int, user: dict, score: float) -> dict | None:
        diaries = self.repository.diaries()
        diary = next((item for item in diaries if int(item["id"]) == diary_id), None)
        if diary is None:
            return None

        ratings = self.repository.diary_ratings()
        existing = next(
            (
                item
                for item in ratings
                if int(item.get("diary_id") or -1) == diary_id and int(item.get("user_id") or -1) == int(user["id"])
            ),
            None,
        )
        if existing is None:
            ratings.append(
                {
                    "id": max((int(item.get("id") or 0) for item in ratings), default=0) + 1,
                    "diary_id": diary_id,
                    "user_id": int(user["id"]),
                    "score": float(score),
                    "updated_at": datetime.now().isoformat(timespec="seconds"),
                }
            )
        else:
            existing["score"] = float(score)
            existing["updated_at"] = datetime.now().isoformat(timespec="seconds")

        diary_scores = [float(item.get("score") or 0.0) for item in ratings if int(item.get("diary_id") or -1) == diary_id]
        if diary_scores:
            diary["rating"] = round(sum(diary_scores) / len(diary_scores), 2)

        self.repository.save_diary_ratings(ratings)
        self.repository.save_diaries(diaries)
        self._built = False

        return {
            "diary": diary,
            "user_score": float(score),
            "rating_count": len(diary_scores),
        }


class CompressionService:
    def __init__(self) -> None:
        self.codec = HuffmanCodec()

    def compress(self, content: str) -> dict:
        encoded, codes = self.codec.encode(content)
        original_bits = len(content.encode("utf-8")) * 8
        compressed_bits = len(encoded)
        ratio = (compressed_bits / original_bits) if original_bits else 0.0
        return {
            "encoded": encoded,
            "codes": codes,
            "original_bits": original_bits,
            "compressed_bits": compressed_bits,
            "compression_ratio": round(ratio, 4),
        }

    def decompress(self, encoded: str, codes: dict[str, str]) -> str:
        return self.codec.decode(encoded, codes)
