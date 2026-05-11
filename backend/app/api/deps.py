from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, Header

from app.core.exceptions import AuthenticationError
from app.repositories.data_loader import DatasetRepository, get_repository
from app.services.auth_service import AuthService
from app.services.ai_service import AIService, BailianModelClient
from app.services.diary_service import CompressionService, DiaryAIGCService, DiarySearchService
from app.services.facility_service import NearbyFacilityService
from app.services.graph_builder import GraphBuilder
from app.services.indoor_service import IndoorNavigationService
from app.services.recommendation_service import RecommendationService
from app.services.routing_service import RoutePlanningService
from app.services.search_service import SearchService
from app.services.plan_service import PlanService


# ---------------------------------------------------------------------------
# 服务工厂 — 通过 lru_cache 实现跨请求单例（绑定到 repository 实例）
# ---------------------------------------------------------------------------


@lru_cache
def _graph_builder(repository: DatasetRepository) -> GraphBuilder:
    return GraphBuilder(repository)


@lru_cache
def _routing_service(repository: DatasetRepository) -> RoutePlanningService:
    return RoutePlanningService(repository, _graph_builder(repository))


@lru_cache
def _search_service(repository: DatasetRepository) -> SearchService:
    return SearchService(repository)


@lru_cache
def _diary_search_service(repository: DatasetRepository) -> DiarySearchService:
    return DiarySearchService(repository)


@lru_cache
def _indoor_service(repository: DatasetRepository) -> IndoorNavigationService:
    return IndoorNavigationService(repository)


@lru_cache
def _recommendation_service(repository: DatasetRepository) -> RecommendationService:
    return RecommendationService(repository)


@lru_cache
def _facility_service(repository: DatasetRepository) -> NearbyFacilityService:
    return NearbyFacilityService(repository, _graph_builder(repository))


@lru_cache
def _plan_service(repository: DatasetRepository) -> PlanService:
    return PlanService(repository)


# ---------------------------------------------------------------------------
# FastAPI Depends 依赖项
# ---------------------------------------------------------------------------


def get_routing_service(repository: DatasetRepository = Depends(get_repository)) -> RoutePlanningService:
    return _routing_service(repository)


def get_search_service(repository: DatasetRepository = Depends(get_repository)) -> SearchService:
    return _search_service(repository)


def get_diary_search_service(repository: DatasetRepository = Depends(get_repository)) -> DiarySearchService:
    return _diary_search_service(repository)


def get_indoor_service(repository: DatasetRepository = Depends(get_repository)) -> IndoorNavigationService:
    return _indoor_service(repository)


def get_recommendation_service(repository: DatasetRepository = Depends(get_repository)) -> RecommendationService:
    return _recommendation_service(repository)


def get_facility_service(repository: DatasetRepository = Depends(get_repository)) -> NearbyFacilityService:
    return _facility_service(repository)


def get_plan_service(repository: DatasetRepository = Depends(get_repository)) -> PlanService:
    return _plan_service(repository)


def get_compression_service() -> CompressionService:
    return CompressionService()


def get_aigc_service() -> DiaryAIGCService:
    return DiaryAIGCService()


@lru_cache
def get_ai_service() -> AIService:
    from app.core.config import get_settings

    settings = get_settings()
    return AIService(
        model_client=BailianModelClient(
            api_key=settings.dashscope_api_key,
            text_base_url=settings.ai_text_base_url,
            image_base_url=settings.ai_image_base_url,
            text_model=settings.ai_text_model,
            image_model=settings.ai_image_model,
            timeout_seconds=settings.ai_timeout_seconds,
        ),
        generated_media_dir=settings.generated_media_dir,
        generated_media_url_prefix=settings.generated_media_url_prefix,
    )


def get_auth_service(repository: DatasetRepository = Depends(get_repository)) -> AuthService:
    return AuthService(repository)


# ---------------------------------------------------------------------------
# 认证相关
# ---------------------------------------------------------------------------


def extract_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    prefix = "Bearer "
    if authorization.startswith(prefix):
        return authorization[len(prefix) :].strip()
    return authorization.strip() or None


def get_current_user(
    authorization: str | None = Header(default=None),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    token = extract_token(authorization)
    user = auth_service.current_user(token)
    if user is None:
        raise AuthenticationError("请先登录")
    return user
