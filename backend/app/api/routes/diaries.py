import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response

from app.api.deps import (
    get_aigc_service,
    get_compression_service,
    get_current_user,
    get_diary_search_service,
    get_optional_user,
)
from app.core.config import get_settings
from app.schemas.diary import (
    DiaryAIGCAnimationResponse,
    DiaryCompressionOut,
    DiaryCompressionRequest,
    DiaryCreateRequest,
    DiaryDecompressionRequest,
    DiaryDecompressionResponse,
    DiaryDetailOut,
    DiaryInteractionResponse,
    DiaryListItemOut,
    DiaryListResponse,
    DiaryRateRequest,
    DiaryRateResponse,
    DiarySearchRequest,
    DiarySearchResponse,
    DiaryUpdateRequest,
)
from app.services.diary_service import CompressionService, DiaryAIGCService, DiarySearchService

router = APIRouter()


@router.get("", response_model=DiaryListResponse)
def list_diaries(
    q: str | None = Query(default=None),
    search_type: str = Query(default="all"),
    sort: str = Query(default="recommend"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    current_user: dict | None = Depends(get_optional_user),
    service: DiarySearchService = Depends(get_diary_search_service),
) -> DiaryListResponse:
    result = service.discover(
        q=q,
        search_type=search_type,
        sort=sort,
        page=page,
        page_size=page_size,
        current_user=current_user,
    )
    return DiaryListResponse(**result)


@router.get("/recommend", response_model=list[DiaryListItemOut])
def recommend_diaries(service: DiarySearchService = Depends(get_diary_search_service)) -> list[dict]:
    return service.recommend()


# NOTE: ``/me`` must be declared before the catch-all ``/{diary_id}`` so the
# literal path takes precedence; otherwise FastAPI would try to parse "me" as
# an int and 422.
@router.get("/me", response_model=DiaryListResponse)
def list_my_diaries(
    current_user: dict = Depends(get_current_user),
    service: DiarySearchService = Depends(get_diary_search_service),
) -> DiaryListResponse:
    items = service.list_by_author(int(current_user["id"]))
    return DiaryListResponse(items=items, total=len(items), page=1, page_size=len(items) or 1)


@router.get("/{diary_id}", response_model=DiaryDetailOut)
def diary_detail(diary_id: int, service: DiarySearchService = Depends(get_diary_search_service)) -> dict:
    diary = service.get_by_id(diary_id)
    if diary is None:
        raise HTTPException(status_code=404, detail="日记不存在")
    return diary


@router.patch("/{diary_id}", response_model=DiaryDetailOut)
def update_diary(
    diary_id: int,
    payload: DiaryUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: DiarySearchService = Depends(get_diary_search_service),
) -> dict:
    try:
        result = service.update(diary_id, current_user, payload.model_dump(exclude_none=True))
    except PermissionError:
        raise HTTPException(status_code=403, detail="只有作者本人可以编辑") from None
    if result is None:
        raise HTTPException(status_code=404, detail="日记不存在")
    return result


@router.delete("/{diary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diary(
    diary_id: int,
    current_user: dict = Depends(get_current_user),
    service: DiarySearchService = Depends(get_diary_search_service),
) -> Response:
    try:
        deleted = service.delete(diary_id, current_user)
    except PermissionError:
        raise HTTPException(status_code=403, detail="只有作者本人可以删除") from None
    if not deleted:
        raise HTTPException(status_code=404, detail="日记不存在")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/search", response_model=DiarySearchResponse)
def search_diaries(
    payload: DiarySearchRequest,
    service: DiarySearchService = Depends(get_diary_search_service),
) -> DiarySearchResponse:
    items = service.search(payload.query)
    return DiarySearchResponse(query=payload.query, items=items)


@router.post("", response_model=DiaryDetailOut)
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


_ALLOWED_IMAGE_EXTS = {"jpg", "jpeg", "png", "webp", "gif", "bmp", "svg"}
_ALLOWED_VIDEO_EXTS = {"mp4", "webm", "ogg", "ogv", "mov", "m4v"}


def _classify_upload(file: UploadFile) -> tuple[str, str]:
    """Return (kind, ext) for the upload; raise 400 on unsupported files."""
    content_type = (file.content_type or "").lower()
    raw_name = file.filename or ""
    ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else ""

    if content_type.startswith("image/") or ext in _ALLOWED_IMAGE_EXTS:
        kind = "image"
    elif content_type.startswith("video/") or ext in _ALLOWED_VIDEO_EXTS:
        kind = "video"
    else:
        raise HTTPException(
            status_code=400,
            detail="仅支持图片或视频文件（image/* 或 video/*）",
        )

    if not ext:
        ext = "bin"
    return kind, ext


@router.post("/media/upload")
async def upload_diary_media(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
) -> dict:
    settings = get_settings()
    kind, ext = _classify_upload(file)
    max_bytes = settings.upload_image_max_bytes if kind == "image" else settings.upload_video_max_bytes

    payload = await file.read()
    size = len(payload)
    if size == 0:
        raise HTTPException(status_code=400, detail="文件内容为空")
    if size > max_bytes:
        limit_mb = max_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"{kind} 文件大小超过 {limit_mb}MB 限制",
        )

    target_dir: Path = settings.upload_media_dir / "diaries"
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{secrets.token_hex(8)}.{ext}"
    target_path = target_dir / filename
    target_path.write_bytes(payload)

    url = f"{settings.upload_media_url_prefix.rstrip('/')}/diaries/{filename}"
    return {"url": url, "type": kind, "filename": filename, "size": size}


@router.post("/compress", response_model=DiaryCompressionOut)
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
