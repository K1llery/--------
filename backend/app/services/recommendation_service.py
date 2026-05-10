"""
推荐服务模块 (Recommendation Service)

提供个性化和热度推荐相关的业务逻辑，用于为用户推荐目的地、特色景点及美食等。
主要包含基于评分、热度和兴趣标签的混合推荐打分计算功能，并结合 TopK选择器优化列表返回。
"""
from __future__ import annotations

from app.algorithms.topk import TopKSelector
from app.repositories.data_loader import DatasetRepository


class RecommendationService:
    """
    提供各种类型地点推荐和美食推荐的服务层类。
    
    依赖于底层的 DatasetRepository 获取原始数据对象，通过 TopKSelector 
    在 O(N) 级别的时间复杂度内取出前 K 个推荐目标，避免全局排序。
    """
    def __init__(self, repository: DatasetRepository) -> None:
        """
        初始化推荐服务。
        
        Args:
            repository (DatasetRepository): 用于访问底层数据集的仓库实例。
        """
        self.repository = repository

    @staticmethod
    def _score(item: dict, interest_tags: list[str]) -> float:
        """
        核心打分算法。
        
        根据地点的评分(rating)和热度(heat)进行加权，
        如果目标地点的标签(tags)包含在用户的兴趣标签内，则给予额外的奖励分。
        
        Args:
            item (dict): 推荐的候选项实体字典。
            interest_tags (list[str]): 用户倾向或感兴趣的标签列表。
            
        Returns:
            float: 该项的总分值。
        """
        rating = float(item.get("rating") or 0.0)
        heat = float(item.get("heat") or 0.0)
        tags = set(item.get("tags", []))
        interest_bonus = len(tags & set(interest_tags)) * 8
        return rating * 15 + heat * 0.1 + interest_bonus

    def recommend_destinations(self, top_k: int, category: str | None, interest_tags: list[str]) -> list[dict]:
        """
        获取一般的目的地推荐列表。
        
        利用 _score 方法及用户兴趣标签进行打分，并使用 TopKSelector 提取出前 top_k 个目的地。
        如果提到了特定类别，则会在候选列表中先筛选特定大类的目的地。

        Args:
            top_k (int): 期望返回的最大推荐项数量。
            category (str | None): 类别过滤器，如果为 None，则对所有的目的地有效。
            interest_tags (list[str]): 当前用户的兴趣倾向，用于增加目标权重。
            
        Returns:
            list[dict]: 被推荐的目的地字典构成的列表列表。
        """
        destinations = self.repository.destinations()
        if category:
            destinations = [item for item in destinations if item["category"] == category]
        selector = TopKSelector(lambda item: self._score(item, interest_tags))
        return selector.select(destinations, top_k)

    def featured_destinations(self, top_k: int | None = None) -> list[dict]:
        """
        获取系统的特色目的地(精选景点)。
        
        从库中检索特色标记项目，如果没有设定 top_k 的限制即全部返回。
        如果指定了数量，则依据目的地的自带属性和打分逻辑进行截断选TopK。
        
        Args:
            top_k (int | None, optional): 选取的最大数量。缺省时返回所有精选。
            
        Returns:
            list[dict]: 特色推荐目的地列表。
        """
        featured = self.repository.featured_destinations()
        if top_k is None:
            return featured
        selector = TopKSelector(lambda item: self._score(item, item.get("tags", [])))
        return selector.select(featured, top_k)

    def recommend_foods(self, top_k: int | None, cuisine: str | None = None) -> list[dict]:
        """
        美食推荐逻辑获取。
        
        依据指定的菜系及其评分热度，找到最合适的美食点返回给前端展示。
        这里未采用用户强关联打分，而是主要按照综合表现(星级x10 + 热度)排序。
        
        Args:
            top_k (int | None): 推荐结果最大条数，如果不限制可使用 None。
            cuisine (str | None, optional): 指定的风味类型，若指定则仅在同菜系中检索。
            
        Returns:
            list[dict]: 美食地点字典所组成的列表。
        """
        foods = self.repository.foods()
        if cuisine:
            foods = [item for item in foods if item["cuisine"] == cuisine]
        if top_k is None:
            return foods
        selector = TopKSelector(lambda item: float(item.get("rating") or 0.0) * 10 + float(item.get("heat") or 0.0))
        return selector.select(foods, top_k)
