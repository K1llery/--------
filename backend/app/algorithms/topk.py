from __future__ import annotations

import heapq
from dataclasses import dataclass
from itertools import count
from typing import Callable, Iterable, Sequence, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class RankedItem:
    item: dict
    score: float


class TopKSelector:
    """Maintain top-k elements without fully sorting the whole sequence."""

    def __init__(self, scorer: Callable[[T], float]) -> None:
        self.scorer = scorer

    def select(self, items: Iterable[T], k: int) -> list[T]:
        if k <= 0:
            return []

        heap: list[tuple[float, int, T]] = []
        serial = count()
        for item in items:
            score = self.scorer(item)
            entry = (score, next(serial), item)
            if len(heap) < k:
                heapq.heappush(heap, entry)
                continue
            if score > heap[0][0]:
                heapq.heapreplace(heap, entry)

        ranked = sorted(heap, key=lambda pair: (pair[0], -pair[1]), reverse=True)
        return [item for _, _, item in ranked]


def quickselect_top_k(items: Sequence[T], k: int, scorer: Callable[[T], float]) -> list[T]:
    if k <= 0:
        return []
    if k >= len(items):
        return sorted(items, key=scorer, reverse=True)

    working = [(scorer(item), item) for item in items]

    def partition(left: int, right: int, pivot_index: int) -> int:
        pivot_score = working[pivot_index][0]
        working[pivot_index], working[right] = working[right], working[pivot_index]
        store_index = left
        for idx in range(left, right):
            if working[idx][0] > pivot_score:
                working[store_index], working[idx] = working[idx], working[store_index]
                store_index += 1
        working[right], working[store_index] = working[store_index], working[right]
        return store_index

    left, right = 0, len(working) - 1
    target = k - 1
    while left <= right:
        pivot_index = (left + right) // 2
        pivot_index = partition(left, right, pivot_index)
        if pivot_index == target:
            break
        if pivot_index < target:
            left = pivot_index + 1
        else:
            right = pivot_index - 1

    return [item for _, item in sorted(working[:k], key=lambda pair: pair[0], reverse=True)]
