from __future__ import annotations

from app.repositories.data_loader import DatasetRepository
from app.services.facility_types import facility_type_label, normalize_facility_type
from app.services.graph_builder import GraphBuilder


class NearbyFacilityService:
    def __init__(self, repository: DatasetRepository, graph_builder: GraphBuilder | None = None) -> None:
        self.repository = repository
        self.graph_builder = graph_builder or GraphBuilder(repository)

    @staticmethod
    def _decorate_facility(facility: dict, distance: float, transport_mode: str) -> dict:
        normalized_type = normalize_facility_type(facility.get("facility_type"), facility.get("name", ""))
        return {
            **facility,
            "normalized_type": normalized_type,
            "facility_label": facility_type_label(normalized_type),
            "graph_distance": round(distance, 1),
            "transport_mode": transport_mode,
        }

    def nearby(
        self,
        scene_name: str,
        origin_code: str,
        category: str | None = None,
        radius: float = 1200.0,
        transport_mode: str = "walk",
        strategy: str = "distance",
    ) -> list[dict]:
        facilities = [item for item in self.repository.facilities() if item["scene_name"] == scene_name]
        if category:
            normalized_category = normalize_facility_type(category)
            facilities = [
                item
                for item in facilities
                if normalize_facility_type(item.get("facility_type"), item.get("name", "")) == normalized_category
            ]

        graph = self.graph_builder.get_scene_graph(scene_name)
        distances = graph.shortest_distances(origin_code, strategy=strategy, transport_mode=transport_mode)

        ranked = []
        for facility in facilities:
            distance = distances.get(facility["code"])
            if distance is None or distance == float("inf"):
                continue
            if distance <= radius:
                ranked.append(self._decorate_facility(facility, distance, transport_mode))
        ranked.sort(key=lambda item: item["graph_distance"])
        return ranked
