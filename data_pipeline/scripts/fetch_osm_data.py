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

DESTINATION_QUERY = """
[out:json][timeout:120];
area["name"="北京市"]["admin_level"="4"]->.searchArea;
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
      nwr["name"]["amenity"~"restaurant|cafe|fast_food|food_court"](39.9850,116.2630,40.0120,116.2920);
    );
    out center tags;
    """,
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
        except Exception as exc:  # pragma: no cover - network fallback
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


def main() -> None:
    save_json("beijing_destinations_osm.json", query_overpass(DESTINATION_QUERY))
    for name, query in SCENE_QUERIES.items():
        try:
            save_json(f"{name}.json", query_overpass(query))
        except Exception as exc:  # pragma: no cover - network/data fallback
            print(f"skip {name}: {exc}")


if __name__ == "__main__":
    main()
