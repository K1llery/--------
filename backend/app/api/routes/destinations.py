from fastapi import APIRouter, Depends

from app.api.deps import (
    get_current_user,
    get_destination_interaction_service,
    get_optional_user,
    get_recommendation_service,
    get_search_service,
)
from app.repositories.data_loader import DatasetRepository, get_repository
from app.schemas.destination import (
    DestinationDetailOut,
    DestinationRateRequest,
    DestinationSearchResponse,
    RecommendationRequest,
    SearchRequest,
)
from app.services.destination_service import DestinationInteractionService
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


@router.get("/{source_id}", response_model=DestinationDetailOut)
def destination_detail(
    source_id: str,
    current_user: dict | None = Depends(get_optional_user),
    service: DestinationInteractionService = Depends(get_destination_interaction_service),
) -> dict:
    return service.detail(source_id, current_user)


@router.post("/{source_id}/view", response_model=DestinationDetailOut)
def increment_destination_view(
    source_id: str,
    current_user: dict | None = Depends(get_optional_user),
    service: DestinationInteractionService = Depends(get_destination_interaction_service),
) -> dict:
    return service.increment_view(source_id, current_user)


@router.post("/{source_id}/rate", response_model=DestinationDetailOut)
def rate_destination(
    source_id: str,
    payload: DestinationRateRequest,
    current_user: dict = Depends(get_current_user),
    service: DestinationInteractionService = Depends(get_destination_interaction_service),
) -> dict:
    return service.rate(source_id, current_user, payload.score)
