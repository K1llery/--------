from __future__ import annotations

import heapq

from app.algorithms.graph import Graph
from app.algorithms.tsp import held_karp, nearest_neighbor_two_opt
from app.core.exceptions import BusinessError, NotFoundError
from app.repositories.data_loader import DatasetRepository
from app.services.facility_service import NearbyFacilityService
from app.services.facility_types import normalize_facility_type
from app.services.graph_builder import GraphBuilder


class RoutePlanningService:
    def __init__(self, repository: DatasetRepository, graph_builder: GraphBuilder | None = None) -> None:
        self.repository = repository
        self.graph_builder = graph_builder or GraphBuilder(repository)

    @staticmethod
    def _strategy_label(strategy: str) -> str:
        mapping = {
            "distance": "最短距离",
            "time": "最快到达",
            "congestion": "避开拥堵",
            "scenic": "轻松逛/打卡优先",
        }
        return mapping.get(strategy, "最短距离")

    @staticmethod
    def _transport_label(transport_mode: str) -> str:
        mapping = {
            "walk": "步行",
            "bike": "骑行",
            "taxi": "打车",
            "shuttle": "摆渡车",
            "mixed": "综合方式",
        }
        return mapping.get(transport_mode, "步行")

    @classmethod
    def _strategy_explanation(cls, strategy: str) -> str:
        mapping = {
            "distance": "这条路线优先压缩步行距离，适合明确赶往目标点。",
            "time": "这条路线优先减少预计耗时，尽量走更快、更顺的连通边。",
            "congestion": "这条路线主动绕开高拥堵边，整体可能略绕，但通过体验更稳定。",
            "scenic": "这条路线会尽量串联更有看点的节点，适合边走边逛。",
        }
        return mapping.get(strategy, "已按默认策略生成路线。")

    def _resolve_start_code(
        self,
        scene_name: str,
        start_code: str,
        prefer_nearest_start: bool,
        start_latitude: float | None,
        start_longitude: float | None,
    ) -> str:
        graph = self.graph_builder.get_scene_graph(scene_name)
        scene_codes = self.graph_builder.get_scene_codes(scene_name)

        if prefer_nearest_start and start_latitude is not None and start_longitude is not None:
            nearest = graph.nearest_node(start_latitude, start_longitude, scene_codes)
            if nearest:
                return nearest

        if start_code in scene_codes:
            return start_code
        raise NotFoundError("起点不在当前场景可导航范围内，请更换起点。")

    def _build_segments(self, scene_name: str, path_codes: list[str], transport_mode: str) -> list[dict]:
        if len(path_codes) <= 1:
            return []

        graph = self.graph_builder.get_scene_graph(scene_name)
        names = self.graph_builder.get_name_map(scene_name)
        segments: list[dict] = []
        cumulative_distance = 0.0
        cumulative_minutes = 0.0

        for index, (source, target) in enumerate(zip(path_codes, path_codes[1:]), start=1):
            edge = graph.edge_between(source, target)
            if edge is None:
                continue

            distance_m = round(edge.distance, 1)
            minutes = round(graph.edge_travel_seconds(edge, transport_mode) / 60, 1)
            cumulative_distance = round(cumulative_distance + distance_m, 1)
            cumulative_minutes = round(cumulative_minutes + minutes, 1)

            selected_mode = graph.selected_mode_for_edge(edge, transport_mode)
            if edge.congestion <= 0.65:
                tip = "该路段拥挤系数偏低，实际速度会下降，建议预留等待时间。"
            elif distance_m >= 500:
                tip = "该路段较长，建议中途留意休息点与补水点。"
            elif transport_mode == "walk" and distance_m >= 250:
                tip = "步行段稍长，建议保持匀速。"
            else:
                tip = "路段通行较顺畅。"

            from_name = names.get(source, source)
            to_name = names.get(target, target)
            source_type = self.graph_builder.get_route_node_type(scene_name, source)
            target_type = self.graph_builder.get_route_node_type(scene_name, target)
            if source_type != "road" and target_type == "road":
                instruction = f"从{from_name}接入附近道路，约{distance_m}米，预计{minutes}分钟。"
            elif source_type == "road" and target_type == "road":
                instruction = (
                    f"{self._transport_label(transport_mode)}沿道路继续前行，约{distance_m}米，预计{minutes}分钟。{tip}"
                )
            elif source_type == "road" and target_type != "road":
                instruction = f"离开道路抵达{to_name}，约{distance_m}米，预计{minutes}分钟。"
            else:
                instruction = (
                    f"{self._transport_label(transport_mode)}前往{to_name}，约{distance_m}米，预计{minutes}分钟。{tip}"
                )

            segments.append(
                {
                    "index": index,
                    "from_code": source,
                    "from_name": from_name,
                    "to_code": target,
                    "to_name": to_name,
                    "distance_m": distance_m,
                    "estimated_minutes": minutes,
                    "congestion": round(edge.congestion, 2),
                    "allowed_modes": sorted(edge.modes),
                    "selected_mode": selected_mode,
                    "selected_mode_label": self._transport_label(selected_mode),
                    "instruction": instruction,
                    "cumulative_distance_m": cumulative_distance,
                    "cumulative_minutes": cumulative_minutes,
                }
            )

        return segments

    def _navigation_summary(
        self, strategy: str, transport_mode: str, path_codes: list[str], metrics: dict[str, float]
    ) -> str:
        if len(path_codes) <= 1:
            return "当前仅包含起点信息，可添加终点或途经点继续规划。"
        return (
            f"共{len(path_codes) - 1}段，约{metrics['total_distance_m']}米，预计{metrics['estimated_minutes']}分钟，"
            f"按{self._strategy_label(strategy)} + {self._transport_label(transport_mode)}策略生成。"
        )

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
        graph = self.graph_builder.get_scene_graph(scene_name)
        names = self.graph_builder.get_name_map(scene_name)
        metrics = graph.path_metrics(path_codes, transport_mode)
        segments = self._build_segments(scene_name, path_codes, transport_mode)
        route_edges = self.graph_builder.route_edges_for_path(scene_name, path_codes, transport_mode)
        return {
            "path_codes": path_codes,
            "path_names": [names.get(code, code) for code in path_codes],
            "total_distance_m": metrics["total_distance_m"],
            "estimated_minutes": metrics["estimated_minutes"],
            "strategy": strategy,
            "strategy_label": self._strategy_label(strategy),
            "transport_mode": transport_mode,
            "transport_mode_label": self._transport_label(transport_mode),
            "explanation": self._strategy_explanation(strategy),
            "navigation_summary": self._navigation_summary(strategy, transport_mode, path_codes, metrics),
            "average_congestion": metrics["average_congestion"],
            "scenic_score": metrics["scenic_score"],
            "segments": segments,
            "route_nodes": self.graph_builder.route_nodes_for_path(scene_name, path_codes),
            "route_edges": route_edges,
        }

    def plan_single(
        self,
        scene_name: str,
        start_code: str,
        end_code: str,
        strategy: str,
        transport_mode: str,
        prefer_nearest_start: bool = False,
        start_latitude: float | None = None,
        start_longitude: float | None = None,
    ) -> dict:
        graph = self.graph_builder.get_scene_graph(scene_name)
        names = self.graph_builder.get_name_map(scene_name)
        resolved_start_code = self._resolve_start_code(
            scene_name,
            start_code,
            prefer_nearest_start,
            start_latitude,
            start_longitude,
        )

        if end_code not in self.graph_builder.get_scene_codes(scene_name):
            raise NotFoundError("终点不在当前场景可导航范围内，请更换终点。")

        if resolved_start_code == end_code:
            path_codes = [resolved_start_code]
            result = self._format_single(scene_name, path_codes, strategy, transport_mode)
            result["resolved_start_code"] = resolved_start_code
            result["resolved_start_name"] = names.get(resolved_start_code, resolved_start_code)
            result["alternatives"] = []
            return result

        if strategy == "astar":
            path_codes, _ = graph.a_star(resolved_start_code, end_code, transport_mode)
            strategy = "distance"
        else:
            path_codes, _ = graph.shortest_path(resolved_start_code, end_code, strategy, transport_mode)

        if not path_codes:
            raise BusinessError("未找到可通行路线，请尝试切换策略或交通方式。")

        result = self._format_single(scene_name, path_codes, strategy, transport_mode)
        result["resolved_start_code"] = resolved_start_code
        result["resolved_start_name"] = names.get(resolved_start_code, resolved_start_code)

        alternatives: list[dict] = []
        for alt_strategy in ("time", "scenic"):
            if alt_strategy == strategy:
                continue
            alt_path, _ = graph.shortest_path(resolved_start_code, end_code, alt_strategy, transport_mode)
            if not alt_path or alt_path == path_codes:
                continue
            alternatives.append(self._format_single(scene_name, alt_path, alt_strategy, transport_mode))
        result["alternatives"] = alternatives[:2]
        return result

    @staticmethod
    def _wander_score(code: str, distance: float, graph: Graph, facility_lookup: dict[str, dict]) -> float:
        facility = facility_lookup.get(code)
        facility_bonus = 0.0
        if facility is not None:
            normalized_type = normalize_facility_type(facility.get("facility_type"), facility.get("name", ""))
            facility_bonus = {
                "artwork": 52.0,
                "restaurant": 36.0,
                "restroom": 26.0,
                "service": 24.0,
                "supermarket": 20.0,
                "sports": 18.0,
            }.get(normalized_type, 10.0)
        return graph.node_scores.get(code, 0.0) * 100 + facility_bonus - distance / 45

    @staticmethod
    def _duration_distance_budget(duration_minutes: int, transport_mode: str) -> float:
        speed_by_mode = {
            "walk": 1.1,
            "bike": 3.5,
            "taxi": 4.8,
            "shuttle": 4.8,
            "mixed": 4.0,
        }
        speed = speed_by_mode.get(transport_mode, 1.1)
        return max(220.0, duration_minutes * 60 * speed * 0.35)

    def _auto_wander_targets(
        self,
        scene_name: str,
        start_code: str,
        transport_mode: str,
        duration_minutes: int,
        limit: int,
    ) -> list[str]:
        graph = self.graph_builder.get_scene_graph(scene_name)
        distances = graph.shortest_distances(start_code, strategy="distance", transport_mode=transport_mode)
        scene_codes = self.graph_builder.get_scene_codes(scene_name)
        facility_lookup = {
            item["code"]: item for item in self.repository.facilities() if item["scene_name"] == scene_name
        }
        distance_budget = self._duration_distance_budget(duration_minutes, transport_mode)

        candidates: list[tuple[float, str]] = []
        for code in scene_codes:
            if code == start_code:
                continue
            distance = distances.get(code, float("inf"))
            if distance == float("inf") or distance <= 0:
                continue
            if distance <= distance_budget:
                score = self._wander_score(code, distance, graph, facility_lookup)
                candidates.append((score, code))

        if not candidates:
            return []

        target_count = min(max(3, min(limit, len(candidates))), len(candidates))
        return [code for _, code in heapq.nlargest(target_count, candidates)]

    def plan_wander(
        self,
        scene_name: str,
        start_code: str,
        transport_mode: str,
        duration_minutes: int = 45,
        prefer_nearest_start: bool = False,
        start_latitude: float | None = None,
        start_longitude: float | None = None,
        limit: int = 4,
    ) -> dict:
        names = self.graph_builder.get_name_map(scene_name)
        resolved_start_code = self._resolve_start_code(
            scene_name,
            start_code,
            prefer_nearest_start,
            start_latitude,
            start_longitude,
        )
        targets = self._auto_wander_targets(scene_name, resolved_start_code, transport_mode, duration_minutes, limit)
        if not targets:
            raise BusinessError("当前交通方式下没有足够可达点位，请扩大时长或切换交通方式。")

        result = self.plan_multi(
            scene_name=scene_name,
            start_code=resolved_start_code,
            target_codes=targets,
            strategy="scenic",
            transport_mode=transport_mode,
        )
        if len(result["path_codes"]) <= 1:
            raise BusinessError("当前点位无法组织成闭环路线，请扩大时长或切换交通方式。")

        result["route_intent"] = "wander"
        result["duration_minutes"] = duration_minutes
        result["suggested_stop_codes"] = targets
        result["suggested_stop_names"] = [names.get(code, code) for code in targets]
        result["explanation"] = (
            f"已按{self._transport_label(transport_mode)}和轻松漫游偏好，自动挑选{len(targets)}个附近点位组成闭环。"
        )
        return result

    def plan_nearby_facility(
        self,
        scene_name: str,
        start_code: str,
        facility_type: str,
        transport_mode: str,
        radius: float = 1200.0,
        strategy: str = "time",
        prefer_nearest_start: bool = False,
        start_latitude: float | None = None,
        start_longitude: float | None = None,
    ) -> dict:
        names = self.graph_builder.get_name_map(scene_name)
        resolved_start_code = self._resolve_start_code(
            scene_name,
            start_code,
            prefer_nearest_start,
            start_latitude,
            start_longitude,
        )
        facility_service = NearbyFacilityService(self.repository, self.graph_builder)
        facilities = facility_service.nearby(
            scene_name=scene_name,
            origin_code=resolved_start_code,
            category=facility_type,
            radius=radius,
            transport_mode=transport_mode,
            strategy="distance",
        )
        if not facilities:
            raise BusinessError("当前范围内没有找到可达设施，请扩大半径或切换交通方式。")

        facility = facilities[0]
        route = self.plan_single(
            scene_name=scene_name,
            start_code=resolved_start_code,
            end_code=facility["code"],
            strategy=strategy,
            transport_mode=transport_mode,
        )
        route["route_intent"] = "nearby_facility"
        route["facility"] = facility
        route["search_radius_m"] = radius
        route["explanation"] = (
            f"已找到距离{names.get(resolved_start_code, resolved_start_code)}最近的{facility['facility_label']}："
            f"{facility['name']}，并按{self._transport_label(transport_mode)}生成到达路线。"
        )
        return route

    def plan_multi(
        self,
        scene_name: str,
        start_code: str,
        target_codes: list[str],
        strategy: str,
        transport_mode: str,
        prefer_nearest_start: bool = False,
        start_latitude: float | None = None,
        start_longitude: float | None = None,
    ) -> dict:
        graph = self.graph_builder.get_scene_graph(scene_name)
        names = self.graph_builder.get_name_map(scene_name)
        resolved_start_code = self._resolve_start_code(
            scene_name,
            start_code,
            prefer_nearest_start,
            start_latitude,
            start_longitude,
        )

        scene_codes = self.graph_builder.get_scene_codes(scene_name)
        normalized_targets = [
            code for code in dict.fromkeys(target_codes) if code != resolved_start_code and code in scene_codes
        ]

        if not normalized_targets:
            ordered_stops = [resolved_start_code]
            full_path = [resolved_start_code]
            optimization_label = "无目标点"
        elif len(normalized_targets) <= 8:
            ordered_stops, _ = held_karp(graph, resolved_start_code, normalized_targets, strategy, transport_mode)
            optimization_label = "精确闭环求解"
            full_path = self._expand_segments(graph, ordered_stops, strategy, transport_mode)
        else:
            ordered_stops, _ = nearest_neighbor_two_opt(
                graph, resolved_start_code, normalized_targets, strategy, transport_mode
            )
            optimization_label = "快速闭环近似"
            full_path = self._expand_segments(graph, ordered_stops, strategy, transport_mode)

        metrics = graph.path_metrics(full_path, transport_mode)
        segments = self._build_segments(scene_name, full_path, transport_mode)
        route_edges = self.graph_builder.route_edges_for_path(scene_name, full_path, transport_mode)

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
            "transport_mode": transport_mode,
            "transport_mode_label": self._transport_label(transport_mode),
            "optimization_label": optimization_label,
            "explanation": explanation,
            "navigation_summary": self._navigation_summary(strategy, transport_mode, full_path, metrics),
            "segments": segments,
            "route_nodes": self.graph_builder.route_nodes_for_path(scene_name, full_path),
            "route_edges": route_edges,
            "resolved_start_code": resolved_start_code,
            "resolved_start_name": names.get(resolved_start_code, resolved_start_code),
        }
