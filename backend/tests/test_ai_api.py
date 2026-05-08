from pathlib import Path

from app.api.deps import get_ai_service, get_current_user
from app.main import app
from app.services.ai_service import AIService, BailianModelClient


class FakeModelClient:
    def create_diary_draft(self, *, destination_name: str, keywords: list[str], style: str) -> dict:
        return {
            "title": f"{destination_name}城市漫游",
            "content": f"今天去了{destination_name}，重点记录：{'、'.join(keywords)}。整体风格：{style}。",
        }

    def create_image_url(self, *, prompt: str) -> str:
        assert "故宫博物院" in prompt
        return "https://example.test/generated.png"


def fake_downloader(_url: str) -> bytes:
    return b"fake-png-bytes"


def test_ai_diary_draft_endpoint_returns_model_text(client, tmp_path):
    service = AIService(
        model_client=FakeModelClient(),
        generated_media_dir=tmp_path,
        generated_media_url_prefix="/media/generated",
        image_downloader=fake_downloader,
    )
    app.dependency_overrides[get_ai_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: {"id": 1, "display_name": "测试用户"}
    try:
        response = client.post(
            "/api/ai/diary/draft",
            json={"destination_name": "故宫博物院", "keywords": ["红墙", "路线"], "style": "轻松真实"},
        )
    finally:
        app.dependency_overrides.pop(get_ai_service, None)
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "故宫博物院城市漫游"
    assert "红墙" in payload["content"]


def test_ai_health_endpoint_reports_configuration_without_secret(client):
    response = client.get("/api/ai/health")

    assert response.status_code == 200
    payload = response.json()
    assert "api_key" not in payload
    assert "api_key_configured" in payload
    assert payload["text_model"]
    assert payload["image_model"]


def test_ai_image_endpoint_saves_generated_image(client, tmp_path):
    service = AIService(
        model_client=FakeModelClient(),
        generated_media_dir=tmp_path,
        generated_media_url_prefix="/media/generated",
        image_downloader=fake_downloader,
    )
    app.dependency_overrides[get_ai_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: {"id": 1, "display_name": "测试用户"}
    try:
        response = client.post(
            "/api/ai/images/generate",
            json={
                "destination_name": "故宫博物院",
                "title": "故宫博物院城市漫游",
                "content": "红墙、路线和午后光影。",
            },
        )
    finally:
        app.dependency_overrides.pop(get_ai_service, None)
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["image_url"].startswith("/media/generated/")
    saved_path = Path(tmp_path) / Path(payload["image_url"]).name
    assert saved_path.read_bytes() == b"fake-png-bytes"


def test_bailian_image_client_uses_wan27_multimodal_endpoint(monkeypatch):
    captured: dict = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "output": {
                    "choices": [
                        {
                            "message": {
                                "content": [
                                    {"type": "image", "image": "https://dashscope.test/result.png"},
                                ]
                            }
                        }
                    ]
                }
            }

    def fake_post(url: str, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs["json"]
        return FakeResponse()

    monkeypatch.setattr("app.services.ai_service.httpx.post", fake_post)
    client = BailianModelClient(
        api_key="sk-test",
        text_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        image_base_url="https://dashscope.aliyuncs.com/api/v1",
        text_model="qwen-plus",
        image_model="wan2.7-image",
        timeout_seconds=60,
    )

    image_url = client.create_image_url(prompt="故宫博物院封面")

    assert captured["url"] == "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    assert captured["json"]["input"]["messages"][0]["content"] == [{"text": "故宫博物院封面"}]
    assert image_url == "https://dashscope.test/result.png"
