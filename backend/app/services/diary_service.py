from __future__ import annotations

import re
from datetime import datetime

from app.algorithms.compression import HuffmanCodec
from app.algorithms.search import InvertedIndex
from app.algorithms.topk import TopKSelector
from app.repositories.data_loader import DatasetRepository


class DiaryRecommendService:
    """Sort/recommend diaries with multiple strategies.

    Strategies (sort key):
    - ``hot``        : descending by ``views``.
    - ``rating``     : Bayesian-smoothed average using ``rating_count`` from
                       ``diary_ratings.json`` (when available); otherwise the raw
                       average is used and the limitation is reported in debug.
    - ``latest``     : descending by ``created_at``.
    - ``recommend``  : composite ``0.6 * normalized_views + 0.4 * normalized_rating``.
    - ``interest``   : restrict to destinations the current user has signaled
                       interest in (own diaries / high ratings / favorites);
                       falls back to ``recommend`` if the signal is too thin.
    """

    BAYESIAN_PRIOR_C: float = 5.0  # confidence weight for Bayesian smoothing

    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository

    # ------------------------------------------------------------------
    # Sorting helpers
    # ------------------------------------------------------------------

    def _rating_counts(self) -> dict[int, int]:
        counts: dict[int, int] = {}
        for record in self.repository.diary_ratings():
            try:
                diary_id = int(record.get("diary_id") or -1)
            except (TypeError, ValueError):
                continue
            if diary_id < 0:
                continue
            counts[diary_id] = counts.get(diary_id, 0) + 1
        return counts

    @staticmethod
    def _global_mean_rating(diaries: list[dict]) -> float:
        scores = [float(d.get("rating") or 0.0) for d in diaries if d.get("rating") is not None]
        return sum(scores) / len(scores) if scores else 0.0

    def _bayesian_score(self, diary: dict, *, counts: dict[int, int], global_mean: float) -> float:
        n = counts.get(int(diary.get("id") or -1), 0)
        avg = float(diary.get("rating") or 0.0)
        return (self.BAYESIAN_PRIOR_C * global_mean + n * avg) / (self.BAYESIAN_PRIOR_C + n)

    def _recommend_sort(self, diaries: list[dict], *, reason: str) -> tuple[list[dict], dict]:
        if not diaries:
            return [], {"sort": "recommend", "reason": reason, "scores": {}}
        max_views = max((int(d.get("views") or 0) for d in diaries), default=0) or 1

        def score(item: dict) -> float:
            v = int(item.get("views") or 0) / max_views
            r = float(item.get("rating") or 0.0) / 5.0
            return 0.6 * v + 0.4 * r

        scored = [(item, score(item)) for item in diaries]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [item for item, _ in scored], {
            "sort": "recommend",
            "reason": reason,
            "formula": "0.6 * normalized_views + 0.4 * normalized_rating",
            "max_views": max_views,
            "scores": {int(item["id"]): round(s, 4) for item, s in scored[:20]},
        }

    # ------------------------------------------------------------------
    # Interest signal
    # ------------------------------------------------------------------

    def _interest_destinations(self, user: dict) -> set[str]:
        try:
            user_id = int(user["id"])
        except (KeyError, TypeError, ValueError):
            return set()
        names: set[str] = set()
        for diary in self.repository.diaries():
            if int(diary.get("author_id") or -1) == user_id:
                name = str(diary.get("destination_name") or "").strip()
                if name:
                    names.add(name)
        rated_ids = {
            int(r.get("diary_id") or -1)
            for r in self.repository.diary_ratings()
            if int(r.get("user_id") or -1) == user_id and float(r.get("score") or 0.0) >= 4.0
        }
        if rated_ids:
            for diary in self.repository.diaries():
                if int(diary.get("id") or -1) in rated_ids:
                    name = str(diary.get("destination_name") or "").strip()
                    if name:
                        names.add(name)
        fav_source_ids = {str(s) for s in (user.get("favorite_destination_ids") or [])}
        if fav_source_ids:
            for dest in self.repository.destinations():
                if str(dest.get("source_id")) in fav_source_ids:
                    name = str(dest.get("name") or "").strip()
                    if name:
                        names.add(name)
        return names

    # ------------------------------------------------------------------
    # Public entry
    # ------------------------------------------------------------------

    def sort(
        self,
        diaries: list[dict],
        sort_key: str,
        *,
        current_user: dict | None = None,
    ) -> tuple[list[dict], dict]:
        """Return ``(sorted_diaries, debug_info)``.

        ``debug_info`` always includes ``sort`` and ``reason``; sort-specific
        keys (``scores``, ``formula``, ``global_mean``...) are added when
        meaningful so the UI can show "命中分数 / 排序原因" without lying.
        """
        normalized = (sort_key or "recommend").strip().lower()
        if normalized == "views":
            normalized = "hot"
        if not diaries:
            return [], {"sort": normalized, "reason": "结果为空"}

        if normalized == "hot":
            sorted_d = sorted(diaries, key=lambda d: int(d.get("views") or 0), reverse=True)
            return sorted_d, {
                "sort": "hot",
                "reason": "按浏览量降序",
                "scores": {int(d["id"]): int(d.get("views") or 0) for d in sorted_d[:20]},
            }

        if normalized == "rating":
            counts = self._rating_counts()
            has_counts = any(counts.values())
            global_mean = self._global_mean_rating(diaries)
            if has_counts:
                scored = [(d, self._bayesian_score(d, counts=counts, global_mean=global_mean)) for d in diaries]
                debug = {
                    "sort": "rating",
                    "reason": "贝叶斯平滑评分",
                    "formula": "(C * global_mean + N * rating) / (C + N)",
                    "prior_C": self.BAYESIAN_PRIOR_C,
                    "global_mean": round(global_mean, 3),
                }
            else:
                scored = [(d, float(d.get("rating") or 0.0)) for d in diaries]
                debug = {
                    "sort": "rating",
                    "reason": "未提供评分人数，使用原始平均分",
                    "limitation": "rating_count 缺失，无法做贝叶斯平滑",
                }
            scored.sort(
                key=lambda pair: (pair[1], float(pair[0].get("rating") or 0.0)),
                reverse=True,
            )
            debug["scores"] = {int(d["id"]): round(s, 3) for d, s in scored[:20]}
            return [d for d, _ in scored], debug

        if normalized == "latest":
            sorted_d = sorted(diaries, key=lambda d: str(d.get("created_at") or ""), reverse=True)
            return sorted_d, {"sort": "latest", "reason": "按创建时间降序"}

        if normalized == "interest":
            if current_user is None:
                items, debug = self._recommend_sort(diaries, reason="未登录，回落综合推荐")
                debug["sort"] = "interest"
                debug["fallback"] = "recommend"
                return items, debug
            interests = self._interest_destinations(current_user)
            if not interests:
                items, debug = self._recommend_sort(diaries, reason="兴趣信号不足，回落综合推荐")
                debug["sort"] = "interest"
                debug["fallback"] = "recommend"
                debug["interest_destinations"] = []
                return items, debug
            interesting = [d for d in diaries if str(d.get("destination_name") or "") in interests]
            if len(interesting) < 3:
                items, debug = self._recommend_sort(diaries, reason="兴趣命中过少，回落综合推荐")
                debug["sort"] = "interest"
                debug["fallback"] = "recommend"
                debug["interest_destinations"] = sorted(interests)
                debug["matched_count"] = len(interesting)
                return items, debug
            items, debug = self._recommend_sort(interesting, reason="按用户兴趣过滤后综合推荐")
            debug["sort"] = "interest"
            debug["interest_destinations"] = sorted(interests)
            debug["matched_count"] = len(interesting)
            return items, debug

        # recommend / default
        return self._recommend_sort(diaries, reason="综合推荐")


class DiarySearchService:
    # Field weights for full-text relevance ranking.
    FIELD_WEIGHTS: list[tuple[str, float]] = [
        ("title", 5.0),
        ("destination_name", 4.0),
        ("tags", 3.0),
        ("content", 1.0),
    ]

    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository
        self.inverted = InvertedIndex()
        self._built = False
        self._items_by_id: dict[int, dict] = {}
        self._items_by_id_str: dict[str, dict] = {}
        # HashMap indices: O(1) lookup by normalized title / destination.
        self._title_index: dict[str, list[int]] = {}
        self._destination_index: dict[str, list[int]] = {}
        self.recommender = DiaryRecommendService(repository)

    @staticmethod
    def _normalize(value: str) -> str:
        """Lowercase + collapse internal whitespace for index keys."""
        return " ".join(value.strip().split()).lower()

    def _rebuild_index(self, diaries: list[dict]) -> None:
        self.inverted = InvertedIndex()
        self.inverted.build_ranked(diaries, self.FIELD_WEIGHTS, "id")
        self._items_by_id = {int(item["id"]): item for item in diaries}
        self._items_by_id_str = {str(item_id): item for item_id, item in self._items_by_id.items()}
        self._title_index = {}
        self._destination_index = {}
        for item in diaries:
            diary_id = int(item["id"])
            title_key = self._normalize(str(item.get("title") or ""))
            dest_key = self._normalize(str(item.get("destination_name") or ""))
            if title_key:
                self._title_index.setdefault(title_key, []).append(diary_id)
            if dest_key:
                self._destination_index.setdefault(dest_key, []).append(diary_id)
        self._built = True

    def _ensure_index(self) -> None:
        if self._built:
            return
        self._rebuild_index(self.repository.diaries())

    def list_all(self) -> list[dict]:
        """返回全部日记列表。"""
        return self.repository.diaries()

    # ------------------------------------------------------------------
    # Targeted lookups (O(1) HashMap lookup; fallback only when missing)
    # ------------------------------------------------------------------

    def search_by_title_exact(self, title: str) -> list[dict]:
        """O(1) HashMap lookup by exact (normalized) title."""
        self._ensure_index()
        key = self._normalize(title)
        if not key:
            return []
        ids = self._title_index.get(key)
        if ids is None:
            return []
        return [self._items_by_id[i] for i in ids if i in self._items_by_id]

    def search_by_destination(self, destination: str) -> list[dict]:
        """O(1) HashMap lookup by exact destination name; falls back to
        substring match over the *destinations only* if the exact key misses
        (still cheaper than scanning full diaries).
        """
        self._ensure_index()
        key = self._normalize(destination)
        if not key:
            return []
        ids = self._destination_index.get(key)
        if ids:
            return [self._items_by_id[i] for i in ids if i in self._items_by_id]
        # Fallback: partial match on destination keys (small set).
        matched_ids: list[int] = []
        for dest_key, dest_ids in self._destination_index.items():
            if key in dest_key:
                matched_ids.extend(dest_ids)
        return [self._items_by_id[i] for i in matched_ids if i in self._items_by_id]

    def search_fulltext(self, query: str) -> list[dict]:
        """Weighted full-text search across title/destination/tags/content.

        Uses :meth:`InvertedIndex.search_ranked` so results are ordered by
        relevance score. Field weights default to title=5, destination=4,
        tags=3, content=1.
        """
        self._ensure_index()
        ranked = self.inverted.search_ranked([query], self.FIELD_WEIGHTS)
        results: list[dict] = []
        for item_id, _score in ranked:
            item = self._items_by_id_str.get(item_id)
            if item is not None:
                results.append(item)
        return results

    def search(self, query: str) -> list[dict]:
        """Backward-compatible search: weighted full-text + substring fallback."""
        results = self.search_fulltext(query)
        if results:
            return results
        normalized = self._normalize(query)
        if not normalized:
            return []
        return [
            item
            for item in self._items_by_id.values()
            if normalized in self._normalize(str(item.get("title") or ""))
            or normalized in self._normalize(str(item.get("content") or ""))
            or normalized in self._normalize(str(item.get("destination_name") or ""))
        ]

    # ------------------------------------------------------------------
    # Recommend / sort
    # ------------------------------------------------------------------

    def recommend(self, top_k: int = 10) -> list[dict]:
        items, _debug = self.recommender.sort(self.repository.diaries(), "recommend")
        return items[:top_k]

    def discover(
        self,
        *,
        q: str | None,
        search_type: str,
        sort: str,
        page: int,
        page_size: int,
        current_user: dict | None = None,
    ) -> dict:
        """Unified discovery entry: filter -> sort -> paginate."""
        self._ensure_index()
        normalized_query = (q or "").strip()
        normalized_type = (search_type or "all").strip().lower()
        normalized_sort = (sort or "recommend").strip().lower()
        if normalized_sort == "views":
            normalized_sort = "hot"
        page = max(int(page or 1), 1)
        page_size = max(min(int(page_size or 50), 200), 1)

        if normalized_query:
            if normalized_type == "destination":
                base = self.search_by_destination(normalized_query)
            elif normalized_type == "title_exact":
                base = self.search_by_title_exact(normalized_query)
            elif normalized_type == "fulltext":
                base = self.search_fulltext(normalized_query)
            else:
                base = self.search(normalized_query)
        else:
            base = list(self._items_by_id.values()) or self.repository.diaries()

        # Fulltext result is already relevance-sorted; only re-sort when the
        # caller explicitly asks for another ordering.
        if normalized_type == "fulltext" and normalized_sort == "recommend" and normalized_query:
            sorted_items = base
            debug = {
                "sort": "recommend",
                "reason": "全文检索按相关度排序，未做综合推荐重排",
                "scores": {},
            }
        else:
            sorted_items, debug = self.recommender.sort(base, normalized_sort, current_user=current_user)

        total = len(sorted_items)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = sorted_items[start:end]

        return {
            "items": page_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "search_type": normalized_type if normalized_query else None,
            "sort": normalized_sort,
            "debug": debug,
        }

    def get_by_id(self, diary_id: int) -> dict | None:
        self._ensure_index()
        return self._items_by_id.get(diary_id)

    def list_by_author(self, user_id: int) -> list[dict]:
        diaries = self.repository.diaries()
        return [item for item in diaries if int(item.get("author_id") or -1) == int(user_id)]

    def update(
        self,
        diary_id: int,
        user: dict,
        payload: dict,
    ) -> dict | None:
        """Update a diary. Returns the updated dict or None if missing.

        Raises ``PermissionError`` if the current user is not the author.
        """
        diaries = self.repository.diaries()
        target = next((item for item in diaries if int(item["id"]) == diary_id), None)
        if target is None:
            return None
        if int(target.get("author_id") or -1) != int(user["id"]):
            raise PermissionError("only author can edit")

        editable = ("title", "destination_name", "content", "cover_image_url", "media_urls")
        for field in editable:
            value = payload.get(field)
            if value is None:
                continue
            target[field] = value
        if payload.get("media_urls") is not None and not target.get("cover_image_url"):
            target["cover_image_url"] = (target["media_urls"] or [""])[0]
        target["updated_at"] = datetime.now().isoformat(timespec="seconds")

        self.repository.save_diaries(diaries)
        self._built = False  # rebuild title/destination/inverted indices
        return target

    def delete(self, diary_id: int, user: dict) -> bool:
        """Delete a diary. Raises ``PermissionError`` if not the author."""
        diaries = self.repository.diaries()
        target = next((item for item in diaries if int(item["id"]) == diary_id), None)
        if target is None:
            return False
        if int(target.get("author_id") or -1) != int(user["id"]):
            raise PermissionError("only author can delete")

        diaries = [item for item in diaries if int(item["id"]) != diary_id]
        self.repository.save_diaries(diaries)
        self._built = False  # rebuild indices
        return True

    def create(self, user: dict, payload: dict) -> dict:
        diaries = self.repository.diaries()
        diary = {
            "id": max((item["id"] for item in diaries), default=0) + 1,
            "title": payload["title"],
            "destination_name": payload["destination_name"],
            "content": payload["content"],
            "views": 0,
            "rating": 4.5,
            "media_urls": payload.get("media_urls")
            or ([payload["cover_image_url"]] if payload.get("cover_image_url") else []),
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

        diary_scores = [
            float(item.get("score") or 0.0) for item in ratings if int(item.get("diary_id") or -1) == diary_id
        ]
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
                f"目的地:{destination}; 镜头:{transition}; 画面重点:{caption}; 关键词:{'、'.join(keywords[:4])}"
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
