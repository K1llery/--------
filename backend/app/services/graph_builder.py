from __future__ import annotations

import logging

from app.algorithms.graph import Graph
from app.repositories.data_loader import DatasetRepository

logger = logging.getLogger(__name__)


class GraphBuilder:
    """负责从 Repository 数据构建场景图，支持跨服务共享。"""

    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository
        self._graphs: dict[str, Graph] = {}
        self._name_maps: dict[str, dict[str, str]] = {}
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
    def _edge_modes(raw_modes: list[str]) -> set[str]:
        modes = set(raw_modes)
        if modes & {"mixed", "shuttle", "taxi"}:
            modes.add("taxi")
        return modes

    def get_scene_graph(self, scene_name: str) -> Graph:
        """获取或构建指定场景的图实例。"""
        if scene_name in self._graphs:
            return self._graphs[scene_name]
        graph = Graph()
        facilities = [item for item in self.repository.facilities() if item["scene_name"] == scene_name]
        scenes = [item for item in self.repository.scenes() if item["name"] == scene_name]
        if scenes:
            for node in scenes[0]["nodes"]:
                graph.add_node(
                    node["code"],
                    node["latitude"],
                    node["longitude"],
                    scenic_score=self._node_scenic_score(node["name"]),
                )
        for facility in facilities:
            graph.add_node(
                facility["code"],
                facility["latitude"],
                facility["longitude"],
                scenic_score=self._node_scenic_score(facility["name"], facility.get("facility_type")),
            )
        for edge in self.repository.edges():
            if edge["scene_name"] != scene_name:
                continue
            taxi_speed = edge.get("taxi_speed", edge.get("shuttle_speed", 4.8))
            graph.add_edge(
                edge["source_code"],
                edge["target_code"],
                edge["distance"],
                edge.get("congestion", 1.0),
                {
                    "walk": edge.get("walk_speed", 1.1),
                    "bike": edge.get("bike_speed", 3.5),
                    "shuttle": edge.get("shuttle_speed", 4.8),
                    "taxi": taxi_speed,
                    "mixed": max(
                        edge.get("walk_speed", 1.1),
                        edge.get("bike_speed", 3.5),
                        edge.get("shuttle_speed", 4.8),
                        taxi_speed,
                    ),
                },
                self._edge_modes(edge.get("allowed_modes", ["walk"])),
            )
        self._graphs[scene_name] = graph
        logger.debug("Built graph for scene %s: %d nodes", scene_name, len(graph.coords))
        return graph

    def get_name_map(self, scene_name: str) -> dict[str, str]:
        """获取 code -> name 映射。"""
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
