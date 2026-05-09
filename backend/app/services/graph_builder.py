from __future__ import annotations

import logging
import math

from app.algorithms.graph import Graph
from app.repositories.data_loader import DatasetRepository

logger = logging.getLogger(__name__)


class GraphBuilder:
    """负责从 Repository 数据构建场景图，支持跨服务共享。"""

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

    @staticmethod
    def _road_code(scene_name: str, row: int, col: int) -> str:
        return f"__road__{scene_name}_{row}_{col}"

    @staticmethod
    def _geo_distance_m(left_lat: float, left_lon: float, right_lat: float, right_lon: float) -> float:
        mean_lat = math.radians((left_lat + right_lat) / 2)
        lat_m = (left_lat - right_lat) * 111_320
        lon_m = (left_lon - right_lon) * 111_320 * max(math.cos(mean_lat), 0.2)
        return math.hypot(lat_m, lon_m)

    @staticmethod
    def _cluster_axis(values: list[float], tolerance: float = 0.00065) -> list[float]:
        if not values:
            return []
        clusters: list[list[float]] = []
        for value in sorted(values):
            if not clusters or abs(value - (sum(clusters[-1]) / len(clusters[-1]))) > tolerance:
                clusters.append([value])
            else:
                clusters[-1].append(value)
        return [sum(cluster) / len(cluster) for cluster in clusters]

    @staticmethod
    def _road_speeds() -> dict[str, float]:
        return {"walk": 1.1, "bike": 3.5, "shuttle": 4.8, "taxi": 4.8, "mixed": 4.8}

    @staticmethod
    def _access_speeds() -> dict[str, float]:
        return {"walk": 1.1, "bike": 2.2, "shuttle": 2.6, "taxi": 2.6, "mixed": 2.6}

    def _scene_points(self, scene_name: str) -> tuple[list[dict], list[dict]]:
        scene = next((item for item in self.repository.scenes() if item["name"] == scene_name), {"nodes": []})
        facilities = [item for item in self.repository.facilities() if item["scene_name"] == scene_name]
        return scene.get("nodes", []), facilities

    def _add_road_layer(
        self,
        scene_name: str,
        graph: Graph,
        points: list[dict],
        names: dict[str, str],
        route_node_types: dict[str, str],
    ) -> None:
        latitudes = self._cluster_axis([item["latitude"] for item in points])
        longitudes = self._cluster_axis([item["longitude"] for item in points])
        if len(latitudes) < 2 or len(longitudes) < 2:
            return

        road_codes: dict[tuple[int, int], str] = {}
        for row, latitude in enumerate(latitudes):
            for col, longitude in enumerate(longitudes):
                code = self._road_code(scene_name, row, col)
                graph.add_node(code, latitude, longitude, scenic_score=0.0)
                road_codes[(row, col)] = code
                names[code] = "道路节点"
                route_node_types[code] = "road"

        modes = {"walk", "bike", "taxi", "shuttle", "mixed"}
        speeds = self._road_speeds()
        for row in range(len(latitudes)):
            for col in range(len(longitudes)):
                source = road_codes[(row, col)]
                neighbors = []
                if row + 1 < len(latitudes):
                    neighbors.append(road_codes[(row + 1, col)])
                if col + 1 < len(longitudes):
                    neighbors.append(road_codes[(row, col + 1)])
                source_lat, source_lon = graph.coords[source]
                for target in neighbors:
                    target_lat, target_lon = graph.coords[target]
                    distance = round(self._geo_distance_m(source_lat, source_lon, target_lat, target_lon), 1)
                    for left, right in ((source, target), (target, source)):
                        graph.add_edge(left, right, max(distance, 8.0), 0.78, speeds, modes)

        road_items = [
            (code, graph.coords[code][0], graph.coords[code][1]) for code in road_codes.values() if code in graph.coords
        ]
        access_speeds = self._access_speeds()
        for point in points:
            nearest_code, nearest_distance = min(
                (
                    (code, self._geo_distance_m(point["latitude"], point["longitude"], latitude, longitude))
                    for code, latitude, longitude in road_items
                ),
                key=lambda item: item[1],
            )
            distance = max(round(nearest_distance, 1), 6.0)
            for left, right in ((point["code"], nearest_code), (nearest_code, point["code"])):
                graph.add_edge(left, right, distance, 0.72, access_speeds, modes)

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
        self._add_road_layer(scene_name, graph, [*scene_nodes, *facilities], names, route_node_types)
        self._graphs[scene_name] = graph
        self._name_maps[scene_name] = {**self._name_maps.get(scene_name, {}), **names}
        self._route_node_types[scene_name] = route_node_types
        logger.debug("Built graph for scene %s: %d nodes", scene_name, len(graph.coords))
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
        scene = next((item for item in self.repository.scenes() if item["name"] == scene_name), {"nodes": []})
        codes = {item["code"] for item in scene.get("nodes", [])}
        codes.update({item["code"] for item in self.repository.facilities() if item["scene_name"] == scene_name})
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
