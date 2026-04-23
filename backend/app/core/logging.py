from __future__ import annotations

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """配置项目日志格式与级别。"""
    level = logging.DEBUG if debug else logging.INFO
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # 避免重复添加 handler
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # 降低第三方库日志级别
    for noisy_logger in ("uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
