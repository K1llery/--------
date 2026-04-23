from __future__ import annotations


class BusinessError(Exception):
    """业务逻辑错误，返回 400。"""

    def __init__(self, message: str, code: str = "BUSINESS_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(Exception):
    """资源不存在，返回 404。"""

    def __init__(self, message: str = "资源不存在", code: str = "NOT_FOUND") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class AuthenticationError(Exception):
    """认证失败，返回 401。"""

    def __init__(self, message: str = "请先登录", code: str = "UNAUTHORIZED") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class ConflictError(Exception):
    """资源冲突，返回 409。"""

    def __init__(self, message: str, code: str = "CONFLICT") -> None:
        self.message = message
        self.code = code
        super().__init__(message)
