from pydantic import BaseModel, Field


class DiaryDraftRequest(BaseModel):
    destination_name: str
    keywords: list[str] = Field(default_factory=list)
    style: str = "轻松真实"


class DiaryDraftResponse(BaseModel):
    title: str
    content: str


class ImageGenerateRequest(BaseModel):
    destination_name: str
    title: str
    content: str


class ImageGenerateResponse(BaseModel):
    image_url: str
    source_url: str
    prompt: str
