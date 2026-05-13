from fastapi import APIRouter, Depends

from app.api.deps import get_repository, get_routing_service
from app.repositories.data_loader import DatasetRepository
from app.schemas.routing import (
    MultiRouteRequest,
    NearbyFacilityRouteRequest,
    OptimizeOrderRequest,
    OptimizeOrderResponse,
    SingleRouteRequest,
    WanderRouteRequest,
)
from app.services.routing_service import RoutePlanningService

import math

router = APIRouter()


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _tsp_greedy_two_opt(points: list[dict]) -> tuple[list[str], float]:
    """基于 Haversine 距离的贪心 + 2-opt TSP 求解器。

    输入: points = [{source_id, latitude, longitude, name}, ...]
    返回: (ordered_source_ids, total_distance_km)
    """
    n = len(points)
    if n <= 2:
        ordered = [p["source_id"] for p in points]
        total = sum(
            _haversine_km(
                points[i]["latitude"], points[i]["longitude"], points[i + 1]["latitude"], points[i + 1]["longitude"]
            )
            for i in range(n - 1)
        )
        return ordered, total

    # 预计算距离矩阵
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = _haversine_km(
                points[i]["latitude"],
                points[i]["longitude"],
                points[j]["latitude"],
                points[j]["longitude"],
            )
            dist[i][j] = d
            dist[j][i] = d

    # 贪心构造初始解（固定从第一个点开始）
    visited = [False] * n
    order = [0]
    visited[0] = True
    current = 0
    for _ in range(n - 1):
        nearest = -1
        min_d = float("inf")
        for j in range(n):
            if not visited[j] and dist[current][j] < min_d:
                min_d = dist[current][j]
                nearest = j
        visited[nearest] = True
        order.append(nearest)
        current = nearest

    # 2-opt 局部优化
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                # 计算交换边 (i-1 -> i, j -> j+1) 为 (i-1 -> j, i -> j+1) 的增益
                before = dist[order[i - 1]][order[i]]
                if j + 1 < n:
                    before += dist[order[j]][order[(j + 1) % n]]
                    after = dist[order[i - 1]][order[j]] + dist[order[i]][order[(j + 1) % n]]
                else:
                    after = dist[order[i - 1]][order[j]]
                if after < before:
                    order[i : j + 1] = reversed(order[i : j + 1])
                    improved = True

    total = sum(dist[order[i]][order[i + 1]] for i in range(n - 1))
    ordered_ids = [points[i]["source_id"] for i in order]
    return ordered_ids, total


@router.post("/single")
def single_route(payload: SingleRouteRequest, service: RoutePlanningService = Depends(get_routing_service)) -> dict:
    return service.plan_single(
        payload.scene_name,
        payload.start_code,
        payload.end_code,
        payload.strategy,
        payload.transport_mode,
        payload.prefer_nearest_start,
        payload.start_latitude,
        payload.start_longitude,
    )


@router.post("/multi")
def multi_route(payload: MultiRouteRequest, service: RoutePlanningService = Depends(get_routing_service)) -> dict:
    return service.plan_multi(
        payload.scene_name,
        payload.start_code,
        payload.target_codes,
        payload.strategy,
        payload.transport_mode,
        payload.prefer_nearest_start,
        payload.start_latitude,
        payload.start_longitude,
    )


@router.post("/wander")
def wander_route(payload: WanderRouteRequest, service: RoutePlanningService = Depends(get_routing_service)) -> dict:
    return service.plan_wander(
        payload.scene_name,
        payload.start_code,
        payload.transport_mode,
        payload.duration_minutes,
        payload.prefer_nearest_start,
        payload.start_latitude,
        payload.start_longitude,
    )


@router.post("/nearby-facility")
def nearby_facility_route(
    payload: NearbyFacilityRouteRequest, service: RoutePlanningService = Depends(get_routing_service)
) -> dict:
    return service.plan_nearby_facility(
        payload.scene_name,
        payload.start_code,
        payload.facility_type,
        payload.transport_mode,
        payload.radius,
        payload.strategy,
        payload.prefer_nearest_start,
        payload.start_latitude,
        payload.start_longitude,
    )


@router.post("/optimize-order", response_model=OptimizeOrderResponse)
def optimize_order(
    payload: OptimizeOrderRequest,
    repository: DatasetRepository = Depends(get_repository),
) -> OptimizeOrderResponse:
    """基于 Haversine 距离 + 贪心TSP 优化跨目的地游览顺序。"""
    all_dests = {d["source_id"]: d for d in repository.destinations()}
    points = []
    for sid in payload.destination_ids:
        d = all_dests.get(sid)
        if d and d.get("latitude") is not None and d.get("longitude") is not None:
            points.append(
                {
                    "source_id": sid,
                    "latitude": float(d["latitude"]),
                    "longitude": float(d["longitude"]),
                    "name": d.get("name", sid),
                }
            )

    if len(points) < 2:
        ordered = [p["source_id"] for p in points]
        return OptimizeOrderResponse(
            ordered_ids=ordered,
            total_distance_km=0.0,
            optimization_label="点位不足，无需优化",
        )

    ordered_ids, total_km = _tsp_greedy_two_opt(points)
    label = "贪心 + 2-opt TSP 优化" if len(points) >= 3 else "贪心最近邻排序"
    return OptimizeOrderResponse(
        ordered_ids=ordered_ids,
        total_distance_km=round(total_km, 2),
        optimization_label=label,
    )
