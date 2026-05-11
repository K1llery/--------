from __future__ import annotations

from app.algorithms.topk import TopKSelector
from app.repositories.data_loader import DatasetRepository


class RecommendationService:
    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository

    @staticmethod
    def _score(item: dict, interest_tags: list[str]) -> float:
        rating = float(item.get("rating") or 0.0)
        heat = float(item.get("heat") or 0.0)
        tags = set(item.get("tags", []))
        interest_bonus = len(tags & set(interest_tags)) * 8
        return rating * 15 + heat * 0.1 + interest_bonus

    def recommend_destinations(self, top_k: int, category: str | None, interest_tags: list[str]) -> list[dict]:
        destinations = self.repository.destinations()
        if category:
            destinations = [item for item in destinations if item["category"] == category]
        selector = TopKSelector(lambda item: self._score(item, interest_tags))
        return selector.select(destinations, top_k)

    def featured_destinations(self, top_k: int | None = None) -> list[dict]:
        featured = self.repository.featured_destinations()
        if top_k is None:
            return featured
        selector = TopKSelector(lambda item: self._score(item, item.get("tags", [])))
        return selector.select(featured, top_k)

    def recommend_foods(
        self,
        top_k: int | None,
        cuisine: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        radius: float = 5.0,
    ) -> list[dict]:
        foods = self.repository.foods()
        if cuisine:
            foods = [item for item in foods if item["cuisine"] == cuisine]
        if lat is not None and lng is not None:
            foods = self._filter_by_distance(foods, lat, lng, radius)
        if top_k is None:
            return foods
        selector = TopKSelector(lambda item: float(item.get("rating") or 0.0) * 10 + float(item.get("heat") or 0.0))
        return selector.select(foods, top_k)

    @staticmethod
    def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        import math

        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _filter_by_distance(self, foods: list[dict], lat: float, lng: float, radius: float) -> list[dict]:
        result = []
        for item in foods:
            item_lat = item.get("latitude")
            item_lng = item.get("longitude")
            if item_lat is None or item_lng is None:
                continue
            dist = self._haversine_km(lat, lng, float(item_lat), float(item_lng))
            if dist <= radius:
                enriched = dict(item)
                enriched["distance_km"] = round(dist, 2)
                result.append(enriched)
        result.sort(key=lambda x: x.get("distance_km", float("inf")))
        return result
