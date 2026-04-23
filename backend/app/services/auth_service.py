from __future__ import annotations

import hashlib
import secrets
from datetime import datetime

from app.repositories.data_loader import DatasetRepository


class AuthService:
    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository

    @staticmethod
    def _now() -> str:
        return datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def _hash_password(password: str, salt: str | None = None) -> str:
        safe_salt = salt or secrets.token_hex(8)
        digest = hashlib.sha256(f"{safe_salt}:{password}".encode("utf-8")).hexdigest()
        return f"{safe_salt}${digest}"

    @classmethod
    def verify_password(cls, password: str, password_hash: str | None) -> bool:
        if not password_hash:
            return password == "demo123"
        salt, _, _ = password_hash.partition("$")
        return cls._hash_password(password, salt) == password_hash

    @staticmethod
    def _public_user(user: dict) -> dict:
        return {
            "id": user["id"],
            "username": user["username"],
            "display_name": user.get("display_name") or user["username"],
            "created_at": user.get("created_at"),
            "last_login_at": user.get("last_login_at"),
            "favorite_destination_ids": user.get("favorite_destination_ids", []),
            "favorite_route_snapshots": user.get("favorite_route_snapshots", []),
        }

    @classmethod
    def _normalize_user(cls, user: dict) -> dict:
        normalized = {**user}
        normalized["display_name"] = normalized.get("display_name") or normalized.get("username", "旅行者")
        normalized["created_at"] = normalized.get("created_at") or cls._now()
        normalized["favorite_destination_ids"] = normalized.get("favorite_destination_ids", [])
        normalized["favorite_route_snapshots"] = normalized.get("favorite_route_snapshots", [])
        if "password_hash" not in normalized:
            normalized["password_hash"] = cls._hash_password("demo123", f"demo-salt-{normalized['id']}")
        return normalized

    def _load_users(self) -> list[dict]:
        return [self._normalize_user(item) for item in self.repository.users()]

    def _save_users(self, users: list[dict]) -> None:
        self.repository.save_users(users)

    def _load_sessions(self) -> list[dict]:
        return self.repository.sessions()

    def _save_sessions(self, sessions: list[dict]) -> None:
        self.repository.save_sessions(sessions)

    def _create_session(self, user_id: int) -> str:
        sessions = [item for item in self._load_sessions() if item["user_id"] != user_id]
        token = f"local-{secrets.token_hex(16)}"
        sessions.append({"token": token, "user_id": user_id, "created_at": self._now()})
        self._save_sessions(sessions)
        return token

    def _get_user_record(self, username: str) -> dict | None:
        for user in self._load_users():
            if user["username"] == username:
                return user
        return None

    def login(self, username: str, password: str) -> tuple[dict, str] | None:
        users = self._load_users()
        for user in users:
            if user["username"] != username:
                continue
            if not self.verify_password(password, user.get("password_hash")):
                return None
            user["last_login_at"] = self._now()
            self._save_users(users)
            return self._public_user(user), self._create_session(user["id"])
        return None

    def register(self, username: str, password: str, display_name: str | None = None) -> tuple[dict, str]:
        users = self._load_users()
        if any(item["username"] == username for item in users):
            raise ValueError("用户名已存在")
        user = {
            "id": max((item["id"] for item in users), default=0) + 1,
            "username": username,
            "display_name": display_name or username,
            "created_at": self._now(),
            "last_login_at": self._now(),
            "password_hash": self._hash_password(password),
            "favorite_destination_ids": [],
            "favorite_route_snapshots": [],
        }
        users.append(user)
        self._save_users(users)
        return self._public_user(user), self._create_session(user["id"])

    def current_user(self, token: str | None) -> dict | None:
        if not token:
            return None
        sessions = {item["token"]: item["user_id"] for item in self._load_sessions()}
        user_id = sessions.get(token)
        if user_id is None:
            return None
        for user in self._load_users():
            if user["id"] == user_id:
                return self._public_user(user)
        return None

    def logout(self, token: str | None) -> None:
        if not token:
            return
        self._save_sessions([item for item in self._load_sessions() if item["token"] != token])

    def toggle_destination_favorite(self, token: str, source_id: str) -> dict:
        sessions = {item["token"]: item["user_id"] for item in self._load_sessions()}
        user_id = sessions.get(token)
        users = self._load_users()
        for user in users:
            if user["id"] != user_id:
                continue
            favorites = list(user.get("favorite_destination_ids", []))
            if source_id in favorites:
                favorites.remove(source_id)
                favorited = False
            else:
                favorites.append(source_id)
                favorited = True
            user["favorite_destination_ids"] = favorites
            self._save_users(users)
            return {"favorited": favorited, "user": self._public_user(user)}
        raise ValueError("用户不存在")

    def save_route_favorite(self, token: str, snapshot: dict) -> dict:
        sessions = {item["token"]: item["user_id"] for item in self._load_sessions()}
        user_id = sessions.get(token)
        users = self._load_users()
        for user in users:
            if user["id"] != user_id:
                continue
            routes = list(user.get("favorite_route_snapshots", []))
            dedupe_key = (snapshot.get("scene_name"), tuple(snapshot.get("path_codes", [])), snapshot.get("strategy"))
            if not any(
                (item.get("scene_name"), tuple(item.get("path_codes", [])), item.get("strategy")) == dedupe_key
                for item in routes
            ):
                routes.append({**snapshot, "saved_at": self._now()})
            user["favorite_route_snapshots"] = routes
            self._save_users(users)
            return self._public_user(user)
        raise ValueError("用户不存在")

    def demo_accounts(self) -> list[dict]:
        return [self._public_user(item) for item in self._load_users()]
