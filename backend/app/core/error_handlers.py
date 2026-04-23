from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AuthenticationError, BusinessError, ConflictError, NotFoundError

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    @app.exception_handler(BusinessError)
    async def handle_business_error(_request: Request, exc: BusinessError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(NotFoundError)
    async def handle_not_found_error(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(AuthenticationError)
    async def handle_authentication_error(_request: Request, exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(ConflictError)
    async def handle_conflict_error(_request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(ValueError)
    async def handle_value_error(_request: Request, exc: ValueError) -> JSONResponse:
        logger.warning("Unhandled ValueError: %s", str(exc))
        return JSONResponse(status_code=400, content={"detail": str(exc), "code": "VALIDATION_ERROR"})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unexpected error: %s", str(exc))
        return JSONResponse(
            status_code=500, content={"detail": "服务器内部错误，请稍后重试。", "code": "INTERNAL_ERROR"}
        )
