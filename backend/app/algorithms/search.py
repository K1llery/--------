from __future__ import annotations

from collections import defaultdict

"""
搜索引擎算法模块。提供了多键哈希索引、前缀树（Trie树）索引以及倒排索引（Inverted Index）实现，支持快速文本检索。
"""


class HashIndex:
    """多键哈希索引类，用于根据单个唯一字段（如 ID 或编号）进行O(1)复杂度的快速查找。"""
    def __init__(self) -> None:
        self._data: dict[str, dict] = {}

    def build(self, items: list[dict], key_field: str) -> None:
        """
        构建哈希索引。
        
        :param items: 需要索引的数据字典列表
        :param key_field: 作为主键的字段名称
        """
        self._data = {str(item[key_field]).lower(): item for item in items}

    def get(self, key: str) -> dict | None:
        """
        获取指定键对应的数据记录。
        
        :param key: 查找的键值
        :return: 数据字典，如果未找到则返回 None
        """
        return self._data.get(key.lower())


class TrieNode:
    """前缀树节点类。存储子节点以及经过此路径的项目 ID 集合。"""
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.item_ids: set[str] = set()
        self.is_end = False


class TrieIndex:
    """前缀树索引类。用于高效的前缀匹配检索。"""
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str, item_id: str) -> None:
        """
        向前缀树中插入一个词语及其对应的项目 ID。
        
        :param word: 需要插入的词语或短语
        :param item_id: 关联的项目 ID
        """
        node = self.root
        for ch in word.lower():
            node = node.children.setdefault(ch, TrieNode())
            node.item_ids.add(item_id)
        node.is_end = True

    def prefix_search(self, prefix: str) -> set[str]:
        """
        根据前缀搜索所有匹配的项目 ID。
        
        :param prefix: 搜索前缀串
        :return: 包含该前缀的项目 ID 集合
        """
        node = self.root
        for ch in prefix.lower():
            if ch not in node.children:
                return set()
            node = node.children[ch]
        return node.item_ids.copy()


class InvertedIndex:
    """倒排索引类。通过分词建立关键字到项目 ID 的映射，支持多关键字检索。"""
    def __init__(self) -> None:
        self._index: dict[str, set[str]] = defaultdict(set)

    def build(self, items: list[dict], fields: list[str], id_field: str) -> None:
        """
        基于提供的字段构建倒排索引。
        
        :param items: 数据记录列表
        :param fields: 需要提取关键词建立索引的字段列表
        :param id_field: 作为返回结果标识的主键字段
        """
        for item in items:
            item_id = str(item[id_field])
            for field in fields:
                for token in self.tokenize(str(item.get(field, ""))):
                    self._index[token].add(item_id)

    def search(self, keywords: list[str]) -> set[str]:
        """
        使用关键字列表检索相关项目，取关键词对应结果的交集。
        
        :param keywords: 搜索关键词列表
        :return: 满足所有关键词检索条件的项目 ID 集合
        """
        if not keywords:
            return set()
        tokens = [token for keyword in keywords for token in self.tokenize(keyword)]
        if not tokens:
            return set()
        result = self._index.get(tokens[0], set()).copy()
        for token in tokens[1:]:
            result &= self._index.get(token, set())
        return result

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """
        对文本进行基础的分词操作，转换为低写并过滤特定标点。
        
        :param text: 输入文本
        :return: 词汇列表
        """
        return [token for token in text.lower().replace(",", " ").replace("，", " ").split() if token]
