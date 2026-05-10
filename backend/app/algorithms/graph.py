from __future__ import annotations

import heapq
import math
from dataclasses import dataclass

"""
图论相关算法执行模块，提供单源最短路径（Dijkstra、A*）求值模型，可处理距离、通勤时间、特殊拥堵及风景倾向多目标权重模型。
"""


@dataclass(slots=True)
class Edge:
    """图中连接节点的边定义类。存储了路距、拥堵程度、出行模式要求等。"""
    target: str
    distance: float
    congestion: float
    transport_speeds: dict[str, float]
    modes: set[str]


class Graph:
    """表示地图路网的图类，封装节点和边，提供最短路等图论基本操作。"""
    def __init__(self) -> None:
        self.adj: dict[str, list[Edge]] = {}
        self.coords: dict[str, tuple[float, float]] = {}
        self.node_scores: dict[str, float] = {}

    def add_node(self, code: str, lat: float, lon: float, scenic_score: float = 0.0) -> None:
        """
        添加图节点。
        
        :param code: 节点编号唯一标识
        :param lat: 经度
        :param lon: 纬度
        :param scenic_score: 风景指数评分
        """
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
        """
        向路网之中添加单向边。
        """
        self.adj.setdefault(source, []).append(Edge(target, distance, congestion, transport_speeds, modes))

    @staticmethod
    def _mode_allowed(edge: Edge, transport_mode: str) -> bool:
        if transport_mode == "mixed":
            return True
        if transport_mode == "taxi":
            return bool({"taxi", "shuttle", "mixed"} & edge.modes)
        return transport_mode in edge.modes or "mixed" in edge.modes

    def _speed_for_mode(self, edge: Edge, transport_mode: str) -> float:
        if transport_mode == "mixed":
            return max(edge.transport_speeds.values(), default=1.0)
        if transport_mode == "taxi":
            return (
                edge.transport_speeds.get("taxi")
                or edge.transport_speeds.get("shuttle")
                or max(edge.transport_speeds.values(), default=1.0)
            )
        return (
            edge.transport_speeds.get(transport_mode)
            or edge.transport_speeds.get("walk")
            or max(edge.transport_speeds.values(), default=1.0)
        )

    def edge_travel_seconds(self, edge: Edge, transport_mode: str) -> float:
        """
        计算具体交通方式下经过对应边所消耗的时间(秒)，受交通拥堵状态影响。
        """
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

    def shortest_path(
        self, start: str, end: str, strategy: str = "distance", transport_mode: str = "walk"
    ) -> tuple[list[str], float]:
        """
        计算两点之间的最短加权路径。
        
        :param start: 开始节点编号
        :param end: 目标节点编号
        :param strategy: 规划优先选项（时间/路程/风景等）
        :param transport_mode: 使用的交通工具方式
        :return: (行驶路线的节点序列，总消耗权重)
        """
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

    def shortest_distances(
        self, start: str, strategy: str = "distance", transport_mode: str = "walk"
    ) -> dict[str, float]:
        """
        计算给定的起点到所有其他可达节点的最短路径权重。
        """
        dist, _ = self._dijkstra(start, strategy=strategy, transport_mode=transport_mode)
        return dist

    def edge_between(self, source: str, target: str) -> Edge | None:
        return next((item for item in self.adj.get(source, []) if item.target == target), None)

    def nearest_node(self, latitude: float, longitude: float, candidates: set[str] | None = None) -> str | None:
        best_code: str | None = None
        best_distance = float("inf")
        candidate_codes = candidates if candidates is not None else set(self.coords.keys())
        for code in candidate_codes:
            if code not in self.coords:
                continue
            node_latitude, node_longitude = self.coords[code]
            distance = math.dist((latitude, longitude), (node_latitude, node_longitude))
            if distance < best_distance:
                best_distance = distance
                best_code = code
        return best_code

    def a_star(self, start: str, end: str, transport_mode: str = "walk") -> tuple[list[str], float]:
        """
        使用 A* 算法估计最短路径，启发式函数为坐标欧式距离，专门用来加快特定情况下的检索速度。
        
        :param start: 出发点
        :param end: 目的地
        :param transport_mode: 交通工具类型
        :return: (路径途经的所有节点列表，总路径跨度距离)
        """
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
        """
        针对指定路线，评定出总距离、预估耗时、综合拥挤和整体路书风景等指标集。
        
        :param path: 生成的游览/路线计划中的节点列表
        :param transport_mode: 出行方式
        :return: 各类评估维度打分和数据
        """
        total_distance = 0.0
        total_seconds = 0.0
        total_congestion = 0.0
        scenic_score = 0.0
        steps = 0
        for source, target in zip(path, path[1:]):
            edge = self.edge_between(source, target)
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
