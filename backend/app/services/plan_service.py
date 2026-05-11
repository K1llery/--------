from datetime import datetime

from app.repositories.data_loader import DatasetRepository


class PlanService:
    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository

    def _now(self) -> str:
        return datetime.now().isoformat(timespec="seconds")

    def _load_plans(self) -> list[dict]:
        return self.repository.plans()

    def _save_plans(self, plans: list[dict]) -> None:
        self.repository.save_plans(plans)

    def list_by_user(self, user_id: int) -> list[dict]:
        return [p for p in self._load_plans() if p.get("user_id") == user_id]

    def get_by_id(self, plan_id: int, user_id: int) -> dict | None:
        plans = self._load_plans()
        return next(
            (p for p in plans if p["id"] == plan_id and p.get("user_id") == user_id),
            None,
        )

    def create(self, user_id: int, payload: dict) -> dict:
        plans = self._load_plans()
        plan_id = max((p["id"] for p in plans), default=0) + 1
        plan = {
            "id": plan_id,
            "user_id": user_id,
            "title": payload["title"],
            "days": payload["days"],
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        plans.append(plan)
        self._save_plans(plans)
        return plan

    def update(self, plan_id: int, user_id: int, payload: dict) -> dict | None:
        plans = self._load_plans()
        for p in plans:
            if p["id"] == plan_id and p.get("user_id") == user_id:
                if "title" in payload and payload["title"] is not None:
                    p["title"] = payload["title"]
                if "days" in payload and payload["days"] is not None:
                    p["days"] = payload["days"]
                p["updated_at"] = self._now()
                self._save_plans(plans)
                return p
        return None

    def delete(self, plan_id: int, user_id: int) -> bool:
        plans = self._load_plans()
        new_plans = [p for p in plans if not (p["id"] == plan_id and p.get("user_id") == user_id)]
        if len(new_plans) == len(plans):
            return False
        self._save_plans(new_plans)
        return True
