from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import delete, text

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import (
    Building,
    Destination,
    Diary,
    DiaryRating,
    Edge,
    Facility,
    Food,
    IndoorBuilding,
    IndoorEdge,
    IndoorNode,
    Scene,
    SceneNode,
    Session,
    User,
    UserFavoriteDestination,
    UserFavoriteRoute,
)


def _load_json(file_path: Path) -> list[dict]:
    if not file_path.exists():
        return []
    return json.loads(file_path.read_text(encoding="utf-8"))


def _sync_sequence(table_name: str) -> None:
    with SessionLocal() as db:
        db.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
                f"COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table_name};"
            )
        )
        db.commit()


def seed_dataset(dataset_dir: Path) -> None:
    destinations = _load_json(dataset_dir / "destinations.json")
    featured_destinations = _load_json(dataset_dir / "featured_destinations.json")
    scenes = _load_json(dataset_dir / "scenes.json")
    buildings = _load_json(dataset_dir / "buildings.json")
    facilities = _load_json(dataset_dir / "facilities.json")
    edges = _load_json(dataset_dir / "edges.json")
    foods = _load_json(dataset_dir / "foods.json")
    indoors = _load_json(dataset_dir / "indoors.json")
    users = _load_json(dataset_dir / "users.json")
    sessions = _load_json(dataset_dir / "sessions.json")
    diaries = _load_json(dataset_dir / "diaries.json")
    diary_ratings = _load_json(dataset_dir / "diary_ratings.json")

    featured_by_source_id = {item.get("source_id") for item in featured_destinations if item.get("source_id")}
    destination_map: dict[str, dict] = {
        item["source_id"]: {**item, "is_featured": item.get("source_id") in featured_by_source_id}
        for item in destinations
        if item.get("source_id")
    }
    for item in featured_destinations:
        source_id = item.get("source_id")
        if not source_id:
            continue
        current = destination_map.get(source_id, {})
        destination_map[source_id] = {
            **current,
            **item,
            "is_featured": True,
        }

    with SessionLocal() as db:
        with db.begin():
            db.execute(delete(DiaryRating))
            db.execute(delete(UserFavoriteRoute))
            db.execute(delete(UserFavoriteDestination))
            db.execute(delete(Session))
            db.execute(delete(Diary))
            db.execute(delete(IndoorEdge))
            db.execute(delete(IndoorNode))
            db.execute(delete(IndoorBuilding))
            db.execute(delete(Edge))
            db.execute(delete(Facility))
            db.execute(delete(Building))
            db.execute(delete(SceneNode))
            db.execute(delete(Food))
            db.execute(delete(Destination))
            db.execute(delete(User))
            db.execute(delete(Scene))

            for item in destination_map.values():
                db.add(
                    Destination(
                        source_id=str(item.get("source_id") or ""),
                        name=str(item.get("name") or ""),
                        city=str(item.get("city") or ""),
                        category=str(item.get("category") or ""),
                        district=str(item.get("district") or ""),
                        address=str(item.get("address") or ""),
                        latitude=float(item.get("latitude") or 0.0),
                        longitude=float(item.get("longitude") or 0.0),
                        rating=float(item["rating"]) if item.get("rating") is not None else None,
                        heat=float(item["heat"]) if item.get("heat") is not None else None,
                        heat_metric=str(item.get("heat_metric") or ""),
                        tags=",".join(item.get("tags") or []),
                        description=str(item.get("description") or ""),
                        image_url=str(item.get("image_url") or ""),
                        image_source_name=str(item.get("image_source_name") or ""),
                        image_source_url=str(item.get("image_source_url") or ""),
                        source_name=str(item.get("source_name") or ""),
                        source_url=str(item.get("source_url") or ""),
                        fetched_date=str(item.get("fetched_date") or ""),
                        is_featured=bool(item.get("is_featured")),
                        rating_source_name=(
                            str(item.get("rating_source_name")) if item.get("rating_source_name") else None
                        ),
                        rating_source_url=str(item.get("rating_source_url")) if item.get("rating_source_url") else None,
                        heat_source_name=str(item.get("heat_source_name")) if item.get("heat_source_name") else None,
                        heat_source_url=str(item.get("heat_source_url")) if item.get("heat_source_url") else None,
                    )
                )

            scene_entities: dict[str, Scene] = {}
            for item in scenes:
                scene = Scene(
                    name=str(item.get("name") or ""),
                    label=str(item.get("label") or ""),
                    city=str(item.get("city") or ""),
                    supports_routing=bool(item.get("supports_routing", True)),
                )
                db.add(scene)
                scene_entities[scene.name] = scene

            db.flush()
            scene_id_by_name = {name: scene.id for name, scene in scene_entities.items()}

            for item in scenes:
                scene_id = scene_id_by_name.get(str(item.get("name") or ""))
                if scene_id is None:
                    continue
                for node in item.get("nodes") or []:
                    db.add(
                        SceneNode(
                            scene_id=scene_id,
                            code=str(node.get("code") or ""),
                            name=str(node.get("name") or ""),
                            latitude=float(node.get("latitude") or 0.0),
                            longitude=float(node.get("longitude") or 0.0),
                        )
                    )

            for item in buildings:
                scene_id = scene_id_by_name.get(str(item.get("scene_name") or ""))
                if scene_id is None:
                    continue
                db.add(
                    Building(
                        scene_id=scene_id,
                        code=str(item.get("code") or ""),
                        name=str(item.get("name") or ""),
                        building_type=str(item.get("building_type") or ""),
                        latitude=float(item.get("latitude") or 0.0),
                        longitude=float(item.get("longitude") or 0.0),
                    )
                )

            for item in facilities:
                scene_id = scene_id_by_name.get(str(item.get("scene_name") or ""))
                if scene_id is None:
                    continue
                db.add(
                    Facility(
                        scene_id=scene_id,
                        code=str(item.get("code") or ""),
                        name=str(item.get("name") or ""),
                        facility_type=str(item.get("facility_type") or ""),
                        latitude=float(item.get("latitude") or 0.0),
                        longitude=float(item.get("longitude") or 0.0),
                    )
                )

            for item in edges:
                scene_id = scene_id_by_name.get(str(item.get("scene_name") or ""))
                if scene_id is None:
                    continue
                db.add(
                    Edge(
                        scene_id=scene_id,
                        source_code=str(item.get("source_code") or ""),
                        target_code=str(item.get("target_code") or ""),
                        distance=float(item.get("distance") or 0.0),
                        congestion=float(item.get("congestion") or 1.0),
                        walk_speed=float(item.get("walk_speed") or 1.1),
                        bike_speed=float(item.get("bike_speed") or 3.5),
                        shuttle_speed=float(item.get("shuttle_speed") or 4.8),
                        allowed_modes=",".join(item.get("allowed_modes") or ["walk"]),
                    )
                )

            for item in foods:
                db.add(
                    Food(
                        source_id=str(item.get("source_id") or ""),
                        name=str(item.get("name") or ""),
                        city=str(item.get("city") or ""),
                        destination_name=str(item.get("destination_name") or ""),
                        cuisine=str(item.get("cuisine") or ""),
                        venue_name=str(item.get("venue_name") or ""),
                        latitude=float(item.get("latitude") or 0.0),
                        longitude=float(item.get("longitude") or 0.0),
                        rating=float(item["rating"]) if item.get("rating") is not None else None,
                        heat=float(item["heat"]) if item.get("heat") is not None else None,
                        heat_metric=str(item.get("heat_metric") or ""),
                        source_name=str(item.get("source_name") or ""),
                        source_url=str(item.get("source_url") or ""),
                        description=str(item.get("description") or ""),
                        image_url=str(item.get("image_url") or ""),
                        image_source_name=str(item.get("image_source_name") or ""),
                        image_source_url=str(item.get("image_source_url") or ""),
                        fetched_date=str(item.get("fetched_date") or ""),
                    )
                )

            indoor_entities: dict[str, IndoorBuilding] = {}
            for item in indoors:
                building = IndoorBuilding(
                    building_code=str(item.get("building_code") or ""),
                    building_name=str(item.get("building_name") or ""),
                    scene_name=str(item.get("scene_name") or ""),
                )
                db.add(building)
                indoor_entities[building.building_code] = building

            db.flush()
            indoor_id_by_code = {code: item.id for code, item in indoor_entities.items()}

            for item in indoors:
                building_id = indoor_id_by_code.get(str(item.get("building_code") or ""))
                if building_id is None:
                    continue

                for node in item.get("nodes") or []:
                    db.add(
                        IndoorNode(
                            building_id=building_id,
                            code=str(node.get("code") or ""),
                            name=str(node.get("name") or ""),
                            floor=int(node.get("floor") or 1),
                            node_type=str(node.get("node_type") or ""),
                        )
                    )

                for edge in item.get("edges") or []:
                    db.add(
                        IndoorEdge(
                            building_id=building_id,
                            source_code=str(edge.get("source") or ""),
                            target_code=str(edge.get("target") or ""),
                            distance=float(edge.get("distance") or 0.0),
                            kind=str(edge.get("kind") or "walk"),
                            wait_seconds=float(edge.get("wait_seconds") or 0.0),
                            bidirectional=bool(edge.get("bidirectional", True)),
                        )
                    )

            user_id_set: set[int] = set()
            for item in users:
                user_id = int(item.get("id") or 0)
                user_id_set.add(user_id)
                db.add(
                    User(
                        id=user_id,
                        username=str(item.get("username") or ""),
                        display_name=str(item.get("display_name") or item.get("username") or ""),
                        interests=str(item.get("interests") or ""),
                        password_hash=str(item.get("password_hash") or ""),
                        created_at=str(item.get("created_at") or ""),
                        last_login_at=str(item.get("last_login_at") or ""),
                    )
                )

            for item in users:
                user_id = int(item.get("id") or 0)
                for source_id in item.get("favorite_destination_ids") or []:
                    db.add(
                        UserFavoriteDestination(
                            user_id=user_id,
                            destination_source_id=str(source_id),
                        )
                    )
                for snapshot in item.get("favorite_route_snapshots") or []:
                    db.add(
                        UserFavoriteRoute(
                            user_id=user_id,
                            scene_name=str(snapshot.get("scene_name") or ""),
                            strategy=str(snapshot.get("strategy") or ""),
                            transport_mode=str(snapshot.get("transport_mode") or ""),
                            path_codes=json.dumps(snapshot.get("path_codes") or [], ensure_ascii=False),
                            path_names=json.dumps(snapshot.get("path_names") or [], ensure_ascii=False),
                            total_distance_m=float(snapshot.get("total_distance_m") or 0.0),
                            estimated_minutes=float(snapshot.get("estimated_minutes") or 0.0),
                            explanation=str(snapshot.get("explanation") or ""),
                            saved_at=str(snapshot.get("saved_at") or ""),
                        )
                    )

            for item in sessions:
                user_id = int(item.get("user_id") or 0)
                if user_id not in user_id_set:
                    continue
                db.add(
                    Session(
                        token=str(item.get("token") or ""),
                        user_id=user_id,
                        created_at=str(item.get("created_at") or ""),
                    )
                )

            diary_id_set: set[int] = set()
            for item in diaries:
                diary_id = int(item.get("id") or 0)
                author_id = int(item.get("author_id") or 0)
                if author_id not in user_id_set:
                    continue
                diary_id_set.add(diary_id)
                db.add(
                    Diary(
                        id=diary_id,
                        title=str(item.get("title") or ""),
                        destination_name=str(item.get("destination_name") or ""),
                        content=str(item.get("content") or ""),
                        views=int(item.get("views") or 0),
                        rating=float(item.get("rating") or 0.0),
                        media_urls=json.dumps(item.get("media_urls") or [], ensure_ascii=False),
                        author_id=author_id,
                        author_name=str(item.get("author_name") or ""),
                        created_at=str(item.get("created_at") or ""),
                    )
                )

            for item in diary_ratings:
                user_id = int(item.get("user_id") or 0)
                diary_id = int(item.get("diary_id") or 0)
                if user_id not in user_id_set or diary_id not in diary_id_set:
                    continue
                db.add(
                    DiaryRating(
                        id=int(item.get("id") or 0),
                        diary_id=diary_id,
                        user_id=user_id,
                        score=float(item.get("score") or 0.0),
                        updated_at=str(item.get("updated_at") or ""),
                    )
                )

    for table_name in [
        "destinations",
        "scenes",
        "scene_nodes",
        "buildings",
        "facilities",
        "edges",
        "foods",
        "indoor_buildings",
        "indoor_nodes",
        "indoor_edges",
        "users",
        "sessions",
        "user_favorite_destinations",
        "user_favorite_routes",
        "diaries",
        "diary_ratings",
    ]:
        _sync_sequence(table_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed PostgreSQL from datasets/prod JSON files")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=get_settings().dataset_dir,
        help="Path to dataset directory containing JSON files",
    )
    parser.add_argument(
        "--skip-create-tables",
        action="store_true",
        help="Skip Base.metadata.create_all before seeding",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_dir = args.dataset_dir.resolve()
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {dataset_dir}")

    if not args.skip_create_tables:
        Base.metadata.create_all(bind=engine)

    seed_dataset(dataset_dir)
    print(f"Seed completed from {dataset_dir}")


if __name__ == "__main__":
    main()
