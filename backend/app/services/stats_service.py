from __future__ import annotations

from collections import Counter

from app.algorithms.topk import TopKSelector
from app.repositories.data_loader import DatasetRepository
from app.services.diary_service import CompressionService
from app.services.facility_types import normalize_facility_type
from app.services.recommendation_service import RecommendationService


class StatsService:
    def __init__(
        self, repository: DatasetRepository, recommendation_service: RecommendationService | None = None
    ) -> None:
        self.repository = repository
        self.recommendation_service = recommendation_service or RecommendationService(repository)

    @staticmethod
    def _distribution(counter: Counter[str], limit: int = 12) -> list[dict]:
        return [{"label": label or "未分类", "value": value} for label, value in counter.most_common(limit)]

    @staticmethod
    def _split_interests(value: str | list[str] | None) -> list[str]:
        raw_items = value if isinstance(value, list) else str(value or "").replace("，", ",").split(",")
        return [item.strip().lower() for item in raw_items if item and item.strip()]

    @staticmethod
    def _quality_score(item: dict) -> float:
        return float(item.get("rating") or 0.0) * 100 + float(item.get("heat") or 0.0)

    @staticmethod
    def _requirement(label: str, actual: int, required: int) -> dict:
        return {"label": label, "actual": actual, "required": required, "passed": actual >= required}

    def _top_destinations(self, limit: int = 8) -> list[dict]:
        selector = TopKSelector(self._quality_score)
        return selector.select(self.repository.destinations(), limit)

    def _top_diaries(self, limit: int = 8) -> list[dict]:
        selector = TopKSelector(lambda item: int(item.get("views") or 0) + float(item.get("rating") or 0.0) * 100)
        return selector.select(self.repository.diaries(), limit)

    def _top_foods(self, limit: int = 8) -> list[dict]:
        selector = TopKSelector(self._quality_score)
        return selector.select(self.repository.foods(), limit)

    def _compression_summary(self) -> dict:
        service = CompressionService()
        original_bits = 0
        compressed_bits = 0
        item_count = 0
        for diary in self.repository.diaries():
            content = str(diary.get("content") or "")
            if not content:
                continue
            item_count += 1
            result = service.compress(content)
            original_bits += int(result["original_bits"])
            compressed_bits += int(result["compressed_bits"])

        return {
            "algorithm": "Huffman",
            "source": "diary.content",
            "item_count": item_count,
            "original_bits": original_bits,
            "compressed_bits": compressed_bits,
            "average_ratio": round(compressed_bits / original_bits, 4) if original_bits else 0.0,
        }

    def overview(self) -> dict:
        destinations = self.repository.destinations()
        buildings = self.repository.buildings()
        facilities = self.repository.facilities()
        edges = self.repository.edges()
        users = self.repository.users()
        foods = self.repository.foods()
        diaries = self.repository.diaries()
        scenes = self.repository.scenes()

        facility_types = {
            normalize_facility_type(item.get("facility_type"), item.get("name", "")) for item in facilities
        }
        counts = {
            "destinations": len(destinations),
            "buildings": len(buildings),
            "facilities": len(facilities),
            "facility_types": len(facility_types),
            "edges": len(edges),
            "users": len(users),
            "foods": len(foods),
            "diaries": len(diaries),
            "scenes": len(scenes),
        }

        rating_buckets: Counter[str] = Counter()
        for item in [*destinations, *foods, *diaries]:
            rating = item.get("rating")
            if rating is None:
                continue
            bucket = f"{int(float(rating))}星"
            rating_buckets[bucket] += 1

        return {
            "counts": counts,
            "requirement_progress": {
                "destinations": self._requirement("景区/校园目的地", counts["destinations"], 200),
                "buildings": self._requirement("内部建筑/地点", counts["buildings"], 20),
                "facility_types": self._requirement("设施类型", counts["facility_types"], 10),
                "facilities": self._requirement("服务设施", counts["facilities"], 50),
                "edges": self._requirement("道路边", counts["edges"], 200),
                "users": self._requirement("系统用户", counts["users"], 10),
            },
            "top_destinations": self._top_destinations(),
            "top_diaries": self._top_diaries(),
            "top_foods": self._top_foods(),
            "distributions": {
                "destination_categories": self._distribution(
                    Counter(item.get("category", "") for item in destinations)
                ),
                "cities": self._distribution(Counter(item.get("city", "") for item in destinations)),
                "facility_types": self._distribution(
                    Counter(
                        normalize_facility_type(item.get("facility_type"), item.get("name", "")) for item in facilities
                    )
                ),
                "food_cuisines": self._distribution(Counter(item.get("cuisine", "") for item in foods)),
                "rating_buckets": self._distribution(rating_buckets),
            },
            "compression_summary": self._compression_summary(),
            "algorithm_evidence": [
                {"name": "非 O(n) 查询", "implementation": "HashIndex + TrieIndex + InvertedIndex"},
                {"name": "Top-10 部分选择", "implementation": "TopKSelector / quickselect_top_k"},
                {"name": "路线规划", "implementation": "Dijkstra / A* / Held-Karp / 2-opt"},
                {"name": "无损压缩", "implementation": "HuffmanCodec"},
            ],
        }

    @staticmethod
    def _matches_interest(destination: dict, interests: list[str]) -> bool:
        haystack = " ".join(
            [
                str(destination.get("name") or ""),
                str(destination.get("category") or ""),
                str(destination.get("description") or ""),
                " ".join(str(tag) for tag in destination.get("tags", [])),
            ]
        ).lower()
        return any(interest in haystack for interest in interests)

    def _relevant_destinations(self, interests: list[str]) -> list[dict]:
        if not interests:
            return []
        relevant = []
        for destination in self.repository.destinations():
            if not self._matches_interest(destination, interests):
                continue
            if float(destination.get("rating") or 0.0) >= 4.0 or float(destination.get("heat") or 0.0) >= 500:
                relevant.append(destination)
        if relevant:
            return relevant
        return [item for item in self.repository.destinations() if self._matches_interest(item, interests)]

    def recommendation_evaluation(self, top_k: int = 10) -> dict:
        top_k = max(1, min(int(top_k), 50))
        samples = []
        precision_sum = 0.0
        recall_sum = 0.0

        for user in self.repository.users():
            interests = self._split_interests(user.get("interests"))
            relevant = self._relevant_destinations(interests)
            if not interests or not relevant:
                continue
            recommendations = self.recommendation_service.recommend_destinations(top_k, None, interests)
            relevant_ids = {str(item.get("source_id")) for item in relevant}
            hits = [item for item in recommendations if str(item.get("source_id")) in relevant_ids]
            precision = len(hits) / max(len(recommendations), 1)
            recall = len(hits) / len(relevant_ids)
            precision_sum += precision
            recall_sum += recall
            samples.append(
                {
                    "user_id": int(user["id"]),
                    "display_name": user.get("display_name") or user.get("username") or "旅行者",
                    "interests": interests,
                    "recommended_count": len(recommendations),
                    "relevant_count": len(relevant_ids),
                    "hit_count": len(hits),
                    "hit_names": [str(item.get("name") or "") for item in hits[:5]],
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                }
            )

        evaluated = len(samples)
        precision_avg = precision_sum / evaluated if evaluated else 0.0
        recall_avg = recall_sum / evaluated if evaluated else 0.0
        f1 = 2 * precision_avg * recall_avg / (precision_avg + recall_avg) if precision_avg + recall_avg else 0.0
        return {
            "top_k": top_k,
            "precision": round(precision_avg, 4),
            "recall": round(recall_avg, 4),
            "f1": round(f1, 4),
            "evaluated_user_count": evaluated,
            "samples": samples[:10],
            "formula": "TopKSelector(score = rating * 15 + heat * 0.1 + interest_tag_hits * 8); relevant = interest match with quality threshold",
        }
