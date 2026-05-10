"""
用户身份与权限认证服务模块 (Auth Service)

提供基于本地存储的简单会话(Session)机制。
实现了加盐 Hash 密码保护、注册分离、基于Token的用户登入控制功能。
同时附带了针对用户个人的收藏夹与旅游线路收藏的状态保持操作。
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.data_loader import DatasetRepository


class AuthService:
    """
    负责维护用户认证与身份核心的服务层对象。
    处理密码核验、Session会话记录的持久化调度以及部分用户档案更新操作。
    """
    def __init__(self, repository: DatasetRepository) -> None:
        """
        初始化认证系统实例。
        
        Args:
            repository (DatasetRepository): 用于落盘 session与用户数据的底层驱动器。
        """
        self.repository = repository

    @staticmethod
    def _now() -> str:
        """助手函数，快速返回标准结构(ISO8601等)的当前时间文本。"""
        return datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def _hash_password(password: str, salt: str | None = None) -> str:
        """
        核心数据摘要算法：使用 SHA-256 和随机特征盐保护密码。
        
        Args:
            password (str): 原始密码明文。
            salt (str | None, optional): 加密盐，若为空将随机重新产生并附加保存。
            
        Returns:
            str: 格式形如 "被采用的盐$校验Hash值" 的加密密码串。
        """
        safe_salt = salt or secrets.token_hex(8)
        digest = hashlib.sha256(f"{safe_salt}:{password}".encode("utf-8")).hexdigest()
        return f"{safe_salt}${digest}"

    @classmethod
    def verify_password(cls, password: str, password_hash: str | None) -> bool:
        """
        对比传递上来的明文密码是否符合持久化留存的哈希校验值。
        特殊设定：为了课程 Demo 的体验，没有哈希且密码为 demo123 则放行。
        """
        if not password_hash:
            return password == "demo123"
        salt, _, _ = password_hash.partition("$")
        return cls._hash_password(password, salt) == password_hash

    @staticmethod
    def _public_user(user: dict) -> dict:
        """将内部隐秘字段如哈希剥离，抽取为前端可用、安全的公网传播对象。"""
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
        """补充残缺老数据。初始化丢失项并对缺失密码的做后门回退保护(填充加盐)。"""
        normalized = {**user}
        normalized["display_name"] = normalized.get("display_name") or normalized.get("username", "旅行者")
        normalized["created_at"] = normalized.get("created_at") or cls._now()
        normalized["favorite_destination_ids"] = normalized.get("favorite_destination_ids", [])
        normalized["favorite_route_snapshots"] = normalized.get("favorite_route_snapshots", [])
        if "password_hash" not in normalized:
            normalized["password_hash"] = cls._hash_password("demo123", f"demo-salt-{normalized['id']}")
        return normalized

    def _load_users(self) -> list[dict]:
        """抓取并规范化所有的账户列表。"""
        return [self._normalize_user(item) for item in self.repository.users()]

    def _save_users(self, users: list[dict]) -> None:
        """向Repository下发同步用户的指令"""
        self.repository.save_users(users)

    def _load_sessions(self) -> list[dict]:
        """查询在期缓存存活 Session 对象集合"""
        return self.repository.sessions()

    def _save_sessions(self, sessions: list[dict]) -> None:
        """持久化当前所有的鉴权会话数组"""
        self.repository.save_sessions(sessions)

    def _create_session(self, user_id: int) -> str:
        """
        分配构建新 Session 并作多点登录互顶处理（单点剔除其他重合会话）。
        """
        sessions = [item for item in self._load_sessions() if item["user_id"] != user_id]
        token = f"local-{secrets.token_hex(16)}"
        sessions.append({"token": token, "user_id": user_id, "created_at": self._now()})
        self._save_sessions(sessions)
        return token

    def _get_user_record(self, username: str) -> dict | None:
        """内部调用，通过准确名字抽取该用户。"""
        for user in self._load_users():
            if user["username"] == username:
                return user
        return None

    def login(self, username: str, password: str) -> tuple[dict, str] | None:
        """
        核心账户登录功能。验证提供的密码以返回合规的展示态账户以及长期或当期 Token。
        """
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
        """
        注册与添加人员行为，查验其账号是否产生唯一性冲突，然后写入集合。
        """
        users = self._load_users()
        if any(item["username"] == username for item in users):
            raise ConflictError("用户名已存在")
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
        """
        利用 Token 从会话列表倒查用户ID，提取完整干净的上下文人员状态档。
        """
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
        """
        登出会话功能。通过过滤列表的方式废弃剔除现有凭证完成注销状态清理。
        """
        if not token:
            return
        self._save_sessions([item for item in self._load_sessions() if item["token"] != token])

    def toggle_destination_favorite(self, token: str, source_id: str) -> dict:
        """
        目的地收藏操作的拨动开关（在收藏与取消间二相震荡切换）。
        """
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
        raise NotFoundError("用户不存在")

    def save_route_favorite(self, token: str, snapshot: dict) -> dict:
        """
        附加规划好或修改后的线路快照于该账户之下，充作系统历史存档功能。
        通过比对多重标识防止频繁无效去重入库。
        """
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
        raise NotFoundError("用户不存在")

    def demo_accounts(self) -> list[dict]:
        """为方便纯前端演示读取返回全部合规屏蔽状态的虚假测用人员表。"""
        return [self._public_user(item) for item in self._load_users()]
