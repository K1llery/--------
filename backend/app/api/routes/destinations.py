from fastapi import APIRouter, Depends

from app.api.deps import get_recommendation_service, get_search_service
from app.repositories.data_loader import DatasetRepository, get_repository
from app.schemas.destination import DestinationSearchResponse, RecommendationRequest, SearchRequest
from app.services.recommendation_service import RecommendationService
from app.services.search_service import SearchService

router = APIRouter()


@router.get("")
def list_destinations(repository: DatasetRepository = Depends(get_repository)) -> list[dict]:
    return repository.destinations()


@router.get("/featured")
def featured_destinations(
    top_k: int | None = None,
    service: RecommendationService = Depends(get_recommendation_service),
) -> list[dict]:
    return service.featured_destinations(top_k)


@router.post("/recommend")
def recommend(
    payload: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> list[dict]:
    return service.recommend_destinations(payload.top_k, payload.category, payload.interest_tags)


@router.post("/search", response_model=DestinationSearchResponse)
def search(
    payload: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> DestinationSearchResponse:
    exact = search_service.exact_search(payload.query)
    fuzzy = search_service.fuzzy_search(payload.query, payload.keywords, payload.category)
    featured = [
        item
        for item in recommendation_service.featured_destinations(None)
        if payload.query.lower() in item["name"].lower()
    ]
    return DestinationSearchResponse(exact=exact, fuzzy=fuzzy, featured=featured)
