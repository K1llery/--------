"""
搜索服务模块 (Search Service)

封装底层的哈希索引(HashIndex)、字典树(TrieIndex)与倒排索引(InvertedIndex)，
为系统提供全局统一搜索入口。包括精准匹配和模糊检索（组合查找前缀及关键字）等。
"""
from __future__ import annotations

from app.algorithms.search import HashIndex, InvertedIndex, TrieIndex
from app.repositories.data_loader import DatasetRepository


class SearchService:
    """
    业务级搜索服务类。
    
    懒加载相关索引，在第一次遇到请求时构建数据源。支持多字段倒排以及名字字典树的查询。
    实现了对海量地点的快速检索以提升后端系统的并发表现。
    """
    def __init__(self, repository: DatasetRepository) -> None:
        """
        初始化搜索组件及其实例化的各种搜索树结构。
        
        Args:
            repository (DatasetRepository): 提供地点信息的数据提取器。
        """
        self.repository = repository
        self.hash_index = HashIndex()
        self.trie = TrieIndex()
        self.inverted = InvertedIndex()
        self._built = False
        self._items_by_source_id: dict[str, dict] = {}
        self._all_items: list[dict] = []

    def _ensure_index(self) -> None:
        """
        惰性初始化方法，确保底层索引已经被成功建立。
        
        抓取数据集目的地之后，依次加载到字典树中(供前缀匹配)，以及倒排索引中(匹配包含关键字的字段)，
        并存入散列表以提供高效率精确匹配。
        """
        if self._built:
            return
        items = self.repository.destinations()
        self._all_items = items
        self._items_by_source_id = {str(item["source_id"]): item for item in items}
        
        # 将name加入散列索引实现常数时间准确查找
        self.hash_index.build(items, "name")
        # 为name区、描述区生成关键字的倒排索引
        self.inverted.build(items, ["name", "district", "description"], "source_id")
        # 将名称逐字载入字典树进行前缀补全推荐
        for item in items:
            self.trie.insert(item["name"], item["source_id"])
        self._built = True

    def exact_search(self, query: str) -> dict | None:
        """
        按指定名字进行精确查询。
        
        Args:
            query (str): 请求精确匹配的目标名称。
            
        Returns:
            dict | None: 解析返回命中条件的完整地点对象，如果不存在则为 None。
        """
        self._ensure_index()
        return self.hash_index.get(query)

    def fuzzy_search(self, query: str, keywords: list[str], category: str | None = None) -> list[dict]:
        """
        模糊与倒排索引融合的搜寻，组合前缀和关键字查询。
        
        利用 TrieIndex 实现的前缀逻辑匹配以及 InvertedIndex 做的关键词倒排，
        返回综合打分高的交集(或并集)。优先使用交集匹配度。
        
        Args:
            query (str): 基于输入框给出的前缀词。
            keywords (list[str]): 根据分词解析后给出的关键词列表。
            category (str | None, optional): 一级大类过滤，若给定其值，仅返回对应数据。
            
        Returns:
            list[dict]: 匹配搜索对象数组，依按照热度和评分进行了反向排序展示。
        """
        self._ensure_index()
        # 前缀命中集合
        prefix_matches = self.trie.prefix_search(query) if query else set()
        # 倒排词根命中集合
        keyword_matches = self.inverted.search(keywords) if keywords else set()
        
        # 取结果集
        if prefix_matches and keyword_matches:
            # 严格模式：两方都有结果则取交集
            matched_ids = prefix_matches & keyword_matches
        else:
            # 宽容模式：若任意一方为空则退后处理合并
            matched_ids = prefix_matches or keyword_matches
            
        # 短查询容错补救，防止查不到东西
        if not matched_ids and query:
            matched_ids = self.trie.prefix_search(query[:2])

        results = [self._items_by_source_id[item_id] for item_id in matched_ids if item_id in self._items_by_source_id]
        
        # 分类后置筛选
        if category:
            results = [item for item in results if item["category"] == category]
            
        # 根据系统内涵设定的热度和评分实现多维度默认排序输出
        return sorted(
            results,
            key=lambda item: (float(item.get("heat") or 0.0), float(item.get("rating") or 0.0)),
            reverse=True,
        )
