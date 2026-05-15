from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "北京高校与景区个性化旅游系统"
    api_prefix: str = "/api"
    debug: bool = True
    cors_origins: list[str] = Field(default=["http://localhost:5173", "http://127.0.0.1:5173"])
    storage_backend: str = "sqlite"
    base_dir: Path = Path(__file__).resolve().parents[3]
    dataset_dir: Path = base_dir / "datasets" / "prod"
    sqlite_path: Path = base_dir / "storage" / "travel.db"
    dashscope_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("DASHSCOPE_API_KEY", "TRAVEL_DASHSCOPE_API_KEY"),
    )
    ai_text_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ai_image_base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    ai_text_model: str = "qwen-plus"
    ai_image_model: str = "wan2.7-image"
    ai_timeout_seconds: float = 60.0
    generated_media_dir: Path = base_dir / "storage" / "media" / "generated"
    generated_media_url_prefix: str = "/media/generated"
    upload_media_dir: Path = base_dir / "storage" / "media" / "uploads"
    upload_media_url_prefix: str = "/media/uploads"
    upload_image_max_bytes: int = 8 * 1024 * 1024  # 8 MB
    upload_video_max_bytes: int = 64 * 1024 * 1024  # 64 MB
    model_config = SettingsConfigDict(env_prefix="TRAVEL_", extra="ignore", env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> str | list[str]:
        if isinstance(value, str):
            text = value.strip()
            # Keep JSON-array style values for pydantic to parse.
            if text.startswith("["):
                return value
            return [item.strip() for item in text.split(",") if item.strip()]
        return value

    @field_validator("storage_backend")
    @classmethod
    def normalize_storage_backend(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"json", "sqlite"}:
            raise ValueError("TRAVEL_STORAGE_BACKEND must be either 'json' or 'sqlite'")
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()
