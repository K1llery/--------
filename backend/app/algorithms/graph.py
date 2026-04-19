from __future__ import annotations

import heapq
import math
from dataclasses import dataclass


@dataclass(slots=True)
class Edge:
    target: str
    distance: float
    congestion: float
    transport_speeds: dict[str, float]
    modes: set[str]


class Graph:
    def __init__(self) -> None:
        self.adj: dict[str, list[Edge]] = {}
        self.coords: dict[str, tuple[float, float]] = {}
        self.node_scores: dict[str, float] = {}

    def add_node(self, code: str, lat: float, lon: float, scenic_score: float = 0.0) -> None:
        self.coords[code] = (lat, lon)
        self.node_scores[code] = scenic_score
        self.adj.setdefault(code, [])

    def add_edge(
        self,
        source: str,
        target: str,
        distance: float,
        congestion: float,
        transport_speeds: dict[str, float],
        modes: set[str],
    ) -> None:
        self.adj.setdefault(source, []).append(Edge(target, distance, congestion, transport_speeds, modes))

    @staticmethod
    def _mode_allowed(edge: Edge, transport_mode: str) -> bool:
        return transport_mode == "mixed" or transport_mode in edge.modes or "mixed" in edge.modes

    def _speed_for_mode(self, edge: Edge, transport_mode: str) -> float:
        if transport_mode == "mixed":
            return max(edge.transport_speeds.values(), default=1.0)
        return edge.transport_speeds.get(transport_mode) or edge.transport_speeds.get("walk") or max(edge.transport_speeds.values(), default=1.0)

    def edge_travel_seconds(self, edge: Edge, transport_mode: str) -> float:
        speed = max(self._speed_for_mode(edge, transport_mode), 0.1)
        return edge.distance / speed * max(edge.congestion, 0.45)

    def _edge_weight(self, source: str, edge: Edge, strategy: str, transport_mode: str) -> float:
        travel_seconds = self.edge_travel_seconds(edge, transport_mode)
        scenic_bonus = (self.node_scores.get(source, 0.0) + self.node_scores.get(edge.target, 0.0)) * 38
        if strategy == "time":
            return travel_seconds
        if strategy == "congestion":
            return travel_seconds * (1 + max(edge.congestion - 0.8, 0) * 3.5) + edge.distance * 0.05
        if strategy == "scenic":
            return max(edge.distance * (1 + edge.congestion * 0.12) - scenic_bonus, 8.0)
        return edge.distance

    def _dijkstra(
        self,
        start: str,
        strategy: str = "distance",
        transport_mode: str = "walk",
        end: str | None = None,
    ) -> tuple[dict[str, float], dict[str, str | None]]:
        queue: list[tuple[float, str]] = [(0.0, start)]
        dist = {start: 0.0}
        parent: dict[str, str | None] = {start: None}

        while queue:
            current_cost, node = heapq.heappop(queue)
            if current_cost > dist.get(node, float("inf")):
                continue
            if end is not None and node == end:
                break
            for edge in self.adj.get(node, []):
                if not self._mode_allowed(edge, transport_mode):
                    continue
                weight = self._edge_weight(node, edge, strategy, transport_mode)
                next_cost = current_cost + weight
                if next_cost < dist.get(edge.target, float("inf")):
                    dist[edge.target] = next_cost
                    parent[edge.target] = node
                    heapq.heappush(queue, (next_cost, edge.target))
        return dist, parent

    def shortest_path(self, start: str, end: str, strategy: str = "distance", transport_mode: str = "walk") -> tuple[list[str], float]:
        dist, parent = self._dijkstra(start, strategy=strategy, transport_mode=transport_mode, end=end)
        if end not in dist:
            return [], float("inf")
        path = []
        cursor: str | None = end
        while cursor is not None:
            path.append(cursor)
            cursor = parent[cursor]
        path.reverse()
        return path, dist[end]

    def shortest_distances(self, start: str, strategy: str = "distance", transport_mode: str = "walk") -> dict[str, float]:
        dist, _ = self._dijkstra(start, strategy=strategy, transport_mode=transport_mode)
        return dist

    def a_star(self, start: str, end: str, transport_mode: str = "walk") -> tuple[list[str], float]:
        def heuristic(node: str) -> float:
            lat1, lon1 = self.coords.get(node, (0.0, 0.0))
            lat2, lon2 = self.coords.get(end, (0.0, 0.0))
            return math.dist((lat1, lon1), (lat2, lon2))

        queue: list[tuple[float, float, str]] = [(heuristic(start), 0.0, start)]
        cost_so_far = {start: 0.0}
        parent: dict[str, str | None] = {start: None}

        while queue:
            _, current_cost, node = heapq.heappop(queue)
            if node == end:
                break
            for edge in self.adj.get(node, []):
                if not self._mode_allowed(edge, transport_mode):
                    continue
                next_cost = current_cost + edge.distance
                if next_cost < cost_so_far.get(edge.target, float("inf")):
                    cost_so_far[edge.target] = next_cost
                    parent[edge.target] = node
                    heapq.heappush(queue, (next_cost + heuristic(edge.target), next_cost, edge.target))

        if end not in parent:
            return [], float("inf")
        path = []
        cursor: str | None = end
        while cursor is not None:
            path.append(cursor)
            cursor = parent[cursor]
        path.reverse()
        return path, cost_so_far[end]

    def path_metrics(self, path: list[str], transport_mode: str = "walk") -> dict[str, float]:
        total_distance = 0.0
        total_seconds = 0.0
        total_congestion = 0.0
        scenic_score = 0.0
        steps = 0
        for source, target in zip(path, path[1:]):
            edge = next((item for item in self.adj.get(source, []) if item.target == target), None)
            if edge is None:
                continue
            total_distance += edge.distance
            total_seconds += self.edge_travel_seconds(edge, transport_mode)
            total_congestion += edge.congestion
            scenic_score += self.node_scores.get(target, 0.0)
            steps += 1
        return {
            "total_distance_m": round(total_distance, 1),
            "estimated_minutes": round(total_seconds / 60, 1),
            "average_congestion": round(total_congestion / max(steps, 1), 2),
            "scenic_score": round(scenic_score, 2),
        }
