from pydantic import BaseModel, Field


class CountItem(BaseModel):
    actual: int
    required: int
    passed: bool
    label: str


class DistributionItem(BaseModel):
    label: str
    value: int


class CompressionSummary(BaseModel):
    algorithm: str = "Huffman"
    source: str = "diary.content"
    item_count: int = 0
    original_bits: int = 0
    compressed_bits: int = 0
    average_ratio: float = 0.0


class StatsOverviewResponse(BaseModel):
    counts: dict[str, int]
    requirement_progress: dict[str, CountItem]
    top_destinations: list[dict] = Field(default_factory=list)
    top_diaries: list[dict] = Field(default_factory=list)
    top_foods: list[dict] = Field(default_factory=list)
    distributions: dict[str, list[DistributionItem]]
    compression_summary: CompressionSummary
    algorithm_evidence: list[dict] = Field(default_factory=list)


class RecommendationEvaluationSample(BaseModel):
    user_id: int
    display_name: str
    interests: list[str]
    recommended_count: int
    relevant_count: int
    hit_count: int
    hit_names: list[str] = Field(default_factory=list)
    precision: float
    recall: float


class RecommendationEvaluationResponse(BaseModel):
    top_k: int
    precision: float
    recall: float
    f1: float
    evaluated_user_count: int
    samples: list[RecommendationEvaluationSample] = Field(default_factory=list)
    formula: str
