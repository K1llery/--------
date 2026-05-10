from __future__ import annotations

import logging

from app.algorithms.graph import Graph
from app.repositories.data_loader import DatasetRepository

logger = logging.getLogger(__name__)


class GraphBuilder:
    """负责从 Repository 的场景点位与 edges 集合构建可复用道路图。"""

    _DEFAULT_SPEEDS = {"walk": 1.1, "bike": 3.5, "shuttle": 4.8, "taxi": 4.8}

    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository
        self._graphs: dict[str, Graph] = {}
        self._name_maps: dict[str, dict[str, str]] = {}
        self._route_node_types: dict[str, dict[str, str]] = {}
        self._scene_code_sets: dict[str, set[str]] = {}

    @staticmethod
    def _node_scenic_score(name: str, raw_type: str | None = None) -> float:
        scenic_keywords = ("门", "湖", "桥", "殿", "宫", "园", "亭", "馆", "阁", "景", "广场", "主楼", "图书馆")
        if any(keyword in name for keyword in scenic_keywords):
            return 0.7
        if raw_type in {"museum", "viewpoint", "artwork", "visitor_center"}:
            return 0.55
        return 0.15

    def _scene_points(self, scene_name: str) -> tuple[list[dict], list[dict]]:
        scene = next((item for item in self.repository.scenes() if item["name"] == scene_name), {"nodes": []})
        facilities = [item for item in self.repository.facilities() if item["scene_name"] == scene_name]
        return scene.get("nodes", []), facilities

    @classmethod
    def _edge_speeds(cls, edge: dict) -> dict[str, float]:
        return {
            "walk": float(edge.get("walk_speed") or cls._DEFAULT_SPEEDS["walk"]),
            "bike": float(edge.get("bike_speed") or cls._DEFAULT_SPEEDS["bike"]),
            "shuttle": float(edge.get("shuttle_speed") or cls._DEFAULT_SPEEDS["shuttle"]),
            "taxi": float(edge.get("taxi_speed") or edge.get("shuttle_speed") or cls._DEFAULT_SPEEDS["taxi"]),
        }

    @staticmethod
    def _edge_modes(edge: dict) -> set[str]:
        raw_modes = edge.get("allowed_modes") or ["walk"]
        return {str(mode) for mode in raw_modes if str(mode)}

    def _add_repository_edges(self, scene_name: str, graph: Graph) -> int:
        added = 0
        for edge in self.repository.edges():
            if edge.get("scene_name") != scene_name:
                continue
            source = edge.get("source_code")
            target = edge.get("target_code")
            if not isinstance(source, str) or not isinstance(target, str):
                continue
            if source not in graph.coords or target not in graph.coords:
                logger.warning("Skip edge with unknown endpoint in %s: %s -> %s", scene_name, source, target)
                continue
            graph.add_edge(
                source,
                target,
                float(edge.get("distance") or edge.get("distance_m") or 1.0),
                float(edge.get("congestion") or 1.0),
                self._edge_speeds(edge),
                self._edge_modes(edge),
            )
            added += 1
        return added

    def get_scene_graph(self, scene_name: str) -> Graph:
        """获取或构建指定场景的图实例。"""
        if scene_name in self._graphs:
            return self._graphs[scene_name]
        graph = Graph()
        names: dict[str, str] = {}
        route_node_types: dict[str, str] = {}
        scene_nodes, facilities = self._scene_points(scene_name)
        for node in scene_nodes:
            graph.add_node(
                node["code"],
                node["latitude"],
                node["longitude"],
                scenic_score=self._node_scenic_score(node["name"]),
            )
            names[node["code"]] = node["name"]
            route_node_types[node["code"]] = "place"
        for facility in facilities:
            graph.add_node(
                facility["code"],
                facility["latitude"],
                facility["longitude"],
                scenic_score=self._node_scenic_score(facility["name"], facility.get("facility_type")),
            )
            names[facility["code"]] = facility["name"]
            route_node_types[facility["code"]] = "facility"
        edge_count = self._add_repository_edges(scene_name, graph)
        self._graphs[scene_name] = graph
        self._name_maps[scene_name] = {**self._name_maps.get(scene_name, {}), **names}
        self._route_node_types[scene_name] = route_node_types
        self._scene_code_sets[scene_name] = set(graph.coords)
        logger.debug("Built graph for scene %s: %d nodes, %d edges", scene_name, len(graph.coords), edge_count)
        return graph

    def get_name_map(self, scene_name: str) -> dict[str, str]:
        """获取 code -> name 映射。"""
        if scene_name in self._name_maps:
            return self._name_maps[scene_name]
        self.get_scene_graph(scene_name)
        if scene_name in self._name_maps:
            return self._name_maps[scene_name]
        scene = next((item for item in self.repository.scenes() if item["name"] == scene_name), {"nodes": []})
        names = {item["code"]: item["name"] for item in scene.get("nodes", [])}
        names.update(
            {item["code"]: item["name"] for item in self.repository.facilities() if item["scene_name"] == scene_name}
        )
        self._name_maps[scene_name] = names
        return names

    def get_scene_codes(self, scene_name: str) -> set[str]:
        """获取场景中所有可用节点代码。"""
        if scene_name in self._scene_code_sets:
            return self._scene_code_sets[scene_name]
        graph = self.get_scene_graph(scene_name)
        codes = set(graph.coords)
        self._scene_code_sets[scene_name] = codes
        return codes

    def get_route_node_type(self, scene_name: str, code: str) -> str:
        self.get_scene_graph(scene_name)
        return self._route_node_types.get(scene_name, {}).get(code, "place")

    def route_nodes_for_path(self, scene_name: str, path_codes: list[str]) -> list[dict]:
        graph = self.get_scene_graph(scene_name)
        names = self.get_name_map(scene_name)
        node_types = self._route_node_types.get(scene_name, {})
        route_nodes = []
        for code in path_codes:
            coords = graph.coords.get(code)
            if coords is None:
                continue
            latitude, longitude = coords
            route_nodes.append(
                {
                    "code": code,
                    "name": names.get(code, "道路节点"),
                    "latitude": latitude,
                    "longitude": longitude,
                    "route_node_type": node_types.get(code, "place"),
                }
            )
        return route_nodes

    def route_edges_for_path(self, scene_name: str, path_codes: list[str], transport_mode: str) -> list[dict]:
        graph = self.get_scene_graph(scene_name)
        names = self.get_name_map(scene_name)
        route_edges = []
        for index, (source, target) in enumerate(zip(path_codes, path_codes[1:]), start=1):
            edge = graph.edge_between(source, target)
            if edge is None:
                continue
            selected_mode = graph.selected_mode_for_edge(edge, transport_mode)
            route_edges.append(
                {
                    "index": index,
                    "source_code": source,
                    "source_name": names.get(source, source),
                    "target_code": target,
                    "target_name": names.get(target, target),
                    "distance_m": round(edge.distance, 1),
                    "congestion": round(edge.congestion, 2),
                    "allowed_modes": sorted(edge.modes),
                    "selected_mode": selected_mode,
                    "speed_mps": round(edge.transport_speeds.get(selected_mode, 0.0), 2),
                    "estimated_minutes": round(graph.edge_travel_seconds(edge, transport_mode) / 60, 1),
                    "transport_speeds": {key: round(value, 2) for key, value in edge.transport_speeds.items()},
                }
            )
        return route_edges
