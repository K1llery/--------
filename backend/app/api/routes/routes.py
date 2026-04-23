from fastapi import APIRouter, Depends

from app.api.deps import get_routing_service
from app.schemas.routing import MultiRouteRequest, SingleRouteRequest
from app.services.routing_service import RoutePlanningService

router = APIRouter()


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
