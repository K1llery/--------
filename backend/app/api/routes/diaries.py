from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_aigc_service, get_compression_service, get_current_user, get_diary_search_service
from app.schemas.diary import (
    DiaryAIGCAnimationResponse,
    DiaryCompressionRequest,
    DiaryCreateRequest,
    DiaryDecompressionRequest,
    DiaryDecompressionResponse,
    DiaryInteractionResponse,
    DiaryListResponse,
    DiaryRateRequest,
    DiaryRateResponse,
    DiarySearchRequest,
    DiarySearchResponse,
)
from app.services.diary_service import CompressionService, DiaryAIGCService, DiarySearchService

router = APIRouter()


@router.get("", response_model=DiaryListResponse)
def list_diaries(service: DiarySearchService = Depends(get_diary_search_service)) -> DiaryListResponse:
    return DiaryListResponse(items=service.list_all())


@router.get("/recommend")
def recommend_diaries(service: DiarySearchService = Depends(get_diary_search_service)) -> list[dict]:
    return service.recommend()


@router.get("/{diary_id}")
def diary_detail(diary_id: int, service: DiarySearchService = Depends(get_diary_search_service)) -> dict:
    diary = service.get_by_id(diary_id)
    if diary is None:
        raise HTTPException(status_code=404, detail="日记不存在")
    return diary


@router.post("/search", response_model=DiarySearchResponse)
def search_diaries(
    payload: DiarySearchRequest,
    service: DiarySearchService = Depends(get_diary_search_service),
) -> DiarySearchResponse:
    items = service.search(payload.query)
    return DiarySearchResponse(query=payload.query, items=items)


@router.post("")
def create_diary(
    payload: DiaryCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: DiarySearchService = Depends(get_diary_search_service),
) -> dict:
    return service.create(current_user, payload.model_dump())


@router.post("/{diary_id}/view", response_model=DiaryInteractionResponse)
def increment_diary_view(
    diary_id: int,
    service: DiarySearchService = Depends(get_diary_search_service),
) -> DiaryInteractionResponse:
    diary = service.increment_view(diary_id)
    if diary is None:
        raise HTTPException(status_code=404, detail="日记不存在")
    return DiaryInteractionResponse(diary=diary)


@router.post("/{diary_id}/rate", response_model=DiaryRateResponse)
def rate_diary(
    diary_id: int,
    payload: DiaryRateRequest,
    current_user: dict = Depends(get_current_user),
    service: DiarySearchService = Depends(get_diary_search_service),
) -> DiaryRateResponse:
    result = service.rate(diary_id, current_user, payload.score)
    if result is None:
        raise HTTPException(status_code=404, detail="日记不存在")
    return DiaryRateResponse(**result)


@router.post("/compress")
def compress_diary(
    payload: DiaryCompressionRequest,
    service: CompressionService = Depends(get_compression_service),
) -> dict:
    return service.compress(payload.content)


@router.post("/decompress", response_model=DiaryDecompressionResponse)
def decompress_diary(
    payload: DiaryDecompressionRequest,
    service: CompressionService = Depends(get_compression_service),
) -> DiaryDecompressionResponse:
    content = service.decompress(payload.encoded, payload.codes)
    return DiaryDecompressionResponse(content=content)


@router.post("/{diary_id}/aigc-animation", response_model=DiaryAIGCAnimationResponse)
def generate_diary_animation(
    diary_id: int,
    diary_service: DiarySearchService = Depends(get_diary_search_service),
    aigc_service: DiaryAIGCService = Depends(get_aigc_service),
) -> DiaryAIGCAnimationResponse:
    diary = diary_service.get_by_id(diary_id)
    if diary is None:
        raise HTTPException(status_code=404, detail="日记不存在")
    return DiaryAIGCAnimationResponse(**aigc_service.generate_animation(diary))
