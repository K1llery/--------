"""
AI 服务模块 (AI Service)

提供基于大型语言模型（如阿里云大语言模型及生图模型）的业务封装服务。
主要用于辅助生成旅游日记草稿以及依据用户输入的内容生成配图。
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Protocol
from uuid import uuid4

import httpx

from app.core.exceptions import BusinessError


class ModelClient(Protocol):
    """
    大模型客户端协议接口 (Protocol)。
    定义了底层的生文(create_diary_draft)与生图(create_image_url)必须要实现的方法。
    """
    def create_diary_draft(self, *, destination_name: str, keywords: list[str], style: str) -> dict: ...

    def create_image_url(self, *, prompt: str) -> str: ...


class BailianModelClient:
    """
    阿里云百炼模型具体实现类。
    
    封装 HTTP 请求直接调用百炼提供的大语言及多模态API。
    负责请求的构建、参数填充、异常捕获到自定义 BusinessError 的转换。
    """
    def __init__(
        self,
        *,
        api_key: str,
        text_base_url: str,
        image_base_url: str,
        text_model: str,
        image_model: str,
        timeout_seconds: float,
    ) -> None:
        self.api_key = api_key
        self.text_base_url = text_base_url.rstrip("/")
        self.image_base_url = image_base_url.rstrip("/")
        self.text_model = text_model
        self.image_model = image_model
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise BusinessError("未配置 DASHSCOPE_API_KEY，无法调用阿里云百炼模型。", code="AI_NOT_CONFIGURED")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _json_from_text(text: str) -> dict:
        try:
            loaded = json.loads(text)
            return loaded if isinstance(loaded, dict) else {}
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.S)
            if not match:
                return {}
            try:
                loaded = json.loads(match.group(0))
                return loaded if isinstance(loaded, dict) else {}
            except json.JSONDecodeError:
                return {}

    def create_diary_draft(self, *, destination_name: str, keywords: list[str], style: str) -> dict:
        """
        基于用户给出的目的名称与关键词等生成匹配当前要求的旅游日记。
        """
        prompt = (
            "你是旅游日记助手。请只返回 JSON，字段为 title 和 content。"
            f"目的地：{destination_name}。关键词：{'、'.join(keywords) or '城市漫游'}。"
            f"风格：{style}。正文 180 到 260 字，语气真实，包含路线体验和建议。"
        )
        payload = {
            "model": self.text_model,
            "messages": [
                {"role": "system", "content": "你擅长为游客生成中文旅游日记草稿。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }
        try:
            response = httpx.post(
                f"{self.text_base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise BusinessError(f"日记大模型调用失败：{exc}", code="AI_TEXT_FAILED") from exc

        draft = self._json_from_text(str(content))
        return {
            "title": str(draft.get("title") or f"{destination_name}游记"),
            "content": str(draft.get("content") or content),
        }

    def create_image_url(self, *, prompt: str) -> str:
        """
        发起大模型图文转化任务，获取一张生成后给定的最终结果图下载地址。
        """
        payload = {
            "model": self.image_model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}],
                    }
                ]
            },
            "parameters": {"size": "1K", "n": 1, "watermark": False, "thinking_mode": False},
        }
        try:
            response = httpx.post(
                f"{self.image_base_url}/services/aigc/multimodal-generation/generation",
                headers=self._headers(),
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            content = data["output"]["choices"][0]["message"]["content"]
            for item in content:
                image_url = item.get("image") or item.get("url") or item.get("image_url")
                if image_url:
                    return str(image_url)
            raise ValueError("response does not contain image URL")
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise BusinessError(f"生图大模型调用失败：{exc}", code="AI_IMAGE_FAILED") from exc


def download_binary(url: str) -> bytes:
    """
    网络辅助图片下载器抽取函数。
    读取外部生图的URL转换成本地二进制流用于落盘持久化。
    """
    try:
        response = httpx.get(url, timeout=60.0)
        response.raise_for_status()
        return response.content
    except httpx.HTTPError as exc:
        raise BusinessError(f"生成图片下载失败：{exc}", code="AI_IMAGE_DOWNLOAD_FAILED") from exc


class AIService:
    """
    综合高级AI服务执行调度门面(Facade)。
    依赖底层大模型抽象操作完成“草稿日记生成”与“封面配图附带落盘”等高阶功能。
    """
    def __init__(
        self,
        *,
        model_client: ModelClient,
        generated_media_dir: Path,
        generated_media_url_prefix: str,
        image_downloader: Callable[[str], bytes] = download_binary,
    ) -> None:
        """
        初始化 AI 调度服务参数如资源盘路径和依赖请求库。
        """
        self.model_client = model_client
        self.generated_media_dir = generated_media_dir
        self.generated_media_url_prefix = generated_media_url_prefix.rstrip("/")
        self.image_downloader = image_downloader

    def draft_diary(self, *, destination_name: str, keywords: list[str], style: str) -> dict:
        """
        调用模型实现代理生成游记草稿的正文内容和合适标题。
        """
        draft = self.model_client.create_diary_draft(
            destination_name=destination_name,
            keywords=keywords,
            style=style,
        )
        return {
            "title": str(draft.get("title") or f"{destination_name}游记"),
            "content": str(draft.get("content") or ""),
        }

    def generate_image(self, *, destination_name: str, title: str, content: str) -> dict:
        """
        构造图像生成 prompt 并请求模型端生成结果图地址，完成后落地缓存至本地 storage。
        返回在本地系统的可用公网访问标识(URL)与原始Prompt等属性。
        """
        prompt = (
            "中文旅游日记封面图，真实摄影质感，适合网页展示。"
            f"目的地：{destination_name}。标题：{title}。内容摘要：{content[:120]}。"
            "画面避免文字、水印和夸张卡通风格。"
        )
        source_url = self.model_client.create_image_url(prompt=prompt)
        if not source_url:
            raise BusinessError("生图模型未返回图片地址。", code="AI_IMAGE_EMPTY")
        image_bytes = self.image_downloader(source_url)
        self.generated_media_dir.mkdir(parents=True, exist_ok=True)
        filename = f"ai-{uuid4().hex}.png"
        output_path = self.generated_media_dir / filename
        output_path.write_bytes(image_bytes)
        return {
            "image_url": f"{self.generated_media_url_prefix}/{filename}",
            "source_url": source_url,
            "prompt": prompt,
        }
