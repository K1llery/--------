from fastapi import APIRouter, Depends, HTTPException

from app.repositories.data_loader import DatasetRepository, get_repository
from app.schemas.indoor import IndoorBuildingListResponse, IndoorRouteRequest, IndoorRouteResponse
from app.services.indoor_service import IndoorNavigationService

router = APIRouter()


@router.get("/buildings", response_model=IndoorBuildingListResponse)
def indoor_buildings(repository: DatasetRepository = Depends(get_repository)) -> IndoorBuildingListResponse:
    service = IndoorNavigationService(repository)
    return IndoorBuildingListResponse(items=service.list_buildings())


@router.post("/route", response_model=IndoorRouteResponse)
def indoor_route(payload: IndoorRouteRequest, repository: DatasetRepository = Depends(get_repository)) -> IndoorRouteResponse:
    service = IndoorNavigationService(repository)
    try:
        result = service.plan_route(
            building_code=payload.building_code,
            start_node_code=payload.start_node_code,
            end_node_code=payload.end_node_code,
            strategy=payload.strategy,
            mobility_mode=payload.mobility_mode,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return IndoorRouteResponse(**result)
