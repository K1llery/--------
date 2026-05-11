from fastapi import APIRouter, Depends, Query

from app.api.deps import get_recommendation_service
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get("")
def list_foods(
    top_k: int | None = Query(None),
    cuisine: str | None = Query(None),
    lat: float | None = Query(None),
    lng: float | None = Query(None),
    radius: float = Query(5.0, ge=0.1, le=50.0),
    service: RecommendationService = Depends(get_recommendation_service),
) -> dict:
    items = service.recommend_foods(top_k, cuisine, lat, lng, radius)
    source_names = sorted({item.get("source_name", "未知来源") for item in items})
    return {"items": items, "loaded_count": len(items), "source_names": source_names}
