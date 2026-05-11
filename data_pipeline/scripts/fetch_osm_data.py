from __future__ import annotations

import json
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "datasets" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# 城市中心坐标和搜索半径（度）
CITY_BBOX = {
    "北京": {"lat": 39.9042, "lon": 116.4074, "delta": 0.5},
    "上海": {"lat": 31.2304, "lon": 121.4737, "delta": 0.5},
    "广州": {"lat": 23.1291, "lon": 113.2644, "delta": 0.4},
    "深圳": {"lat": 22.5431, "lon": 114.0579, "delta": 0.4},
    "成都": {"lat": 30.6586, "lon": 104.0648, "delta": 0.4},
    "南京": {"lat": 32.0603, "lon": 118.7969, "delta": 0.35},
    "苏州": {"lat": 31.2990, "lon": 120.5853, "delta": 0.35},
}

DESTINATION_QUERY_TEMPLATE = """
[out:json][timeout:120];
area["name"="{city_name}"]["admin_level"~"4|6"]->.searchArea;
(
  node["amenity"="university"](area.searchArea);
  way["amenity"="university"](area.searchArea);
  relation["amenity"="university"](area.searchArea);
  node["tourism"~"attraction|museum|theme_park|zoo|viewpoint|artwork"](area.searchArea);
  way["tourism"~"attraction|museum|theme_park|zoo|viewpoint|artwork"](area.searchArea);
  relation["tourism"~"attraction|museum|theme_park|zoo|viewpoint|artwork"](area.searchArea);
  node["leisure"~"park|garden"](area.searchArea);
  way["leisure"~"park|garden"](area.searchArea);
);
out center tags;
"""

# Fallback: 使用 bbox 直接查询（不依赖 area 边界）
BBOX_DESTINATION_QUERY_TEMPLATE = """
[out:json][timeout:120];
(
  node["amenity"="university"]({south},{west},{north},{east});
  way["amenity"="university"]({south},{west},{north},{east});
  relation["amenity"="university"]({south},{west},{north},{east});
  node["tourism"~"attraction|museum|theme_park|zoo|viewpoint|artwork"]({south},{west},{north},{east});
  way["tourism"~"attraction|museum|theme_park|zoo|viewpoint|artwork"]({south},{west},{north},{east});
  relation["tourism"~"attraction|museum|theme_park|zoo|viewpoint|artwork"]({south},{west},{north},{east});
  node["leisure"~"park|garden"]({south},{west},{north},{east});
  way["leisure"~"park|garden"]({south},{west},{north},{east});
);
out center tags;
"""

# 城市名到 OSM 地区名称的映射
CITY_MAPPING = {
    "北京": "北京市",
    "上海": "上海市",
    "广州": "广州市",
    "深圳": "深圳市",
    "成都": "成都市",
    "南京": "南京市",
    "苏州": "苏州市",
}

SCENE_QUERIES = {
    "bupt_scene": """
    [out:json][timeout:120];
    (
      nwr["name"]["building"](39.9580,116.3480,39.9690,116.3695);
      nwr["name"]["amenity"~"library|college|university|school|cafe|restaurant|fast_food|bank|hospital|toilets|post_office|charging_station|bicycle_parking|parking"](39.9580,116.3480,39.9690,116.3695);
      nwr["name"]["shop"](39.9580,116.3480,39.9690,116.3695);
      nwr["name"]["tourism"](39.9580,116.3480,39.9690,116.3695);
      nwr["name"]["leisure"](39.9580,116.3480,39.9690,116.3695);
      nwr["name"]["office"](39.9580,116.3480,39.9690,116.3695);
    );
    out center tags;
    """,
    "bupt_foods": """
    [out:json][timeout:120];
    (
      nwr["name"]["amenity"~"restaurant|cafe|fast_food|food_court"](39.9580,116.3480,39.9690,116.3695);
    );
    out center tags;
    """,
    "summer_palace_scene": """
    [out:json][timeout:120];
    (
      nwr["name"]["building"](39.9850,116.2630,40.0120,116.2920);
      nwr["name"]["amenity"~"toilets|restaurant|cafe|fast_food|parking|ticket_booth|police|hospital|charging_station"](39.9850,116.2630,40.0120,116.2920);
      nwr["name"]["shop"](39.9850,116.2630,40.0120,116.2920);
      nwr["name"]["tourism"](39.9850,116.2630,40.0120,116.2920);
      nwr["name"]["historic"](39.9850,116.2630,40.0120,116.2920);
      nwr["name"]["leisure"](39.9850,116.2630,40.0120,116.2920);
    );
    out center tags;
    """,
    "summer_palace_foods": """
    [out:json][timeout:120];
    (
      node["amenity"~"restaurant|cafe|fast_food|food_court"](39.9850,116.2630,40.0120,116.2920);
      way["amenity"~"restaurant|cafe|fast_food|food_court"](39.9850,116.2630,40.0120,116.2920);
    );
    out center tags;
    """,
}

# 美食查询模板（使用 area）
FOOD_QUERY_TEMPLATE = """
[out:json][timeout:120];
area["name"="{city_name}"]["admin_level"~"4|6"]->.searchArea;
(
  node["amenity"~"restaurant|cafe|fast_food|food_court|bar|pub|bakery"](area.searchArea);
  way["amenity"~"restaurant|cafe|fast_food|food_court|bar|pub|bakery"](area.searchArea);
  relation["amenity"~"restaurant|cafe|fast_food|food_court|bar|pub|bakery"](area.searchArea);
);
out center tags;
"""

# Fallback: 美食 bbox 查询
BBOX_FOOD_QUERY_TEMPLATE = """
[out:json][timeout:120];
(
  node["amenity"~"restaurant|cafe|fast_food|food_court|bar|pub|bakery"]({south},{west},{north},{east});
  way["amenity"~"restaurant|cafe|fast_food|food_court|bar|pub|bakery"]({south},{west},{north},{east});
  relation["amenity"~"restaurant|cafe|fast_food|food_court|bar|pub|bakery"]({south},{west},{north},{east});
);
out center tags;
"""

# 目的地查询使用的城市列表
DESTINATION_CITIES = ["北京", "上海", "广州", "深圳", "成都", "南京", "苏州"]

# 城市代码（用于文件名）
CITY_CODES = {
    "北京": "beijing",
    "上海": "shanghai",
    "广州": "guangzhou",
    "深圳": "shenzhen",
    "成都": "chengdu",
    "南京": "nanjing",
    "苏州": "suzhou",
}


def query_overpass(query: str) -> dict:
    last_error: Exception | None = None
    for url in OVERPASS_URLS:
        try:
            with httpx.Client(
                timeout=180.0,
                headers={"User-Agent": "travel-system-course-project/1.0"},
                trust_env=False,
            ) as client:
                response = client.post(url, data={"data": query})
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            last_error = exc
    if last_error is None:
        raise RuntimeError("query_overpass failed without an exception")
    raise last_error


def save_json(name: str, payload: dict) -> None:
    target = RAW_DIR / name
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"saved {target}")


def build_destination_query(city_name: str) -> str:
    osm_name = CITY_MAPPING[city_name]
    return DESTINATION_QUERY_TEMPLATE.format(city_name=osm_name)


def build_bbox_destination_query(city_name: str) -> str:
    bbox = CITY_BBOX[city_name]
    south = bbox["lat"] - bbox["delta"]
    north = bbox["lat"] + bbox["delta"]
    west = bbox["lon"] - bbox["delta"]
    east = bbox["lon"] + bbox["delta"]
    return BBOX_DESTINATION_QUERY_TEMPLATE.format(
        south=south, north=north, west=west, east=east
    )


def build_food_query(city_name: str) -> str:
    osm_name = CITY_MAPPING[city_name]
    return FOOD_QUERY_TEMPLATE.format(city_name=osm_name)


def build_bbox_food_query(city_name: str) -> str:
    bbox = CITY_BBOX[city_name]
    south = bbox["lat"] - bbox["delta"]
    north = bbox["lat"] + bbox["delta"]
    west = bbox["lon"] - bbox["delta"]
    east = bbox["lon"] + bbox["delta"]
    return BBOX_FOOD_QUERY_TEMPLATE.format(
        south=south, north=north, west=west, east=east
    )


def main() -> None:
    # 采集各城市目的地
    for city in DESTINATION_CITIES:
        code = CITY_CODES[city]
        # 先尝试 area 查询
        query = build_destination_query(city)
        try:
            result = query_overpass(query)
            if result.get("elements"):
                save_json(f"{code}_destinations_osm.json", result)
                print(f"  {city}: area query ok, {len(result['elements'])} elements")
                continue
        except Exception as exc:
            print(f"  {city}: area query failed: {exc}")
        # fallback: bbox 查询
        try:
            bbox_query = build_bbox_destination_query(city)
            result = query_overpass(bbox_query)
            save_json(f"{code}_destinations_osm.json", result)
            print(f"  {city}: bbox query ok, {len(result.get('elements', []))} elements")
        except Exception as exc:
            print(f"skip {city} ({code}): {exc}")

    # 采集各城市美食
    for city in DESTINATION_CITIES:
        code = CITY_CODES[city]
        # 先尝试 area 查询
        query = build_food_query(city)
        try:
            result = query_overpass(query)
            if result.get("elements"):
                save_json(f"{code}_foods_osm.json", result)
                print(f"  {city} foods: area query ok, {len(result['elements'])} elements")
                continue
        except Exception as exc:
            print(f"  {city} foods: area query failed: {exc}")
        # fallback: bbox 查询
        try:
            bbox_query = build_bbox_food_query(city)
            result = query_overpass(bbox_query)
            save_json(f"{code}_foods_osm.json", result)
            print(f"  {city} foods: bbox query ok, {len(result.get('elements', []))} elements")
        except Exception as exc:
            print(f"skip {city} foods ({code}): {exc}")

    # 采集场景数据（仅北京BUPT和颐和园）
    for name, query in SCENE_QUERIES.items():
        try:
            save_json(f"{name}.json", query_overpass(query))
        except Exception as exc:
            print(f"skip {name}: {exc}")


if __name__ == "__main__":
    main()