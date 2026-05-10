"""
FastAPI 依赖注入模块 (Dependencies)

该模块定义了所有需要通过 FastAPI 的 Depends 进行注入的依赖项服务。
使用了 lru_cache 确保由于服务实例化开销可能带来的一些性能问题被最小化，
使其在每个实例化的 Repository 以及服务工厂生命周期中作为跨请求单例运行。
"""
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


# ---------------------------------------------------------------------------
# 服务工厂 — 通过 lru_cache 实现跨请求单例（绑定到 repository 实例）
# ---------------------------------------------------------------------------


@lru_cache
def _graph_builder(repository: DatasetRepository) -> GraphBuilder:
    """
    依赖注入: 获取图构建器（单例模式）。
    根据当前存储库构建道路网络的内存图以供寻路算法使用。
    """
    return GraphBuilder(repository)


@lru_cache
def _routing_service(repository: DatasetRepository) -> RoutePlanningService:
    """依赖注入: 获取路线规划服务（单例模式）。"""
    return RoutePlanningService(repository, _graph_builder(repository))


@lru_cache
def _search_service(repository: DatasetRepository) -> SearchService:
    """依赖注入: 获取通用搜索服务（单例模式）。"""
    return SearchService(repository)


@lru_cache
def _diary_search_service(repository: DatasetRepository) -> DiarySearchService:
    """依赖注入: 获取游记搜索服务（单例模式）。"""
    return DiarySearchService(repository)


@lru_cache
def _indoor_service(repository: DatasetRepository) -> IndoorNavigationService:
    """依赖注入: 获取室内导航服务（单例模式）。"""
    return IndoorNavigationService(repository)


@lru_cache
def _recommendation_service(repository: DatasetRepository) -> RecommendationService:
    """依赖注入: 获取景点与游记推荐服务（单例模式）。"""
    return RecommendationService(repository)


@lru_cache
def _facility_service(repository: DatasetRepository) -> NearbyFacilityService:
    """依赖注入: 获取周边设施查询服务（单例模式）。"""
    return NearbyFacilityService(repository, _graph_builder(repository))


# ---------------------------------------------------------------------------
# FastAPI Depends 依赖项
# ---------------------------------------------------------------------------


def get_routing_service(repository: DatasetRepository = Depends(get_repository)) -> RoutePlanningService:
    """提供 RoutePlanningService 的 FastAPI 依赖项注入"""
    return _routing_service(repository)


def get_search_service(repository: DatasetRepository = Depends(get_repository)) -> SearchService:
    """提供 SearchService 的 FastAPI 依赖项注入"""
    return _search_service(repository)


def get_diary_search_service(repository: DatasetRepository = Depends(get_repository)) -> DiarySearchService:
    """提供 DiarySearchService 的 FastAPI 依赖项注入"""
    return _diary_search_service(repository)


def get_indoor_service(repository: DatasetRepository = Depends(get_repository)) -> IndoorNavigationService:
    """提供 IndoorNavigationService 的 FastAPI 依赖项注入"""
    return _indoor_service(repository)


def get_recommendation_service(repository: DatasetRepository = Depends(get_repository)) -> RecommendationService:
    """提供 RecommendationService 的 FastAPI 依赖项注入"""
    return _recommendation_service(repository)


def get_facility_service(repository: DatasetRepository = Depends(get_repository)) -> NearbyFacilityService:
    """提供 NearbyFacilityService 的 FastAPI 依赖项注入"""
    return _facility_service(repository)


def get_compression_service() -> CompressionService:
    """提供 CompressionService 的 FastAPI 依赖项注入"""
    return CompressionService()


def get_aigc_service() -> DiaryAIGCService:
    """提供 DiaryAIGCService 的 FastAPI 依赖项注入"""
    return DiaryAIGCService()


@lru_cache
def get_ai_service() -> AIService:
    """
    提供 AIService 的 FastAPI 依赖项注入，
    实例化并缓存基于 Bailian 的 AI 客户端服务。
    """
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
    """提供 AuthService 的 FastAPI 依赖项注入"""
    return AuthService(repository)


# ---------------------------------------------------------------------------
# 认证相关
# ---------------------------------------------------------------------------


def extract_token(authorization: str | None) -> str | None:
    """从请求头提取 Bearer 格式的 token"""
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
    """
    通过 Header 或 Auth 服务解析并获取当前登录的用户，
    如果无权或解析失败会抛出 AuthenticationError。
    """
    token = extract_token(authorization)
    user = auth_service.current_user(token)
    if user is None:
        raise AuthenticationError("请先登录")
    return user
