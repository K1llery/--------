from fastapi import APIRouter, Depends, Query

from app.api.deps import get_facility_service
from app.services.facility_service import NearbyFacilityService

router = APIRouter()


@router.get("/nearby")
def nearby(
    scene_name: str = Query(...),
    origin_code: str = Query(...),
    category: str | None = Query(None),
    radius: float = Query(1200.0),
    service: NearbyFacilityService = Depends(get_facility_service),
) -> list[dict]:
    return service.nearby(scene_name, origin_code, category, radius)
