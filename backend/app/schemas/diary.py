from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_VIDEO_EXTS = ("mp4", "webm", "ogg", "ogv", "mov", "m4v")


def _infer_media_type(url: str) -> Literal["image", "video"]:
    if not url:
        return "image"
    cleaned = url.lower().split("?", 1)[0].split("#", 1)[0]
    return "video" if cleaned.endswith(tuple("." + ext for ext in _VIDEO_EXTS)) else "image"


# ---------------------------------------------------------------------------
# Request shapes
# ---------------------------------------------------------------------------


class DiaryCreateRequest(BaseModel):
    destination_name: str
    title: str
    content: str
    cover_image_url: str | None = None
    media_urls: list[str] = Field(default_factory=list)


class DiaryUpdateRequest(BaseModel):
    title: str | None = None
    destination_name: str | None = None
    content: str | None = None
    cover_image_url: str | None = None
    media_urls: list[str] | None = None


class DiarySearchRequest(BaseModel):
    query: str


class DiaryCompressionRequest(BaseModel):
    content: str


class DiaryDecompressionRequest(BaseModel):
    encoded: str
    codes: dict[str, str] = Field(default_factory=dict)


class DiaryRateRequest(BaseModel):
    score: float = Field(ge=1.0, le=5.0)


# ---------------------------------------------------------------------------
# Response shapes
# ---------------------------------------------------------------------------


class DiaryMediaOut(BaseModel):
    """Single media item attached to a diary."""

    type: Literal["image", "video"] = "image"
    url: str
    thumbnail_url: str | None = None
    caption: str | None = None
    order: int | None = None


class DiaryListItemOut(BaseModel):
    """Diary as it appears in list / search responses.

    Backwards-compat aliases:
    - ``rating`` (legacy) and ``rating_avg`` (new canonical) are both emitted.
    - ``media_urls`` (legacy ``list[str]``) and ``media`` (new
      ``list[DiaryMediaOut]``) are both emitted; the missing side is
      back-filled from the present side at validation time.
    """

    model_config = ConfigDict(extra="ignore")

    id: int
    title: str
    destination_name: str
    content: str
    views: int = 0
    rating: float = 0.0
    rating_avg: float = 0.0
    rating_count: int = 0
    media_urls: list[str] = Field(default_factory=list)
    media: list[DiaryMediaOut] = Field(default_factory=list)
    cover_image_url: str | None = None
    author_id: int | None = None
    author_name: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _backfill_aliases(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        result = dict(data)

        # rating <-> rating_avg
        has_rating = "rating" in result and result["rating"] is not None
        has_avg = "rating_avg" in result and result["rating_avg"] is not None
        if has_rating and not has_avg:
            result["rating_avg"] = result["rating"]
        elif has_avg and not has_rating:
            result["rating"] = result["rating_avg"]

        # media <-> media_urls
        media = result.get("media") or []
        urls = result.get("media_urls") or []
        if media and not urls:
            result["media_urls"] = [m.get("url") for m in media if isinstance(m, dict) and m.get("url")]
        elif urls and not media:
            result["media"] = [
                {"type": _infer_media_type(str(u)), "url": str(u), "order": i} for i, u in enumerate(urls) if u
            ]

        return result


class DiaryDetailOut(DiaryListItemOut):
    """Same shape as list item; declared separately for OpenAPI clarity."""


class DiaryRatingOut(BaseModel):
    """A single ``diary_ratings.json`` row (per user-per diary)."""

    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    diary_id: int
    user_id: int
    score: float
    updated_at: str | None = None


class DiaryCompressionOut(BaseModel):
    """Result of POST /diaries/compress."""

    encoded: str
    codes: dict[str, str]
    original_bits: int
    compressed_bits: int
    compression_ratio: float


class DiaryListResponse(BaseModel):
    items: list[DiaryListItemOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 50
    search_type: str | None = None
    sort: str = "recommend"
    debug: dict | None = None


class DiarySearchResponse(BaseModel):
    query: str
    items: list[DiaryListItemOut] = Field(default_factory=list)


class DiaryInteractionResponse(BaseModel):
    diary: DiaryDetailOut


class DiaryRateResponse(BaseModel):
    diary: DiaryDetailOut
    user_score: float
    rating_count: int


class DiaryDecompressionResponse(BaseModel):
    content: str


class DiaryAnimationShot(BaseModel):
    index: int
    caption: str
    media_url: str
    transition: str
    duration_seconds: int
    start_second: int
    visual_prompt: str
    narration: str


class DiaryAIGCAnimationResponse(BaseModel):
    diary_id: int
    title: str
    destination_name: str
    generation_mode: str
    keywords: list[str] = Field(default_factory=list)
    total_duration_seconds: int
    narration_script: str
    shots: list[DiaryAnimationShot] = Field(default_factory=list)
