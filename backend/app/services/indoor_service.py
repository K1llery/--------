from __future__ import annotations

import heapq
from dataclasses import dataclass

from app.repositories.data_loader import DatasetRepository


@dataclass(slots=True)
class IndoorEdge:
    source: str
    target: str
    distance: float
    kind: str
    wait_seconds: float


class IndoorNavigationService:
    WALK_SPEED = 1.25
    STAIRS_SPEED = 0.9
    ELEVATOR_SPEED = 1.8

    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository
        self._buildings = {item["building_code"]: item for item in repository.indoors()}

    def list_buildings(self) -> list[dict]:
        items: list[dict] = []
        for building in self._buildings.values():
            nodes = building.get("nodes", [])
            items.append(
                {
                    "building_code": building["building_code"],
                    "building_name": building.get("building_name", building["building_code"]),
                    "scene_name": building.get("scene_name"),
                    "node_count": len(nodes),
                    "floors": sorted({int(node.get("floor", 1)) for node in nodes}),
                    "nodes": nodes,
                }
            )
        return items

    def _building_or_raise(self, building_code: str) -> dict:
        building = self._buildings.get(building_code)
        if building is None:
            raise ValueError("室内建筑不存在，请检查 building_code。")
        return building

    @staticmethod
    def _edge_seconds(edge: IndoorEdge) -> float:
        if edge.kind == "stairs":
            speed = IndoorNavigationService.STAIRS_SPEED
        elif edge.kind == "elevator":
            speed = IndoorNavigationService.ELEVATOR_SPEED
        else:
            speed = IndoorNavigationService.WALK_SPEED
        return edge.distance / max(speed, 0.1) + edge.wait_seconds

    @classmethod
    def _edge_weight(cls, edge: IndoorEdge, strategy: str) -> float:
        if strategy == "distance":
            return edge.distance
        seconds = cls._edge_seconds(edge)
        if strategy == "accessible":
            return seconds + (120.0 if edge.kind == "stairs" else 0.0)
        return seconds

    def _build_graph(self, building: dict, mobility_mode: str) -> tuple[dict[str, list[IndoorEdge]], dict[tuple[str, str], IndoorEdge]]:
        adjacency: dict[str, list[IndoorEdge]] = {}
        edge_lookup: dict[tuple[str, str], IndoorEdge] = {}

        def add_edge(source: str, target: str, distance: float, kind: str, wait_seconds: float) -> None:
            edge = IndoorEdge(source=source, target=target, distance=distance, kind=kind, wait_seconds=wait_seconds)
            adjacency.setdefault(source, []).append(edge)
            edge_lookup[(source, target)] = edge

        for edge in building.get("edges", []):
            kind = edge.get("kind", "walk")
            if mobility_mode == "wheelchair" and kind == "stairs":
                continue

            source = edge["source"]
            target = edge["target"]
            distance = float(edge.get("distance", 0.0))
            wait_seconds = float(edge.get("wait_seconds", 0.0))
            add_edge(source, target, distance, kind, wait_seconds)

            if edge.get("bidirectional", True):
                add_edge(target, source, distance, kind, wait_seconds)

        return adjacency, edge_lookup

    @staticmethod
    def _reconstruct_path(parent: dict[str, str | None], end_node: str) -> list[str]:
        path: list[str] = []
        cursor: str | None = end_node
        while cursor is not None:
            path.append(cursor)
            cursor = parent.get(cursor)
        path.reverse()
        return path

    def _shortest_path(
        self,
        adjacency: dict[str, list[IndoorEdge]],
        start_node: str,
        end_node: str,
        strategy: str,
    ) -> list[str]:
        queue: list[tuple[float, str]] = [(0.0, start_node)]
        dist: dict[str, float] = {start_node: 0.0}
        parent: dict[str, str | None] = {start_node: None}

        while queue:
            current_cost, node = heapq.heappop(queue)
            if current_cost > dist.get(node, float("inf")):
                continue
            if node == end_node:
                return self._reconstruct_path(parent, end_node)

            for edge in adjacency.get(node, []):
                next_cost = current_cost + self._edge_weight(edge, strategy)
                if next_cost < dist.get(edge.target, float("inf")):
                    dist[edge.target] = next_cost
                    parent[edge.target] = node
                    heapq.heappush(queue, (next_cost, edge.target))

        return []

    @staticmethod
    def _instruction_for_edge(from_node: dict, to_node: dict, edge: IndoorEdge) -> str:
        from_name = from_node.get("name", edge.source)
        to_name = to_node.get("name", edge.target)
        from_floor = int(from_node.get("floor", 1))
        to_floor = int(to_node.get("floor", 1))

        if edge.kind == "elevator" and from_floor != to_floor:
            return f"乘坐电梯从{from_floor}层前往{to_floor}层，抵达{to_name}。"
        if edge.kind == "stairs" and from_floor != to_floor:
            direction = "上" if to_floor > from_floor else "下"
            return f"通过楼梯向{direction}到{to_floor}层，抵达{to_name}。"
        return f"从{from_name}步行至{to_name}。"

    def _build_steps(self, path: list[str], nodes: dict[str, dict], edge_lookup: dict[tuple[str, str], IndoorEdge]) -> tuple[list[dict], float, float]:
        steps: list[dict] = []
        total_distance = 0.0
        total_seconds = 0.0

        for index, (source, target) in enumerate(zip(path, path[1:]), start=1):
            edge = edge_lookup.get((source, target))
            if edge is None:
                continue
            from_node = nodes[source]
            to_node = nodes[target]
            segment_seconds = self._edge_seconds(edge)

            total_distance += edge.distance
            total_seconds += segment_seconds
            steps.append(
                {
                    "index": index,
                    "from_node_code": source,
                    "from_name": from_node.get("name", source),
                    "from_floor": int(from_node.get("floor", 1)),
                    "to_node_code": target,
                    "to_name": to_node.get("name", target),
                    "to_floor": int(to_node.get("floor", 1)),
                    "connector": edge.kind,
                    "distance_m": round(edge.distance, 1),
                    "estimated_seconds": round(segment_seconds, 1),
                    "instruction": self._instruction_for_edge(from_node, to_node, edge),
                }
            )

        return steps, total_distance, total_seconds

    def plan_route(
        self,
        building_code: str,
        start_node_code: str,
        end_node_code: str,
        strategy: str = "time",
        mobility_mode: str = "normal",
    ) -> dict:
        building = self._building_or_raise(building_code)
        nodes = {node["code"]: node for node in building.get("nodes", [])}

        if start_node_code not in nodes:
            raise ValueError("室内起点不存在，请检查 start_node_code。")
        if end_node_code not in nodes:
            raise ValueError("室内终点不存在，请检查 end_node_code。")

        if strategy not in {"distance", "time", "accessible"}:
            strategy = "time"
        if mobility_mode not in {"normal", "wheelchair"}:
            mobility_mode = "normal"

        if start_node_code == end_node_code:
            return {
                "building_code": building_code,
                "building_name": building.get("building_name", building_code),
                "path_node_codes": [start_node_code],
                "path_node_names": [nodes[start_node_code].get("name", start_node_code)],
                "strategy": strategy,
                "mobility_mode": mobility_mode,
                "total_distance_m": 0.0,
                "estimated_seconds": 0.0,
                "summary": "起点与终点一致，无需移动。",
                "steps": [],
            }

        adjacency, edge_lookup = self._build_graph(building, mobility_mode)
        path = self._shortest_path(adjacency, start_node_code, end_node_code, strategy)
        if not path:
            raise ValueError("未找到可达的室内路线，请尝试切换策略或节点。")

        steps, total_distance, total_seconds = self._build_steps(path, nodes, edge_lookup)
        summary = (
            f"共{len(steps)}段室内路径，约{round(total_distance, 1)}米，"
            f"预计{round(total_seconds, 1)}秒。"
        )

        return {
            "building_code": building_code,
            "building_name": building.get("building_name", building_code),
            "path_node_codes": path,
            "path_node_names": [nodes[node_code].get("name", node_code) for node_code in path],
            "strategy": strategy,
            "mobility_mode": mobility_mode,
            "total_distance_m": round(total_distance, 1),
            "estimated_seconds": round(total_seconds, 1),
            "summary": summary,
            "steps": steps,
        }
