from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.repositories.data_loader import DatasetRepository, get_repository
from app.schemas.diary import (
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
from app.services.diary_service import CompressionService, DiarySearchService

router = APIRouter()


@router.get("", response_model=DiaryListResponse)
def list_diaries(repository: DatasetRepository = Depends(get_repository)) -> DiaryListResponse:
    return DiaryListResponse(items=repository.diaries())


@router.get("/recommend")
def recommend_diaries(repository: DatasetRepository = Depends(get_repository)) -> list[dict]:
    return DiarySearchService(repository).recommend()


@router.get("/{diary_id}")
def diary_detail(diary_id: int, repository: DatasetRepository = Depends(get_repository)) -> dict:
    diary = DiarySearchService(repository).get_by_id(diary_id)
    if diary is None:
        raise HTTPException(status_code=404, detail="日记不存在")
    return diary


@router.post("/search", response_model=DiarySearchResponse)
def search_diaries(payload: DiarySearchRequest, repository: DatasetRepository = Depends(get_repository)) -> DiarySearchResponse:
    items = DiarySearchService(repository).search(payload.query)
    return DiarySearchResponse(query=payload.query, items=items)


@router.post("")
def create_diary(
    payload: DiaryCreateRequest,
    current_user: dict = Depends(get_current_user),
    repository: DatasetRepository = Depends(get_repository),
) -> dict:
    return DiarySearchService(repository).create(current_user, payload.model_dump())


@router.post("/{diary_id}/view", response_model=DiaryInteractionResponse)
def increment_diary_view(diary_id: int, repository: DatasetRepository = Depends(get_repository)) -> DiaryInteractionResponse:
    diary = DiarySearchService(repository).increment_view(diary_id)
    if diary is None:
        raise HTTPException(status_code=404, detail="日记不存在")
    return DiaryInteractionResponse(diary=diary)


@router.post("/{diary_id}/rate", response_model=DiaryRateResponse)
def rate_diary(
    diary_id: int,
    payload: DiaryRateRequest,
    current_user: dict = Depends(get_current_user),
    repository: DatasetRepository = Depends(get_repository),
) -> DiaryRateResponse:
    result = DiarySearchService(repository).rate(diary_id, current_user, payload.score)
    if result is None:
        raise HTTPException(status_code=404, detail="日记不存在")
    return DiaryRateResponse(**result)


@router.post("/compress")
def compress_diary(payload: DiaryCompressionRequest) -> dict:
    return CompressionService().compress(payload.content)


@router.post("/decompress", response_model=DiaryDecompressionResponse)
def decompress_diary(payload: DiaryDecompressionRequest) -> DiaryDecompressionResponse:
    content = CompressionService().decompress(payload.encoded, payload.codes)
    return DiaryDecompressionResponse(content=content)
