from __future__ import annotations

from app.algorithms.graph import Graph
from app.algorithms.tsp import held_karp, nearest_neighbor_two_opt
from app.repositories.data_loader import DatasetRepository


class RoutePlanningService:
    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository
        self._graphs: dict[str, Graph] = {}

    @staticmethod
    def _strategy_label(strategy: str) -> str:
        mapping = {
            "distance": "最短距离",
            "time": "最快到达",
            "congestion": "避开拥堵",
            "scenic": "轻松逛/打卡优先",
        }
        return mapping.get(strategy, "最短距离")

    @classmethod
    def _strategy_explanation(cls, strategy: str) -> str:
        mapping = {
            "distance": "这条路线优先压缩步行距离，适合明确赶往目标点。",
            "time": "这条路线优先减少预计耗时，尽量走更快、更顺的连通边。",
            "congestion": "这条路线主动绕开高拥堵边，整体可能略绕，但通过体验更稳定。",
            "scenic": "这条路线会尽量串联更有看点的节点，适合边走边逛。",
        }
        return mapping.get(strategy, "已按默认策略生成路线。")

    @staticmethod
    def _node_scenic_score(name: str, raw_type: str | None = None) -> float:
        scenic_keywords = ("门", "湖", "桥", "殿", "宫", "园", "亭", "馆", "阁", "景", "广场", "主楼", "图书馆")
        if any(keyword in name for keyword in scenic_keywords):
            return 0.7
        if raw_type in {"museum", "viewpoint", "artwork", "visitor_center"}:
            return 0.55
        return 0.15

    def _scene_graph(self, scene_name: str) -> Graph:
        if scene_name in self._graphs:
            return self._graphs[scene_name]
        graph = Graph()
        facilities = [item for item in self.repository.facilities() if item["scene_name"] == scene_name]
        scenes = [item for item in self.repository.scenes() if item["name"] == scene_name]
        if scenes:
            for node in scenes[0]["nodes"]:
                graph.add_node(node["code"], node["latitude"], node["longitude"], scenic_score=self._node_scenic_score(node["name"]))
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
            graph.add_edge(
                edge["source_code"],
                edge["target_code"],
                edge["distance"],
                edge.get("congestion", 1.0),
                {
                    "walk": edge.get("walk_speed", 1.1),
                    "bike": edge.get("bike_speed", 3.5),
                    "shuttle": edge.get("shuttle_speed", 4.8),
                    "mixed": max(edge.get("walk_speed", 1.1), edge.get("bike_speed", 3.5), edge.get("shuttle_speed", 4.8)),
                },
                set(edge.get("allowed_modes", ["walk"])),
            )
        self._graphs[scene_name] = graph
        return graph

    def _name_map(self, scene_name: str) -> dict[str, str]:
        scene = next((item for item in self.repository.scenes() if item["name"] == scene_name), {"nodes": []})
        names = {item["code"]: item["name"] for item in scene.get("nodes", [])}
        names.update({item["code"]: item["name"] for item in self.repository.facilities() if item["scene_name"] == scene_name})
        return names

    def _expand_segments(self, graph: Graph, ordered_codes: list[str], strategy: str, transport_mode: str) -> list[str]:
        expanded: list[str] = []
        for left, right in zip(ordered_codes, ordered_codes[1:]):
            segment, _ = graph.shortest_path(left, right, strategy=strategy, transport_mode=transport_mode)
            if not segment:
                continue
            if not expanded:
                expanded.extend(segment)
            else:
                expanded.extend(segment[1:])
        return expanded or ordered_codes

    def _format_single(self, scene_name: str, path_codes: list[str], strategy: str, transport_mode: str) -> dict:
        graph = self._scene_graph(scene_name)
        names = self._name_map(scene_name)
        metrics = graph.path_metrics(path_codes, transport_mode)
        return {
            "path_codes": path_codes,
            "path_names": [names.get(code, code) for code in path_codes],
            "total_distance_m": metrics["total_distance_m"],
            "estimated_minutes": metrics["estimated_minutes"],
            "strategy": strategy,
            "strategy_label": self._strategy_label(strategy),
            "explanation": self._strategy_explanation(strategy),
            "average_congestion": metrics["average_congestion"],
            "scenic_score": metrics["scenic_score"],
        }

    def plan_single(self, scene_name: str, start_code: str, end_code: str, strategy: str, transport_mode: str) -> dict:
        graph = self._scene_graph(scene_name)
        if strategy == "astar":
            path_codes, _ = graph.a_star(start_code, end_code, transport_mode)
            strategy = "distance"
        else:
            path_codes, _ = graph.shortest_path(start_code, end_code, strategy, transport_mode)
        result = self._format_single(scene_name, path_codes, strategy, transport_mode)
        alternatives: list[dict] = []
        for alt_strategy in ("time", "scenic"):
            if alt_strategy == strategy:
                continue
            alt_path, _ = graph.shortest_path(start_code, end_code, alt_strategy, transport_mode)
            if not alt_path or alt_path == path_codes:
                continue
            alternatives.append(self._format_single(scene_name, alt_path, alt_strategy, transport_mode))
        result["alternatives"] = alternatives[:2]
        return result

    def plan_multi(self, scene_name: str, start_code: str, target_codes: list[str], strategy: str, transport_mode: str) -> dict:
        graph = self._scene_graph(scene_name)
        normalized_targets = [code for code in dict.fromkeys(target_codes) if code != start_code]

        if not normalized_targets:
            ordered_stops = [start_code]
            full_path = [start_code]
            optimization_label = "无目标点"
        elif len(normalized_targets) <= 8:
            ordered_stops, _ = held_karp(graph, start_code, normalized_targets, strategy, transport_mode)
            optimization_label = "精确闭环求解"
            full_path = self._expand_segments(graph, ordered_stops, strategy, transport_mode)
        else:
            ordered_stops, _ = nearest_neighbor_two_opt(graph, start_code, normalized_targets, strategy, transport_mode)
            optimization_label = "快速闭环近似"
            full_path = self._expand_segments(graph, ordered_stops, strategy, transport_mode)

        metrics = graph.path_metrics(full_path, transport_mode)
        names = self._name_map(scene_name)

        explanation = (
            f"{self._strategy_explanation(strategy)} 未提供额外目标点，返回起点信息。"
            if optimization_label == "无目标点"
            else f"{self._strategy_explanation(strategy)} 当前采用{optimization_label}组织多点闭环。"
        )

        return {
            "path_codes": full_path,
            "path_names": [names.get(code, code) for code in full_path],
            "ordered_stop_codes": ordered_stops,
            "ordered_stop_names": [names.get(code, code) for code in ordered_stops],
            "total_distance_m": metrics["total_distance_m"],
            "estimated_minutes": metrics["estimated_minutes"],
            "strategy": strategy,
            "strategy_label": self._strategy_label(strategy),
            "optimization_label": optimization_label,
            "explanation": explanation,
        }
