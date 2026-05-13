from app.algorithms.compression import HuffmanCodec
from app.algorithms.graph import Graph
from app.algorithms.search import HashIndex, InvertedIndex, TrieIndex
from app.algorithms.tsp import held_karp, nearest_neighbor_two_opt
from app.algorithms.topk import TopKSelector, quickselect_top_k
from app.repositories.data_loader import get_json_repository
from app.services.diary_service import CompressionService, DiaryAIGCService
from app.services.facility_service import NearbyFacilityService
from app.services.indoor_service import IndoorNavigationService
from app.services.routing_service import RoutePlanningService
from app.services.search_service import SearchService


def local_route_service() -> RoutePlanningService:
    return RoutePlanningService(get_json_repository())


def test_topk_selector_works():
    items = [{"name": "a", "score": 1}, {"name": "b", "score": 3}, {"name": "c", "score": 2}]
    selector = TopKSelector(lambda item: item["score"])
    result = selector.select(items, 2)
    assert [item["name"] for item in result] == ["b", "c"]


def test_quickselect_top_k_works():
    items = [{"name": "a", "score": 1}, {"name": "b", "score": 3}, {"name": "c", "score": 2}]
    result = quickselect_top_k(items, 2, lambda item: item["score"])
    assert [item["name"] for item in result] == ["b", "c"]


def test_topk_selector_ties_do_not_raise_type_error():
    items = [{"name": "a", "score": 5}, {"name": "b", "score": 5}, {"name": "c", "score": 4}]
    selector = TopKSelector(lambda item: item["score"])
    result = selector.select(items, 2)
    assert {item["name"] for item in result} == {"a", "b"}


def test_quickselect_calls_scorer_once_per_item():
    items = [{"name": str(i), "score": i} for i in range(20)]
    counter = {"calls": 0}

    def scorer(item: dict) -> int:
        counter["calls"] += 1
        return item["score"]

    result = quickselect_top_k(items, 5, scorer)
    assert counter["calls"] == len(items)
    assert [item["score"] for item in result] == [19, 18, 17, 16, 15]


def test_hash_trie_inverted_search():
    items = [
        {"source_id": "1", "name": "北京邮电大学", "description": "海淀 校园"},
        {"source_id": "2", "name": "北京动物园", "description": "景区 熊猫"},
    ]
    hash_index = HashIndex()
    hash_index.build(items, "name")
    assert hash_index.get("北京邮电大学")["source_id"] == "1"

    trie = TrieIndex()
    trie.insert("北京邮电大学", "1")
    assert "1" in trie.prefix_search("北京")

    inverted = InvertedIndex()
    inverted.build(items, ["name", "description"], "source_id")
    assert "2" in inverted.search(["熊猫"])


def test_graph_shortest_path():
    graph = Graph()
    graph.add_node("A", 0.0, 0.0)
    graph.add_node("B", 1.0, 1.0)
    graph.add_node("C", 2.0, 2.0)
    graph.add_edge("A", "B", 10, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("B", "C", 5, 1.0, {"walk": 1.0}, {"walk"})
    path, cost = graph.shortest_path("A", "C")
    assert path == ["A", "B", "C"]
    assert cost == 15


def test_graph_shortest_distances_matches_path_cost():
    graph = Graph()
    graph.add_node("A", 0.0, 0.0)
    graph.add_node("B", 1.0, 1.0)
    graph.add_node("C", 2.0, 2.0)
    graph.add_edge("A", "B", 7, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("B", "C", 4, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("A", "C", 20, 1.0, {"walk": 1.0}, {"walk"})

    dist = graph.shortest_distances("A")
    path, cost = graph.shortest_path("A", "C")

    assert path == ["A", "B", "C"]
    assert dist["C"] == cost == 11


def test_graph_nearest_node_returns_closest_candidate():
    graph = Graph()
    graph.add_node("A", 39.0, 116.0)
    graph.add_node("B", 39.5, 116.5)
    graph.add_node("C", 40.0, 117.0)

    assert graph.nearest_node(39.48, 116.48) == "B"
    assert graph.nearest_node(39.48, 116.48, {"A", "C"}) == "A"


def test_tsp_algorithms_handle_empty_targets():
    graph = Graph()
    graph.add_node("A", 0.0, 0.0)

    exact_route, exact_cost = held_karp(graph, "A", [], "distance", "walk")
    approx_route, approx_cost = nearest_neighbor_two_opt(graph, "A", [], "distance", "walk")

    assert exact_route == ["A", "A"]
    assert exact_cost == 0.0
    assert approx_route == ["A", "A"]
    assert approx_cost == 0.0


def test_held_karp_uses_single_source_distance_tables(monkeypatch):
    graph = Graph()
    for code in ("A", "B", "C", "D"):
        graph.add_node(code, 0.0, 0.0)
    graph.add_edge("A", "B", 1, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("A", "C", 2, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("A", "D", 3, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("B", "A", 1, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("B", "C", 1, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("B", "D", 2, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("C", "A", 2, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("C", "B", 1, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("C", "D", 1, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("D", "A", 3, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("D", "B", 2, 1.0, {"walk": 1.0}, {"walk"})
    graph.add_edge("D", "C", 1, 1.0, {"walk": 1.0}, {"walk"})

    calls = {"count": 0}
    original = graph.shortest_distances

    def tracked(start: str, strategy: str = "distance", transport_mode: str = "walk") -> dict[str, float]:
        calls["count"] += 1
        return original(start, strategy=strategy, transport_mode=transport_mode)

    monkeypatch.setattr(graph, "shortest_distances", tracked)
    route, cost = held_karp(graph, "A", ["B", "C", "D"], "distance", "walk")

    assert route[0] == "A" and route[-1] == "A"
    assert cost > 0
    assert calls["count"] == 4


def test_nearby_facility_uses_graph_distances_instead_of_single_route_calls():
    repository = get_json_repository()
    service = NearbyFacilityService(repository)

    # 重构后 NearbyFacilityService 直接使用 GraphBuilder 而非 RoutePlanningService，
    # 因此不再存在 route_service 属性——架构已保证不会调用 plan_single。
    assert not hasattr(service, "route_service"), "NearbyFacilityService 不应再依赖 RoutePlanningService"
    items = service.nearby("BUPT_Main_Campus", "BUPT_GATE")

    assert items
    assert "graph_distance" in items[0]


def test_nearby_facility_restroom_category_matches_toilets_data():
    service = NearbyFacilityService(get_json_repository())
    items = service.nearby("BUPT_Main_Campus", "BUPT_LIB", category="restroom", transport_mode="walk")

    assert items
    assert items[0]["facility_type"] == "toilets"
    assert items[0]["normalized_type"] == "restroom"


def test_taxi_mode_uses_vehicle_speed_on_mixed_roads():
    service = local_route_service()

    walk = service.plan_single("BUPT_Main_Campus", "BUPT_GATE", "BUPT_LIB", "time", "walk")
    taxi = service.plan_single("BUPT_Main_Campus", "BUPT_GATE", "BUPT_LIB", "time", "taxi")

    assert taxi["transport_mode_label"] == "打车"
    assert taxi["estimated_minutes"] < walk["estimated_minutes"]


def test_single_route_returns_algorithm_path_and_geometry():
    service = local_route_service()
    result = service.plan_single("BUPT_Main_Campus", "BUPT_GATE", "BUPT_LIB", "time", "walk")

    assert result["path_codes"][0] == "BUPT_GATE"
    assert result["path_codes"][-1] == "BUPT_LIB"
    assert result["total_distance_m"] > 0
    assert result["route_source"] == "local"
    assert result["algorithm_path_codes"] == result["path_codes"]
    assert result["route_geometry"]
    assert len(result["path_codes"]) > 2
    assert any(node["route_node_type"] != "place" for node in result["route_nodes"][1:-1])
    assert all(code in {node["code"] for node in result["route_nodes"]} for code in result["path_codes"])


def test_single_route_is_local_algorithm_only():
    service = RoutePlanningService(get_json_repository())
    result = service.plan_single("BUPT_Main_Campus", "BUPT_GATE", "BUPT_LIB", "time", "walk")

    assert result["route_source"] == "local"
    assert result["route_source_label"] == "本地算法"
    assert result["algorithm_path_codes"] == result["path_codes"]
    assert "external_provider" not in result
    assert "provider_distance_m" not in result
    assert "provider_estimated_minutes" not in result
    assert "external_fallback_reason" not in result


def test_wander_route_returns_closed_loop_with_auto_stops():
    service = local_route_service()
    result = service.plan_wander(
        scene_name="BUPT_Main_Campus",
        start_code="BUPT_GATE",
        transport_mode="walk",
        duration_minutes=35,
    )

    assert result["route_intent"] == "wander"
    assert result["path_codes"][0] == "BUPT_GATE"
    assert result["path_codes"][-1] == "BUPT_GATE"
    assert len(result["ordered_stop_codes"]) >= 3
    assert result["segments"]


def test_plan_multi_empty_targets_returns_origin_only():
    service = local_route_service()
    result = service.plan_multi("BUPT_Main_Campus", "BUPT_GATE", [], "distance", "walk")

    assert result["path_codes"] == ["BUPT_GATE"]
    assert result["ordered_stop_codes"] == ["BUPT_GATE"]
    assert result["optimization_label"] == "无目标点"


def test_indoor_service_wheelchair_route_avoids_stairs_edges():
    service = IndoorNavigationService(get_json_repository())
    result = service.plan_route(
        building_code="BUPT_LIB",
        start_node_code="BUPT_LIB_GATE_L1",
        end_node_code="BUPT_LIB_ARCHIVE_L3",
        strategy="accessible",
        mobility_mode="wheelchair",
    )

    assert result["path_node_codes"]
    assert all(step["connector"] != "stairs" for step in result["steps"])


def test_huffman_codec_roundtrip():
    codec = HuffmanCodec()
    encoded, codes = codec.encode("travel diary")
    decoded = codec.decode(encoded, codes)
    assert decoded == "travel diary"


def test_compression_service_returns_ratio_metrics():
    result = CompressionService().compress("故宫故宫故宫故宫")
    assert "encoded" in result
    assert "codes" in result
    assert result["original_bits"] > 0
    assert result["compressed_bits"] >= 0
    assert 0 <= result["compression_ratio"] <= 1


def test_diary_aigc_service_generates_storyboard():
    diary = {
        "id": 99,
        "title": "颐和园漫游",
        "destination_name": "颐和园",
        "content": "从东门入园后先去长廊拍照。随后在昆明湖边散步，最后看日落返程。",
        "media_urls": ["/media/destinations/sample-01.jpg", "/media/destinations/sample-02.jpg"],
    }
    result = DiaryAIGCService().generate_animation(diary)

    assert result["generation_mode"] == "aigc-storyboard-v1"
    assert len(result["shots"]) >= 3
    assert result["total_duration_seconds"] > 0
    assert result["keywords"]


def test_search_service_fuzzy_results_are_ranked_by_heat_and_rating():
    class FakeRepository:
        @staticmethod
        def destinations() -> list[dict]:
            return [
                {
                    "source_id": "1",
                    "name": "故宫博物院",
                    "district": "东城",
                    "description": "皇家宫殿",
                    "category": "scenic",
                    "heat": 900,
                    "rating": 4.7,
                },
                {
                    "source_id": "2",
                    "name": "故宫角楼",
                    "district": "东城",
                    "description": "故宫拍照机位",
                    "category": "scenic",
                    "heat": 1200,
                    "rating": 4.5,
                },
            ]

    results = SearchService(FakeRepository()).fuzzy_search("故宫", ["故宫"], category="scenic")
    assert [item["source_id"] for item in results] == ["2", "1"]
