from __future__ import annotations

from app.repositories.data_loader import DatasetRepository
from app.services.routing_service import RoutePlanningService


class NearbyFacilityService:
    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository
        self.route_service = RoutePlanningService(repository)

    def nearby(self, scene_name: str, origin_code: str, category: str | None = None, radius: float = 1200.0) -> list[dict]:
        facilities = [item for item in self.repository.facilities() if item["scene_name"] == scene_name]
        if category:
            facilities = [item for item in facilities if item["facility_type"] == category]

        graph = self.route_service._scene_graph(scene_name)
        distances = graph.shortest_distances(origin_code, strategy="distance", transport_mode="walk")

        ranked = []
        for facility in facilities:
            distance = distances.get(facility["code"])
            if distance is None or distance == float("inf"):
                continue
            if distance <= radius:
                ranked.append({**facility, "graph_distance": round(distance, 1)})
        ranked.sort(key=lambda item: item["graph_distance"])
        return ranked
