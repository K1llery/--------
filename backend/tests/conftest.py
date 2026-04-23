import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.data_loader import DatasetRepository, get_repository


@pytest.fixture
def isolated_repository(tmp_path):
    """提供基于 tmp_path 的隔离数据仓库。"""
    source_dir = Path(__file__).resolve().parents[2] / "datasets" / "prod"
    target_dir = tmp_path / "prod"
    shutil.copytree(source_dir, target_dir)
    return DatasetRepository(target_dir)


@pytest.fixture
def client():
    """提供 TestClient 实例。"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolate_api_dataset(tmp_path):
    """自动为所有 API 测试隔离数据集。"""
    source_dir = Path(__file__).resolve().parents[2] / "datasets" / "prod"
    target_dir = tmp_path / "prod"
    shutil.copytree(source_dir, target_dir)
    repository = DatasetRepository(target_dir)
    app.dependency_overrides[get_repository] = lambda: repository
    yield
    app.dependency_overrides.pop(get_repository, None)
