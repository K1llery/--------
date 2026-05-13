from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = ROOT / "tourism-system-main" / "backend" / "data"
DEFAULT_OUTPUT_PATH = ROOT / "datasets" / "source_maps" / "bupt_campus_map.json"
BUPT_PLACE_ID = "place_001"
BUPT_SCENE_NAME = "BUPT_Main_Campus"
SOURCE_DATASET = "tourism-system-main"
DEFAULT_MIN_INTERSECTIONS = 20
DEFAULT_MIN_EDGES = 200


def load_json(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def location_of(item: dict[str, Any]) -> tuple[float, float]:
    location = item.get("location") or {}
    return float(location["lat"]), float(location["lng"])


def normalized_code(legacy_id: str, node_type: str | None = None) -> str:
    if node_type == "facility" and not legacy_id.startswith("facility_"):
        return f"LEGACY_facility_{legacy_id}"
    return f"LEGACY_{legacy_id}"


def normalize_facility_type(raw_type: str | None, name: str = "") -> tuple[str, str]:
    text = f"{raw_type or ''}{name}"
    if any(token in text for token in ("卫生间", "厕所", "洗手间", "公厕")):
        return "toilets", "restroom"
    if any(token in text for token in ("餐", "食堂", "咖啡", "饮", "饭")):
        return "restaurant", "restaurant"
    if any(token in text for token in ("超市", "便利", "商店", "店铺")):
        return "supermarket", "supermarket"
    if any(token in text for token in ("公交", "车站", "站台")):
        return "transit", "transit"
    if any(token in text for token in ("ATM", "电话", "服务")):
        return "service", "service"
    return "service", "service"


def normalize_modes(vehicles: list[str] | None) -> list[str]:
    mapping = {
        "步行": "walk",
        "自行车": "bike",
        "电瓶车": "shuttle",
        "摆渡车": "shuttle",
    }
    modes: list[str] = []
    for vehicle in vehicles or []:
        mode = mapping.get(vehicle)
        if mode and mode not in modes:
            modes.append(mode)
    return modes or ["walk"]


def base_node(
    *,
    legacy_id: str,
    code: str,
    name: str,
    node_type: str,
    latitude: float,
    longitude: float,
    legacy_type: str | None = None,
) -> dict[str, Any]:
    node = {
        "code": code,
        "name": name,
        "node_type": node_type,
        "latitude": latitude,
        "longitude": longitude,
        "legacy_id": legacy_id,
        "source_dataset": SOURCE_DATASET,
    }
    if legacy_type:
        node["legacy_type"] = legacy_type
    return node


def import_bupt_map(
    source_dir: Path = DEFAULT_SOURCE_DIR,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    *,
    min_intersections: int = DEFAULT_MIN_INTERSECTIONS,
    min_edges: int = DEFAULT_MIN_EDGES,
) -> dict[str, int]:
    places = load_json(source_dir / "places.json")
    buildings_raw = [item for item in load_json(source_dir / "buildings.json") if item.get("placeId") == BUPT_PLACE_ID]
    facilities_raw = [
        item for item in load_json(source_dir / "facilities.json") if item.get("placeId") == BUPT_PLACE_ID
    ]
    roads_raw = load_json(source_dir / "roads.json")
    place = next((item for item in places if item.get("id") == BUPT_PLACE_ID), None)
    if place is None:
        raise ValueError(f"missing BUPT place {BUPT_PLACE_ID}")

    raw_to_code: dict[str, str] = {}
    raw_to_type: dict[str, str] = {}
    nodes: list[dict[str, Any]] = []
    buildings: list[dict[str, Any]] = []
    facilities: list[dict[str, Any]] = []
    intersections = 0

    place_latitude, place_longitude = location_of(place)
    place_code = normalized_code(place["id"])
    raw_to_code[place["id"]] = place_code
    raw_to_type[place["id"]] = "place"
    nodes.append(
        base_node(
            legacy_id=place["id"],
            code=place_code,
            name=place.get("name") or "北京邮电大学",
            node_type="place",
            latitude=place_latitude,
            longitude=place_longitude,
            legacy_type=place.get("type"),
        )
    )

    for item in sorted(buildings_raw, key=lambda value: value["id"]):
        latitude, longitude = location_of(item)
        code = normalized_code(item["id"])
        raw_to_code[item["id"]] = code
        raw_to_type[item["id"]] = "building"
        node = base_node(
            legacy_id=item["id"],
            code=code,
            name=item.get("name") or item["id"],
            node_type="building",
            latitude=latitude,
            longitude=longitude,
            legacy_type=item.get("type"),
        )
        nodes.append(node)
        buildings.append(
            {
                "scene_name": BUPT_SCENE_NAME,
                "code": code,
                "name": node["name"],
                "latitude": latitude,
                "longitude": longitude,
                "building_type": item.get("type") or "building",
                "legacy_id": item["id"],
                "source_dataset": SOURCE_DATASET,
            }
        )

    for item in sorted(facilities_raw, key=lambda value: value["id"]):
        latitude, longitude = location_of(item)
        legacy_id = item["id"]
        if legacy_id.startswith("intersection_"):
            code = normalized_code(legacy_id)
            raw_to_code[legacy_id] = code
            raw_to_type[legacy_id] = "intersection"
            intersections += 1
            nodes.append(
                base_node(
                    legacy_id=legacy_id,
                    code=code,
                    name=f"路口 {legacy_id.removeprefix('intersection_')}",
                    node_type="intersection",
                    latitude=latitude,
                    longitude=longitude,
                    legacy_type=item.get("type"),
                )
            )
            continue

        code = normalized_code(legacy_id, "facility")
        raw_to_code[legacy_id] = code
        raw_to_type[legacy_id] = "facility"
        facility_type, normalized_type = normalize_facility_type(item.get("type"), item.get("name", ""))
        node = base_node(
            legacy_id=legacy_id,
            code=code,
            name=item.get("name") or legacy_id,
            node_type="facility",
            latitude=latitude,
            longitude=longitude,
            legacy_type=item.get("type"),
        )
        nodes.append(node)
        facilities.append(
            {
                "scene_name": BUPT_SCENE_NAME,
                "code": code,
                "name": node["name"],
                "facility_type": facility_type,
                "normalized_type": normalized_type,
                "facility_label": item.get("type") or "服务设施",
                "latitude": latitude,
                "longitude": longitude,
                "legacy_id": legacy_id,
                "source_dataset": SOURCE_DATASET,
            }
        )

    road_endpoints = {endpoint for road in roads_raw for endpoint in (road.get("from"), road.get("to"))}
    unknown_endpoints = sorted(endpoint for endpoint in road_endpoints if endpoint not in raw_to_code)
    if unknown_endpoints:
        preview = ", ".join(unknown_endpoints[:10])
        raise ValueError(f"unknown road endpoints: {preview}")

    if intersections < min_intersections:
        raise ValueError(f"imported only {intersections} intersections, expected at least {min_intersections}")

    edges: list[dict[str, Any]] = []
    for road in sorted(roads_raw, key=lambda value: value["id"]):
        source_code = raw_to_code[road["from"]]
        target_code = raw_to_code[road["to"]]
        base_edge = {
            "scene_name": BUPT_SCENE_NAME,
            "distance": round(float(road.get("distance") or 0.0), 2),
            "congestion": float(road.get("congestionRate") or 1.0),
            "allowed_modes": normalize_modes(road.get("allowedVehicles")),
            "walk_speed": float(road.get("idealSpeed") or 1.2),
            "bike_speed": float(road.get("idealSpeed") or 1.2) * 3,
            "shuttle_speed": float(road.get("idealSpeed") or 1.2) * 5,
            "road_type": road.get("roadType") or "road",
            "source_dataset": SOURCE_DATASET,
            "legacy_road_id": road.get("id"),
            "edge_source": {
                "dataset": SOURCE_DATASET,
                "legacy_road_id": road.get("id"),
                "legacy_from": road["from"],
                "legacy_to": road["to"],
                "legacy_from_type": raw_to_type[road["from"]],
                "legacy_to_type": raw_to_type[road["to"]],
            },
        }
        edges.append({**base_edge, "source_code": source_code, "target_code": target_code})
        edges.append({**base_edge, "source_code": target_code, "target_code": source_code})

    if len(edges) < min_edges:
        raise ValueError(f"imported only {len(edges)} directed edges, expected at least {min_edges}")

    payload = {
        "source": SOURCE_DATASET,
        "source_place_id": BUPT_PLACE_ID,
        "scene_name": BUPT_SCENE_NAME,
        "label": place.get("name") or "北京邮电大学",
        "center": {"latitude": place_latitude, "longitude": place_longitude},
        "nodes": nodes,
        "buildings": buildings,
        "facilities": facilities,
        "edges": edges,
        "import_summary": {
            "nodes": len(nodes),
            "buildings": len(buildings),
            "facilities": len(facilities),
            "intersections": intersections,
            "edges": len(edges),
            "source_roads": len(roads_raw),
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload["import_summary"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Import legacy BUPT map data into a project-owned source map.")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--min-intersections", type=int, default=DEFAULT_MIN_INTERSECTIONS)
    parser.add_argument("--min-edges", type=int, default=DEFAULT_MIN_EDGES)
    args = parser.parse_args()

    summary = import_bupt_map(
        source_dir=args.source_dir,
        output_path=args.output_path,
        min_intersections=args.min_intersections,
        min_edges=args.min_edges,
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
