from fastapi import APIRouter, Depends, Query

from app.api.deps import get_stats_service
from app.schemas.stats import RecommendationEvaluationResponse, StatsOverviewResponse
from app.services.stats_service import StatsService

router = APIRouter()


@router.get("/overview", response_model=StatsOverviewResponse)
def stats_overview(service: StatsService = Depends(get_stats_service)) -> dict:
    return service.overview()


@router.get("/recommendation-evaluation", response_model=RecommendationEvaluationResponse)
def recommendation_evaluation(
    top_k: int = Query(default=10, ge=1, le=50),
    service: StatsService = Depends(get_stats_service),
) -> dict:
    return service.recommendation_evaluation(top_k)
