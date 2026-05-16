from __future__ import annotations

from datetime import UTC, datetime

from app.algorithms.topk import TopKSelector
from app.core.exceptions import NotFoundError
from app.repositories.data_loader import DatasetRepository
from app.services.recommendation_service import RecommendationService


class DestinationInteractionService:
    """Destination detail and interaction service.

    Runtime interaction data is stored separately from the destination snapshot so
    seed data stays stable while views/ratings remain persistent.
    """

    def __init__(
        self, repository: DatasetRepository, recommendation_service: RecommendationService | None = None
    ) -> None:
        self.repository = repository
        self.recommendation_service = recommendation_service or RecommendationService(repository)

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    @staticmethod
    def _distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        return RecommendationService._haversine_km(lat1, lng1, lat2, lng2)

    def _destination_candidates(self) -> list[dict]:
        seen: set[str] = set()
        items: list[dict] = []
        for item in [*self.repository.featured_destinations(), *self.repository.destinations()]:
            source_id = str(item.get("source_id", ""))
            if source_id and source_id not in seen:
                seen.add(source_id)
                items.append(item)
        return items

    def _find_destination(self, source_id: str) -> dict:
        for item in self._destination_candidates():
            if str(item.get("source_id")) == source_id:
                return item
        raise NotFoundError("目的地不存在")

    def _load_interactions(self) -> list[dict]:
        return self.repository.destination_interactions()

    def _get_or_create_interaction(self, source_id: str) -> tuple[list[dict], dict]:
        interactions = self._load_interactions()
        for item in interactions:
            if str(item.get("source_id")) == source_id:
                item.setdefault("total_views", 0)
                item.setdefault("ratings", [])
                return interactions, item
        item = {"source_id": source_id, "total_views": 0, "ratings": []}
        interactions.append(item)
        return interactions, item

    def _save_interactions(self, interactions: list[dict]) -> None:
        self.repository.save_destination_interactions(interactions)

    @staticmethod
    def _interaction_stats(interaction: dict | None, user: dict | None = None) -> dict:
        if interaction is None:
            return {"total_views": 0, "rating_avg": None, "rating_count": 0, "user_score": None}

        ratings = [
            item
            for item in interaction.get("ratings", [])
            if item.get("score") is not None and item.get("user_id") is not None
        ]
        scores = [float(item["score"]) for item in ratings]
        user_score = None
        if user is not None:
            user_id = int(user["id"])
            for item in ratings:
                if int(item.get("user_id")) == user_id:
                    user_score = float(item["score"])
                    break
        return {
            "total_views": int(interaction.get("total_views") or 0),
            "rating_avg": round(sum(scores) / len(scores), 2) if scores else None,
            "rating_count": len(scores),
            "user_score": user_score,
        }

    def _nearby_facilities(self, destination: dict, limit: int = 6) -> list[dict]:
        lat = destination.get("latitude")
        lng = destination.get("longitude")
        if lat is None or lng is None:
            return []

        ranked = []
        for facility in self.repository.facilities():
            item_lat = facility.get("latitude")
            item_lng = facility.get("longitude")
            if item_lat is None or item_lng is None:
                continue
            distance = self._distance_km(float(lat), float(lng), float(item_lat), float(item_lng))
            enriched = dict(facility)
            enriched["distance_km"] = round(distance, 2)
            ranked.append(enriched)
        selector = TopKSelector(lambda item: -float(item.get("distance_km") or 0.0))
        return selector.select(ranked, limit)

    def _nearby_foods(self, destination: dict, limit: int = 6) -> list[dict]:
        name = str(destination.get("name") or "")
        exact = [item for item in self.repository.foods() if str(item.get("destination_name") or "") == name]
        if len(exact) >= limit:
            selector = TopKSelector(lambda item: float(item.get("rating") or 0.0) * 10 + float(item.get("heat") or 0.0))
            return selector.select(exact, limit)

        lat = destination.get("latitude")
        lng = destination.get("longitude")
        nearby = []
        if lat is not None and lng is not None:
            nearby = self.recommendation_service.recommend_foods(limit * 2, None, float(lat), float(lng), 5.0)

        seen = {str(item.get("source_id") or item.get("name")) for item in exact}
        merged = list(exact)
        for item in nearby:
            key = str(item.get("source_id") or item.get("name"))
            if key not in seen:
                seen.add(key)
                merged.append(item)
            if len(merged) >= limit:
                break
        return merged[:limit]

    def _related_diaries(self, destination: dict, limit: int = 5) -> list[dict]:
        name = str(destination.get("name") or "")
        if not name:
            return []
        related = []
        for diary in self.repository.diaries():
            diary_destination = str(diary.get("destination_name") or "")
            if diary_destination and (diary_destination in name or name in diary_destination):
                related.append(diary)
        selector = TopKSelector(lambda item: int(item.get("views") or 0) + float(item.get("rating") or 0.0) * 100)
        return selector.select(related, limit)

    def _decorate(self, destination: dict, user: dict | None = None) -> dict:
        interaction = next(
            (
                item
                for item in self._load_interactions()
                if str(item.get("source_id")) == str(destination.get("source_id"))
            ),
            None,
        )
        return {
            **destination,
            "interaction_stats": self._interaction_stats(interaction, user),
            "nearby_facilities": self._nearby_facilities(destination),
            "nearby_foods": self._nearby_foods(destination),
            "related_diaries": self._related_diaries(destination),
            "algorithm_explanation": "详情页联动使用哈希定位目的地，TopKSelector 选取周边美食和相关日记，浏览/评分写入独立持久化集合。",
        }

    def detail(self, source_id: str, user: dict | None = None) -> dict:
        return self._decorate(self._find_destination(source_id), user)

    def increment_view(self, source_id: str, user: dict | None = None) -> dict:
        destination = self._find_destination(source_id)
        interactions, interaction = self._get_or_create_interaction(source_id)
        interaction["total_views"] = int(interaction.get("total_views") or 0) + 1
        interaction["updated_at"] = self._now()
        self._save_interactions(interactions)
        return self._decorate(destination, user)

    def rate(self, source_id: str, user: dict, score: float) -> dict:
        destination = self._find_destination(source_id)
        interactions, interaction = self._get_or_create_interaction(source_id)
        user_id = int(user["id"])
        ratings = list(interaction.get("ratings") or [])
        for item in ratings:
            if int(item.get("user_id") or -1) == user_id:
                item["score"] = round(float(score), 2)
                item["updated_at"] = self._now()
                break
        else:
            ratings.append({"user_id": user_id, "score": round(float(score), 2), "updated_at": self._now()})
        interaction["ratings"] = ratings
        interaction["updated_at"] = self._now()
        self._save_interactions(interactions)
        return self._decorate(destination, user)
