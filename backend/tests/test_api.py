from uuid import uuid4


def test_destinations_endpoint_returns_real_dataset(client):
    response = client.get("/api/destinations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 200
    assert any(item["name"] == "北京邮电大学" for item in data)


def test_deployment_build_does_not_expose_non_core_debug_routes(client):
    assert client.get("/api/agents").status_code == 404
    assert client.get("/api/admin/import/status").status_code == 404


def test_featured_destinations_include_scenic_and_shopping(client):
    response = client.get("/api/destinations/featured")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 8
    categories = {item["category"] for item in data}
    assert "scenic" in categories
    assert "shopping" in categories
    assert all(item["rating"] is not None for item in data)
    assert all(item["source_url"] for item in data)


def test_single_route_endpoint_returns_path(client):
    response = client.post(
        "/api/routes/single",
        json={
            "scene_name": "BUPT_Main_Campus",
            "start_code": "BUPT_GATE",
            "end_code": "BUPT_LIB",
            "strategy": "distance",
            "transport_mode": "walk",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["path_codes"]
    assert payload["path_names"]
    assert payload["estimated_minutes"] >= 0
    assert payload["segments"]
    assert payload["navigation_summary"]
    assert payload["resolved_start_code"] == "BUPT_GATE"
    assert "alternatives" in payload
    assert payload["route_source"] == "local"
    assert payload["route_source_label"] == "本地算法"
    assert payload["algorithm_path_codes"] == payload["path_codes"]
    assert "external_provider" not in payload
    assert "provider_distance_m" not in payload
    assert "provider_estimated_minutes" not in payload
    assert "external_fallback_reason" not in payload
    assert payload["route_geometry"]
    assert payload["route_polyline"]
    assert len(payload["path_codes"]) > 2
    assert all(code in {node["code"] for node in payload["route_nodes"]} for code in payload["path_codes"])


def test_single_route_can_resolve_start_from_current_location(client):
    response = client.post(
        "/api/routes/single",
        json={
            "scene_name": "BUPT_Main_Campus",
            "start_code": "BUPT_LIB",
            "end_code": "BUPT_05",
            "strategy": "distance",
            "transport_mode": "walk",
            "prefer_nearest_start": True,
            "start_latitude": 39.96007,
            "start_longitude": 116.36408,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["resolved_start_code"] == "BUPT_GATE"
    assert payload["path_codes"][0] == "BUPT_GATE"


def test_indoor_buildings_endpoint_returns_structured_items(client):
    response = client.get("/api/indoor/buildings")
    assert response.status_code == 200
    payload = response.json()["items"]
    assert payload
    assert any(item["building_code"] == "BUPT_LIB" for item in payload)


def test_indoor_route_cross_floor_contains_elevator_instruction(client):
    response = client.post(
        "/api/indoor/route",
        json={
            "building_code": "BUPT_LIB",
            "start_node_code": "BUPT_LIB_GATE_L1",
            "end_node_code": "BUPT_LIB_ROOM_201",
            "strategy": "time",
            "mobility_mode": "normal",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["path_node_codes"]
    assert any(step["connector"] == "elevator" for step in payload["steps"])
    assert any("电梯" in step["instruction"] for step in payload["steps"])


def test_indoor_route_wheelchair_mode_avoids_stairs(client):
    response = client.post(
        "/api/indoor/route",
        json={
            "building_code": "BUPT_LIB",
            "start_node_code": "BUPT_LIB_GATE_L1",
            "end_node_code": "BUPT_LIB_ARCHIVE_L3",
            "strategy": "accessible",
            "mobility_mode": "wheelchair",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["steps"]
    assert all(step["connector"] != "stairs" for step in payload["steps"])


def test_nearby_facilities_endpoint_returns_graph_distance(client):
    response = client.get(
        "/api/facilities/nearby",
        params={"scene_name": "BUPT_Main_Campus", "origin_code": "BUPT_GATE"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "graph_distance" in data[0]


def test_nearby_facility_route_endpoint_returns_route_to_restroom(client):
    response = client.post(
        "/api/routes/nearby-facility",
        json={
            "scene_name": "BUPT_Main_Campus",
            "start_code": "BUPT_LIB",
            "facility_type": "restroom",
            "transport_mode": "taxi",
            "radius": 1500,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["route_intent"] == "nearby_facility"
    assert payload["facility"]["normalized_type"] == "restroom"
    assert payload["path_codes"][0] == payload["resolved_start_code"]
    assert payload["path_codes"][-1] == payload["facility"]["code"]
    assert payload["segments"]


def test_wander_route_endpoint_returns_auto_loop(client):
    response = client.post(
        "/api/routes/wander",
        json={
            "scene_name": "BUPT_Main_Campus",
            "start_code": "BUPT_GATE",
            "transport_mode": "walk",
            "duration_minutes": 35,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["route_intent"] == "wander"
    assert payload["path_codes"][0] == "BUPT_GATE"
    assert payload["path_codes"][-1] == "BUPT_GATE"
    assert len(payload["ordered_stop_codes"]) >= 3


def test_foods_endpoint_returns_structured_items(client):
    response = client.get("/api/foods")
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"]
    assert payload["items"][0]["rating"] is not None


def test_diary_search_and_detail_return_structured_payload(client):
    search_response = client.post("/api/diaries/search", json={"query": "故宫"})
    assert search_response.status_code == 200
    payload = search_response.json()
    assert "items" in payload
    diary_id = payload["items"][0]["id"]
    detail_response = client.get(f"/api/diaries/{diary_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["content"]


def test_auth_register_me_favorite_and_logout_flow(client):
    username = f"test_{uuid4().hex[:8]}"
    register_response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "secret123", "display_name": "测试用户"},
    )
    assert register_response.status_code == 200
    payload = register_response.json()
    token = payload["token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["user"]["username"] == username

    favorite_response = client.post(
        "/api/auth/favorites/destinations",
        json={"source_id": "featured-5"},
        headers=headers,
    )
    assert favorite_response.status_code == 200
    assert "featured-5" in favorite_response.json()["user"]["favorite_destination_ids"]

    route_response = client.post(
        "/api/auth/favorites/routes",
        json={
            "scene_name": "BUPT_Main_Campus",
            "strategy": "distance",
            "transport_mode": "walk",
            "path_codes": ["BUPT_GATE", "BUPT_LIB"],
            "path_names": ["南门", "图书馆"],
            "total_distance_m": 100,
            "estimated_minutes": 2.1,
            "explanation": "测试路线",
        },
        headers=headers,
    )
    assert route_response.status_code == 200
    assert route_response.json()["user"]["favorite_route_snapshots"]

    logout_response = client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 200


def test_create_diary_requires_auth_and_persists(client):
    login_response = client.post("/api/auth/login", json={"username": "demo_user_1", "password": "demo123"})
    assert login_response.status_code == 200
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/diaries",
        json={
            "destination_name": "故宫博物院",
            "title": "测试发布日记",
            "content": "这是一篇用于接口测试的新日记。",
            "cover_image_url": "/media/destinations/destination-01.svg",
            "media_urls": ["/media/destinations/destination-01.svg"],
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    assert create_response.json()["author_name"]


def test_diary_view_and_rate_interaction_flow(client):
    search_response = client.post("/api/diaries/search", json={"query": "故宫"})
    assert search_response.status_code == 200
    diary_id = search_response.json()["items"][0]["id"]

    detail_response = client.get(f"/api/diaries/{diary_id}")
    assert detail_response.status_code == 200
    before_views = detail_response.json()["views"]

    view_response = client.post(f"/api/diaries/{diary_id}/view")
    assert view_response.status_code == 200
    assert view_response.json()["diary"]["views"] == before_views + 1

    login_response = client.post("/api/auth/login", json={"username": "demo_user_2", "password": "demo123"})
    assert login_response.status_code == 200
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    rate_response = client.post(f"/api/diaries/{diary_id}/rate", json={"score": 4.8}, headers=headers)
    assert rate_response.status_code == 200
    payload = rate_response.json()
    assert payload["user_score"] == 4.8
    assert payload["rating_count"] >= 1
    assert 1.0 <= payload["diary"]["rating"] <= 5.0


def test_diary_compress_and_decompress_roundtrip(client):
    content = "路线体验很好，故宫红墙很适合拍照。"
    compress_response = client.post("/api/diaries/compress", json={"content": content})
    assert compress_response.status_code == 200
    compressed = compress_response.json()
    assert compressed["encoded"]
    assert compressed["codes"]

    decompress_response = client.post(
        "/api/diaries/decompress",
        json={"encoded": compressed["encoded"], "codes": compressed["codes"]},
    )
    assert decompress_response.status_code == 200
    assert decompress_response.json()["content"] == content


def test_diary_aigc_animation_endpoint_returns_storyboard(client):
    search_response = client.post("/api/diaries/search", json={"query": "故宫"})
    assert search_response.status_code == 200
    diary_id = search_response.json()["items"][0]["id"]

    response = client.post(f"/api/diaries/{diary_id}/aigc-animation")
    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_mode"] == "aigc-storyboard-v1"
    assert payload["shots"]
    assert payload["total_duration_seconds"] > 0
    assert payload["narration_script"]
