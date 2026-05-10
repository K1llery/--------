"""
游客日记与交流管理服务模块 (Diary Service)

集合了游记系统的检索查询(倒排索引)、数据存取与压缩解压(霍夫曼树)、
以及通过规则引擎抽取或生成故事板(AIGC storyboard)的能力等核心业务实现。
"""
from __future__ import annotations

import re
from datetime import datetime

from app.algorithms.compression import HuffmanCodec
from app.algorithms.search import InvertedIndex
from app.algorithms.topk import TopKSelector
from app.repositories.data_loader import DatasetRepository


class DiarySearchService:
    """
    负责本地游记模糊检索与全文查询的业务服务层。
    依靠 InvertedIndex 倒排搜索进行加速返回。
    """
    def __init__(self, repository: DatasetRepository) -> None:
        """初始化结构变量及索引缓存状态"""
        self.repository = repository
        self.inverted = InvertedIndex()
        self._built = False
        self._items_by_id: dict[int, dict] = {}
        self._items_by_id_str: dict[str, dict] = {}

    def _rebuild_index(self, diaries: list[dict]) -> None:
        """
        每次发生核心数据变动时（或第一次加载），把游记的所有标题和内容
        灌入树形索引实现词库打散和建立倒排链。
        """
        self.inverted = InvertedIndex()
        self.inverted.build(diaries, ["title", "content", "destination_name"], "id")
        self._items_by_id = {int(item["id"]): item for item in diaries}
        self._items_by_id_str = {str(item_id): item for item_id, item in self._items_by_id.items()}
        self._built = True

    def _ensure_index(self) -> None:
        """确保在搜索以前词汇倒排索图建立完善"""
        if self._built:
            return
        self._rebuild_index(self.repository.diaries())

    def list_all(self) -> list[dict]:
        """返回无条件全部系统内原始日记列表(已倒序等基础展示)"""
        return self.repository.diaries()

    def search(self, query: str) -> list[dict]:
        """
        根据给出的分词片段或查询指令进行搜索。
        优先利用 O(1) + O(K) 的倒排索引命中集；如果倒排漏检了，退回暴力包含匹配。
        """
        self._ensure_index()
        ids = self.inverted.search([query])
        matched = [self._items_by_id_str[item_id] for item_id in ids if item_id in self._items_by_id_str]
        if matched:
            return matched
        normalized = query.strip().lower()
        return [
            item
            for item in self._items_by_id.values()
            if normalized in item["title"].lower()
            or normalized in item["content"].lower()
            or normalized in item["destination_name"].lower()
        ]

    def recommend(self, top_k: int = 10) -> list[dict]:
        """依据系统内访问量和已有评分推荐出最为热门优秀的前 K 篇日记。"""
        selector = TopKSelector(lambda item: item["views"] + item["rating"] * 10)
        return selector.select(self.repository.diaries(), top_k)

    def get_by_id(self, diary_id: int) -> dict | None:
        """凭借指定的整型ID获取唯一的日记详细对象。"""
        self._ensure_index()
        return self._items_by_id.get(diary_id)

    def create(self, user: dict, payload: dict) -> dict:
        """
        创建一个全新的用户日记（草稿发布），并自动保存与维护倒排缓存过期。
        """
        diaries = self.repository.diaries()
        diary = {
            "id": max((item["id"] for item in diaries), default=0) + 1,
            "title": payload["title"],
            "destination_name": payload["destination_name"],
            "content": payload["content"],
            "views": 0,
            "rating": 4.5,
            "media_urls": payload.get("media_urls")
            or ([payload["cover_image_url"]] if payload.get("cover_image_url") else []),
            "author_id": user["id"],
            "author_name": user["display_name"],
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        diaries.append(diary)
        self.repository.save_diaries(diaries)
        self._built = False
        return diary

    def increment_view(self, diary_id: int) -> dict | None:
        """
        自增指定日记的浏览次数（热度增长），并持久化重置相应缓存。
        """
        diaries = self.repository.diaries()
        for item in diaries:
            if int(item["id"]) != diary_id:
                continue
            item["views"] = int(item.get("views") or 0) + 1
            self.repository.save_diaries(diaries)
            self._built = False
            return item
        return None

    def rate(self, diary_id: int, user: dict, score: float) -> dict | None:
        """
        接收并处理针对某一游记的用户评分。
        计算包含历史评分和新增评分的均值，更新至主表。
        """
        diary = next((item for item in diaries if int(item["id"]) == diary_id), None)
        if diary is None:
            return None

        ratings = self.repository.diary_ratings()
        existing = next(
            (
                item
                for item in ratings
                if int(item.get("diary_id") or -1) == diary_id and int(item.get("user_id") or -1) == int(user["id"])
            ),
            None,
        )
        if existing is None:
            ratings.append(
                {
                    "id": max((int(item.get("id") or 0) for item in ratings), default=0) + 1,
                    "diary_id": diary_id,
                    "user_id": int(user["id"]),
                    "score": float(score),
                    "updated_at": datetime.now().isoformat(timespec="seconds"),
                }
            )
        else:
            existing["score"] = float(score)
            existing["updated_at"] = datetime.now().isoformat(timespec="seconds")

        diary_scores = [
            float(item.get("score") or 0.0) for item in ratings if int(item.get("diary_id") or -1) == diary_id
        ]
        if diary_scores:
            diary["rating"] = round(sum(diary_scores) / len(diary_scores), 2)

        self.repository.save_diary_ratings(ratings)
        self.repository.save_diaries(diaries)
        self._built = False

        return {
            "diary": diary,
            "user_score": float(score),
            "rating_count": len(diary_scores),
        }


class CompressionService:
    """
    提供面向游记/博客级纯文本的字符无损压缩与解压缩服务。
    使用自定义的霍夫曼(HuffmanCodec)实现实现以字节为单位的最佳前缀编码节省后端保存游记所须储存层开销。
    """
    def __init__(self) -> None:
        """初始化一个无状态基于即时字典映射生成的信源编码引擎实例"""
        self.codec = HuffmanCodec()

    def compress(self, content: str) -> dict:
        """
        接收长段文本内容进行哈夫曼压缩。返回被压缩过后的比特01字符串、字典表及效率等元资料。
        """
        encoded, codes = self.codec.encode(content)
        original_bits = len(content.encode("utf-8")) * 8
        compressed_bits = len(encoded)
        ratio = (compressed_bits / original_bits) if original_bits else 0.0
        return {
            "encoded": encoded,
            "codes": codes,
            "original_bits": original_bits,
            "compressed_bits": compressed_bits,
            "compression_ratio": round(ratio, 4),
        }

    def decompress(self, encoded: str, codes: dict[str, str]) -> str:
        """反向执行霍夫曼解压得出原始的中英文字符串内容"""
        return self.codec.decode(encoded, codes)


class DiaryAIGCService:
    """
    负责进行针对性分析将单薄图文游记按电影分镜（AIGC Storyboard）进行编排展示的服务体系。
    """
    transitions = ("fade", "pan-left", "zoom-in", "wipe", "dolly")
    keyword_candidates = (
        "校园",
        "景区",
        "路线",
        "日落",
        "湖",
        "古建筑",
        "博物馆",
        "图书馆",
        "咖啡",
        "夜景",
        "花园",
        "广场",
    )

    @staticmethod
    def _split_sentences(content: str) -> list[str]:
        """通过分析常规中文句号和标点利用正则强行分割句子"""
        parts = [item.strip() for item in re.split(r"[。！？!?\n]+", content) if item.strip()]
        return parts or ["本次旅程记录暂未包含完整文本，系统按标题生成镜头草稿。"]

    @classmethod
    def _extract_keywords(cls, text: str, limit: int = 6) -> list[str]:
        """
        穷举+字典筛除模式（简易 NLP 抽取代替繁重的 TF-IDF等机制）。
        过滤掉常用停留停用词("可以", "非常"等)，留下富有实际场景描述的字词组成精修提示信息。
        """
        matched = [item for item in cls.keyword_candidates if item in text]
        if len(matched) >= limit:
            return matched[:limit]

        tokens = re.findall(r"[A-Za-z0-9\u4e00-\u9fff]{2,}", text)
        stopwords = {"我们", "这里", "可以", "一个", "这个", "非常", "然后", "今天", "感觉", "旅行", "游览", "拍照"}
        for token in tokens:
            if token in stopwords or token in matched:
                continue
            matched.append(token)
            if len(matched) >= limit:
                break
        return matched[:limit] if matched else ["旅行", "城市漫游"]

    def generate_animation(self, diary: dict, max_shots: int = 6) -> dict:
        """
        基于原日记对象执行虚拟拍摄解析(Storyboard 分镜引擎)。
        
        模拟通过分屏展示的方式把整篇日记划分为特定数目的“镜头”(Shot)，
        推导出各自配音讲解文本与假想转场样式特效提示指令以及每个片段维持的秒数，最后打包成AIGC剧本结构体返回。
        
        Args:
            diary (dict): 系统获取的日记原属字典。
            max_shots (int, optional): 制作分镜数量最大截断。
            
        Returns:
            dict: 囊括了脚本描述、时长列表、分镜头词汇列表元素的媒体大合集字典。
        """
        title = diary.get("title") or "旅程回放"
        destination = diary.get("destination_name") or "目的地"
        content = diary.get("content") or title
        media_urls = diary.get("media_urls") or []

        sentences = self._split_sentences(content)
        shot_count = min(max(len(sentences), 3), max_shots)
        keywords = self._extract_keywords(f"{title} {destination} {content}")

        shots: list[dict] = []
        cursor = 0
        for index in range(shot_count):
            caption = sentences[index % len(sentences)]
            transition = self.transitions[index % len(self.transitions)]
            duration_seconds = max(2, min(6, round(len(caption) / 12)))
            media_url = media_urls[index % len(media_urls)] if media_urls else ""
            visual_prompt = (
                f"目的地:{destination}; 镜头:{transition}; 画面重点:{caption}; 关键词:{'、'.join(keywords[:4])}"
            )
            narration = f"第{index + 1}镜，{caption}"

            shots.append(
                {
                    "index": index + 1,
                    "caption": caption,
                    "media_url": media_url,
                    "transition": transition,
                    "duration_seconds": duration_seconds,
                    "start_second": cursor,
                    "visual_prompt": visual_prompt,
                    "narration": narration,
                }
            )
            cursor += duration_seconds

        narration_script = " ".join(shot["narration"] for shot in shots)
        return {
            "diary_id": int(diary.get("id") or 0),
            "title": title,
            "destination_name": destination,
            "generation_mode": "aigc-storyboard-v1",
            "keywords": keywords,
            "total_duration_seconds": cursor,
            "narration_script": narration_script,
            "shots": shots,
        }
