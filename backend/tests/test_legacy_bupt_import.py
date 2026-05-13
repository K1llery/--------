import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.import_legacy_bupt_map import import_bupt_map  # noqa: E402


def write_json(path: Path, payload: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_import_bupt_map_normalizes_nodes_edges_and_facilities(tmp_path):
    source_dir = tmp_path / "legacy"
    output_path = tmp_path / "bupt_campus_map.json"
    write_json(
        source_dir / "places.json",
        [
            {
                "id": "place_001",
                "name": "北京邮电大学",
                "type": "校园",
                "location": {"lat": 39.9577, "lng": 116.3577},
            }
        ],
    )
    write_json(
        source_dir / "buildings.json",
        [
            {
                "id": "building_001",
                "name": "教学楼",
                "type": "教学楼",
                "placeId": "place_001",
                "location": {"lat": 39.958, "lng": 116.358},
            }
        ],
    )
    write_json(
        source_dir / "facilities.json",
        [
            {
                "id": "intersection_001",
                "name": "intersection_001",
                "type": "路口",
                "placeId": "place_001",
                "location": {"lat": 39.9585, "lng": 116.3585},
            },
            {
                "id": "toilet_facility_001",
                "name": "公共厕所",
                "type": "卫生间",
                "placeId": "place_001",
                "location": {"lat": 39.959, "lng": 116.359},
            },
        ],
    )
    write_json(
        source_dir / "roads.json",
        [
            {
                "id": "road_001",
                "from": "building_001",
                "to": "intersection_001",
                "distance": 12.5,
                "idealSpeed": 1.2,
                "congestionRate": 0.8,
                "allowedVehicles": ["步行"],
                "roadType": "步行道",
            },
            {
                "id": "road_002",
                "from": "intersection_001",
                "to": "toilet_facility_001",
                "distance": 20.0,
                "idealSpeed": 3.5,
                "congestionRate": 0.9,
                "allowedVehicles": ["步行", "自行车"],
                "roadType": "校园道路",
            },
        ],
    )

    summary = import_bupt_map(
        source_dir=source_dir,
        output_path=output_path,
        min_intersections=1,
        min_edges=4,
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert summary["buildings"] == 1
    assert summary["facilities"] == 1
    assert summary["intersections"] == 1
    assert summary["edges"] == 4
    assert payload["scene_name"] == "BUPT_Main_Campus"
    assert {node["node_type"] for node in payload["nodes"]} == {"building", "facility", "intersection", "place"}
    assert any(node["code"] == "LEGACY_intersection_001" for node in payload["nodes"])
    assert payload["buildings"][0]["code"] == "LEGACY_building_001"
    assert payload["facilities"][0]["code"] == "LEGACY_facility_toilet_facility_001"
    assert payload["facilities"][0]["normalized_type"] == "restroom"
    assert payload["edges"][0]["source_dataset"] == "tourism-system-main"
    assert payload["edges"][0]["allowed_modes"] == ["walk"]
    assert payload["edges"][0]["source_code"].startswith("LEGACY_")
    assert payload["edges"][0]["target_code"].startswith("LEGACY_")


def test_import_bupt_map_rejects_roads_with_unknown_endpoints(tmp_path):
    source_dir = tmp_path / "legacy"
    write_json(
        source_dir / "places.json",
        [{"id": "place_001", "name": "北京邮电大学", "location": {"lat": 39.9577, "lng": 116.3577}}],
    )
    write_json(source_dir / "buildings.json", [])
    write_json(source_dir / "facilities.json", [])
    write_json(
        source_dir / "roads.json",
        [{"id": "road_001", "from": "missing_a", "to": "missing_b", "distance": 1}],
    )

    try:
        import_bupt_map(
            source_dir=source_dir,
            output_path=tmp_path / "bupt_campus_map.json",
            min_intersections=0,
            min_edges=0,
        )
    except ValueError as exc:
        assert "unknown road endpoints" in str(exc)
    else:
        raise AssertionError("expected unknown endpoints to be rejected")
