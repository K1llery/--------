from fastapi import APIRouter, Depends

from app.api.deps import get_ai_service, get_current_user
from app.core.config import get_settings
from app.schemas.ai import DiaryDraftRequest, DiaryDraftResponse, ImageGenerateRequest, ImageGenerateResponse
from app.services.ai_service import AIService

router = APIRouter()


@router.get("/health")
def ai_health() -> dict:
    settings = get_settings()
    return {
        "api_key_configured": bool(settings.dashscope_api_key),
        "text_base_url": settings.ai_text_base_url,
        "image_base_url": settings.ai_image_base_url,
        "text_model": settings.ai_text_model,
        "image_model": settings.ai_image_model,
    }


@router.post("/diary/draft", response_model=DiaryDraftResponse)
def draft_diary(
    payload: DiaryDraftRequest,
    _current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service),
) -> DiaryDraftResponse:
    return DiaryDraftResponse(
        **service.draft_diary(
            destination_name=payload.destination_name,
            keywords=payload.keywords,
            style=payload.style,
        )
    )


@router.post("/images/generate", response_model=ImageGenerateResponse)
def generate_image(
    payload: ImageGenerateRequest,
    _current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service),
) -> ImageGenerateResponse:
    return ImageGenerateResponse(
        **service.generate_image(
            destination_name=payload.destination_name,
            title=payload.title,
            content=payload.content,
        )
    )
