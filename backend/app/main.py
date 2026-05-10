"""
主应用程序模块 (Main Application Module)
=========================================
该模块负责初始化 FastAPI 应用程序、配置中间件(CORS)、
注册异常处理器、挂载静态文件目录以及引入 API 路由。

主要流程:
1. 获取系统配置字典和初始化日志。
2. 创建 FastAPI 实例。
3. 配置跨域资源共享 (CORS) 策略。
4. 注册自定义以及全局的错误/异常处理。
5. 注册子路由 (API Router) 并挂载用于 AI 生成图片的静态资源目录。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.error_handlers import register_error_handlers

settings = get_settings()
setup_logging(debug=settings.debug)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    summary="北京高校与景区个性化旅游系统 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(api_router, prefix=settings.api_prefix)
settings.generated_media_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.generated_media_url_prefix,
    StaticFiles(directory=settings.generated_media_dir),
    name="generated-media",
)


@app.get("/")
def root() -> dict[str, str]:
    """
    根路由处理函数。
    
    返回:
        dict: 包含系统 API 运行状态的欢迎信息。
    """
    return {"message": "Personalized Travel System API is running."}
