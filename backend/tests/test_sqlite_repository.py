from pathlib import Path

from app.repositories.sqlite_repository import SQLiteRepository
from app.scripts.seed_sqlite import seed_sqlite_from_json
from app.services.auth_service import AuthService
from app.services.diary_service import DiarySearchService


def test_sqlite_repository_can_seed_and_persist_core_flows(tmp_path):
    database_path = tmp_path / "travel.db"
    dataset_dir = Path(__file__).resolve().parents[2] / "datasets" / "prod"
    seed_sqlite_from_json(dataset_dir, database_path)
    repository = SQLiteRepository(database_path)

    assert len(repository.destinations()) >= 200
    assert any(item["name"] == "北京邮电大学" for item in repository.destinations())
    assert repository.featured_destinations()
    assert repository.scenes()

    auth_service = AuthService(repository)
    user, token = auth_service.login("demo_user_1", "demo123")
    assert token.startswith("local-")
    assert auth_service.current_user(token)["id"] == user["id"]

    diary_service = DiarySearchService(repository)
    created = diary_service.create(
        user,
        {
            "destination_name": "故宫博物院",
            "title": "SQLite 发布测试",
            "content": "SQLite 模式下发布一篇测试日记。",
            "media_urls": [],
        },
    )
    assert diary_service.get_by_id(created["id"])["title"] == "SQLite 发布测试"
