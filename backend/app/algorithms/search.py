from __future__ import annotations

from collections import defaultdict


class HashIndex:
    def __init__(self) -> None:
        self._data: dict[str, dict] = {}

    def build(self, items: list[dict], key_field: str) -> None:
        self._data = {str(item[key_field]).lower(): item for item in items}

    def get(self, key: str) -> dict | None:
        return self._data.get(key.lower())


class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.item_ids: set[str] = set()
        self.is_end = False


class TrieIndex:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str, item_id: str) -> None:
        node = self.root
        for ch in word.lower():
            node = node.children.setdefault(ch, TrieNode())
            node.item_ids.add(item_id)
        node.is_end = True

    def prefix_search(self, prefix: str) -> set[str]:
        node = self.root
        for ch in prefix.lower():
            if ch not in node.children:
                return set()
            node = node.children[ch]
        return node.item_ids.copy()


class InvertedIndex:
    """Inverted index with CJK-aware tokenization.

    For ASCII text we keep word-level tokens. For CJK runs we generate
    overlapping bigrams (e.g. "故宫博物院" -> ["故宫", "宫博", "博物", "物院"])
    so any 2+ char Chinese query can locate documents without an external
    segmentation library.
    """

    def __init__(self) -> None:
        self._index: dict[str, set[str]] = defaultdict(set)
        # Per-field index, populated by ``build_ranked``; used for weighted scoring.
        self._field_index: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    def build(self, items: list[dict], fields: list[str], id_field: str) -> None:
        for item in items:
            item_id = str(item[id_field])
            for field in fields:
                for token in self.tokenize(str(item.get(field, ""))):
                    self._index[token].add(item_id)

    def build_ranked(
        self,
        items: list[dict],
        field_weights: list[tuple[str, float]],
        id_field: str,
    ) -> None:
        """Index items per-field so ``search_ranked`` can weight matches."""
        self._index = defaultdict(set)
        self._field_index = defaultdict(lambda: defaultdict(set))
        for item in items:
            item_id = str(item[id_field])
            for field, _ in field_weights:
                value = item.get(field)
                if value is None:
                    continue
                for token in self.tokenize(str(value)):
                    self._index[token].add(item_id)
                    self._field_index[field][token].add(item_id)

    def search(self, keywords: list[str]) -> set[str]:
        if not keywords:
            return set()
        tokens = [token for keyword in keywords for token in self.tokenize(keyword)]
        if not tokens:
            return set()
        result = self._index.get(tokens[0], set()).copy()
        for token in tokens[1:]:
            result &= self._index.get(token, set())
        return result

    def search_ranked(
        self,
        keywords: list[str],
        field_weights: list[tuple[str, float]],
    ) -> list[tuple[str, float]]:
        """Return ``(item_id, score)`` pairs sorted by descending relevance."""
        tokens: list[str] = []
        for keyword in keywords:
            tokens.extend(self.tokenize(keyword))
        if not tokens:
            return []
        scores: dict[str, float] = defaultdict(float)
        for field, weight in field_weights:
            field_idx = self._field_index.get(field, {})
            for token in tokens:
                for item_id in field_idx.get(token, set()):
                    scores[item_id] += weight
        return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    @staticmethod
    def tokenize(text: str) -> list[str]:
        normalized = text.lower().replace(",", " ").replace("，", " ")
        tokens: list[str] = []
        for word in normalized.split():
            cjk_buf: list[str] = []
            for ch in word:
                if "一" <= ch <= "鿿":
                    cjk_buf.append(ch)
                else:
                    if cjk_buf:
                        tokens.extend(_cjk_bigrams(cjk_buf))
                        cjk_buf = []
                    if ch.isalnum():
                        tokens.append(ch)
            if cjk_buf:
                tokens.extend(_cjk_bigrams(cjk_buf))
            if word.isascii() and word.isalnum():
                # Keep the whole ASCII word so short queries match exactly.
                tokens.append(word)
        return tokens


def _cjk_bigrams(chars: list[str]) -> list[str]:
    if len(chars) == 1:
        return [chars[0]]
    return [chars[i] + chars[i + 1] for i in range(len(chars) - 1)]
