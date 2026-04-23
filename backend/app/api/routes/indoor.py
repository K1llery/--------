from fastapi import APIRouter, Depends

from app.api.deps import get_indoor_service
from app.schemas.indoor import IndoorBuildingListResponse, IndoorRouteRequest, IndoorRouteResponse
from app.services.indoor_service import IndoorNavigationService

router = APIRouter()


@router.get("/buildings", response_model=IndoorBuildingListResponse)
def indoor_buildings(service: IndoorNavigationService = Depends(get_indoor_service)) -> IndoorBuildingListResponse:
    return IndoorBuildingListResponse(items=service.list_buildings())


@router.post("/route", response_model=IndoorRouteResponse)
def indoor_route(
    payload: IndoorRouteRequest,
    service: IndoorNavigationService = Depends(get_indoor_service),
) -> IndoorRouteResponse:
    result = service.plan_route(
        building_code=payload.building_code,
        start_node_code=payload.start_node_code,
        end_node_code=payload.end_node_code,
        strategy=payload.strategy,
        mobility_mode=payload.mobility_mode,
    )
    return IndoorRouteResponse(**result)
