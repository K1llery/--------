from __future__ import annotations

import re
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


class DiaryAIGCService:
    transitions = ("fade", "pan-left", "zoom-in", "wipe", "dolly")
    keyword_candidates = (
        "校园",
        "景区",
        "路线",
        "日落",
        "湖",
        "古建筑",
        "博物馆",
        "图书馆",
        "咖啡",
        "夜景",
        "花园",
        "广场",
    )

    @staticmethod
    def _split_sentences(content: str) -> list[str]:
        parts = [item.strip() for item in re.split(r"[。！？!?\n]+", content) if item.strip()]
        return parts or ["本次旅程记录暂未包含完整文本，系统按标题生成镜头草稿。"]

    @classmethod
    def _extract_keywords(cls, text: str, limit: int = 6) -> list[str]:
        matched = [item for item in cls.keyword_candidates if item in text]
        if len(matched) >= limit:
            return matched[:limit]

        tokens = re.findall(r"[A-Za-z0-9\u4e00-\u9fff]{2,}", text)
        stopwords = {"我们", "这里", "可以", "一个", "这个", "非常", "然后", "今天", "感觉", "旅行", "游览", "拍照"}
        for token in tokens:
            if token in stopwords or token in matched:
                continue
            matched.append(token)
            if len(matched) >= limit:
                break
        return matched[:limit] if matched else ["旅行", "城市漫游"]

    def generate_animation(self, diary: dict, max_shots: int = 6) -> dict:
        title = diary.get("title") or "旅程回放"
        destination = diary.get("destination_name") or "目的地"
        content = diary.get("content") or title
        media_urls = diary.get("media_urls") or []

        sentences = self._split_sentences(content)
        shot_count = min(max(len(sentences), 3), max_shots)
        keywords = self._extract_keywords(f"{title} {destination} {content}")

        shots: list[dict] = []
        cursor = 0
        for index in range(shot_count):
            caption = sentences[index % len(sentences)]
            transition = self.transitions[index % len(self.transitions)]
            duration_seconds = max(2, min(6, round(len(caption) / 12)))
            media_url = media_urls[index % len(media_urls)] if media_urls else ""
            visual_prompt = (
                f"目的地:{destination}; 镜头:{transition}; 画面重点:{caption}; "
                f"关键词:{'、'.join(keywords[:4])}"
            )
            narration = f"第{index + 1}镜，{caption}"

            shots.append(
                {
                    "index": index + 1,
                    "caption": caption,
                    "media_url": media_url,
                    "transition": transition,
                    "duration_seconds": duration_seconds,
                    "start_second": cursor,
                    "visual_prompt": visual_prompt,
                    "narration": narration,
                }
            )
            cursor += duration_seconds

        narration_script = " ".join(shot["narration"] for shot in shots)
        return {
            "diary_id": int(diary.get("id") or 0),
            "title": title,
            "destination_name": destination,
            "generation_mode": "aigc-storyboard-v1",
            "keywords": keywords,
            "total_duration_seconds": cursor,
            "narration_script": narration_script,
            "shots": shots,
        }
