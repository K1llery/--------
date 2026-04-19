from __future__ import annotations

from app.algorithms.search import HashIndex, InvertedIndex, TrieIndex
from app.repositories.data_loader import DatasetRepository


class SearchService:
    def __init__(self, repository: DatasetRepository) -> None:
        self.repository = repository
        self.hash_index = HashIndex()
        self.trie = TrieIndex()
        self.inverted = InvertedIndex()
        self._built = False
        self._items_by_source_id: dict[str, dict] = {}
        self._all_items: list[dict] = []

    def _ensure_index(self) -> None:
        if self._built:
            return
        items = self.repository.destinations()
        self._all_items = items
        self._items_by_source_id = {str(item["source_id"]): item for item in items}
        self.hash_index.build(items, "name")
        self.inverted.build(items, ["name", "district", "description"], "source_id")
        for item in items:
            self.trie.insert(item["name"], item["source_id"])
        self._built = True

    def exact_search(self, query: str) -> dict | None:
        self._ensure_index()
        return self.hash_index.get(query)

    def fuzzy_search(self, query: str, keywords: list[str], category: str | None = None) -> list[dict]:
        self._ensure_index()
        prefix_matches = self.trie.prefix_search(query) if query else set()
        keyword_matches = self.inverted.search(keywords) if keywords else set()
        if prefix_matches and keyword_matches:
            matched_ids = prefix_matches & keyword_matches
        else:
            matched_ids = prefix_matches or keyword_matches
        if not matched_ids and query:
            matched_ids = self.trie.prefix_search(query[:2])

        results = [self._items_by_source_id[item_id] for item_id in matched_ids if item_id in self._items_by_source_id]
        if category:
            results = [item for item in results if item["category"] == category]
        return sorted(
            results,
            key=lambda item: (float(item.get("heat") or 0.0), float(item.get("rating") or 0.0)),
            reverse=True,
        )
