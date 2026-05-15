from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.error_handlers import register_error_handlers

settings = get_settings()
setup_logging(debug=settings.debug)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    summary="北京高校与景区个性化旅游系统 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(api_router, prefix=settings.api_prefix)
settings.generated_media_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.generated_media_url_prefix,
    StaticFiles(directory=settings.generated_media_dir),
    name="generated-media",
)
(settings.upload_media_dir / "diaries").mkdir(parents=True, exist_ok=True)
app.mount(
    settings.upload_media_url_prefix,
    StaticFiles(directory=settings.upload_media_dir),
    name="upload-media",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Personalized Travel System API is running."}
