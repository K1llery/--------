from pydantic import BaseModel, Field


class DestinationOut(BaseModel):
    source_id: str
    name: str
    category: str
    city: str = ""
    district: str = ""
    address: str = ""
    latitude: float
    longitude: float
    rating: float | None = None
    heat: float | None = None
    tags: list[str] = Field(default_factory=list)
    description: str = ""
    image_url: str | None = None
    image_source_name: str | None = None
    image_source_url: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    fetched_date: str | None = None
    heat_metric: str | None = None
    rating_source_name: str | None = None
    rating_source_url: str | None = None
    heat_source_name: str | None = None
    heat_source_url: str | None = None


class DestinationInteractionStats(BaseModel):
    total_views: int = 0
    rating_avg: float | None = None
    rating_count: int = 0
    user_score: float | None = None


class DestinationDetailOut(DestinationOut):
    interaction_stats: DestinationInteractionStats
    nearby_facilities: list[dict] = Field(default_factory=list)
    nearby_foods: list[dict] = Field(default_factory=list)
    related_diaries: list[dict] = Field(default_factory=list)
    algorithm_explanation: str = ""


class DestinationRateRequest(BaseModel):
    score: float = Field(ge=1.0, le=5.0)


class RecommendationRequest(BaseModel):
    top_k: int = 10
    sort_by: str = "score"
    interest_tags: list[str] = Field(default_factory=list)
    category: str | None = None


class SearchRequest(BaseModel):
    query: str
    category: str | None = None
    keywords: list[str] = Field(default_factory=list)


class DestinationSearchResponse(BaseModel):
    exact: dict | None = None
    fuzzy: list[dict] = Field(default_factory=list)
    featured: list[dict] = Field(default_factory=list)
