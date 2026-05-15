import type { Food } from "../types/models";

export type FoodSortMode = "recommend" | "rating" | "heat" | "distance";

const MAX_REASON_COUNT = 3;

const isFiniteNumber = (value: unknown): value is number =>
  typeof value === "number" && Number.isFinite(value);

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

const safeNumber = (value: number | null | undefined, fallback = 0) =>
  isFiniteNumber(value) ? value : fallback;

const safeFood = (food: Food | null | undefined): Partial<Food> => food ?? {};

const collectStringParts = (...values: unknown[]): string[] => {
  const parts: string[] = [];

  for (const value of values) {
    if (Array.isArray(value)) {
      parts.push(...collectStringParts(...value));
    } else if (typeof value === "string" || typeof value === "number") {
      const text = String(value).trim();
      if (text) parts.push(text);
    }
  }

  return parts;
};

const isSubsequence = (query: string, target: string) => {
  if (!query) return true;

  let queryIndex = 0;
  for (const char of target) {
    if (char === query[queryIndex]) queryIndex += 1;
    if (queryIndex === query.length) return true;
  }

  return false;
};

const compareNumberDesc = (left: number, right: number) => right - left;

const getComparableDistance = (food: Food) => getFoodDistanceKm(food) ?? Number.POSITIVE_INFINITY;

export function normalizeText(input: unknown): string {
  if (input == null) return "";
  return String(input).toLowerCase().replace(/\s+/g, "");
}

export function getFoodSearchText(food: Food): string {
  const item = safeFood(food);

  return collectStringParts(
    item.name,
    item.city,
    item.cuisine,
    item.description,
    item.address,
    item.destination_name,
    item.restaurant_name,
    item.canteen_name,
    item.window_name,
    item.venue_type,
    item.dishes,
    item.aliases,
    item.tags,
    item.rank_reasons,
  ).join(" ");
}

export function matchesFoodKeyword(food: Food, keyword: string): boolean {
  const query = normalizeText(keyword);
  if (!query) return true;

  const searchText = normalizeText(getFoodSearchText(food));
  return searchText.includes(query) || isSubsequence(query, searchText);
}

export function getFoodDistanceKm(food: Food): number | null {
  const item = safeFood(food);

  if (isFiniteNumber(item.distance_km) && item.distance_km >= 0) {
    return item.distance_km;
  }

  if (isFiniteNumber(item.distance_m) && item.distance_m >= 0) {
    return item.distance_m / 1000;
  }

  return null;
}

export function getRecommendScore(food: Food): number {
  const item = safeFood(food);
  const ratingScore = clamp(safeNumber(item.rating) / 5, 0, 1);
  const heatScore = clamp(Math.log1p(Math.max(0, safeNumber(item.heat))) / Math.log1p(10000), 0, 1);
  const distanceKm = getFoodDistanceKm(item as Food);
  const distanceScore = distanceKm == null ? 0.35 : clamp(1 - distanceKm / 10, 0, 1);
  const explicitScore = isFiniteNumber(item.recommend_score)
    ? clamp(item.recommend_score / 100, 0, 1)
    : 0;

  return ratingScore * 45 + heatScore * 25 + distanceScore * 20 + explicitScore * 10;
}

export function compareFoods(a: Food, b: Food, sort: FoodSortMode): number {
  const left = safeFood(a);
  const right = safeFood(b);

  if (sort === "rating") {
    return compareNumberDesc(safeNumber(left.rating), safeNumber(right.rating));
  }

  if (sort === "heat") {
    return compareNumberDesc(safeNumber(left.heat), safeNumber(right.heat));
  }

  if (sort === "distance") {
    const distanceDiff = getComparableDistance(left as Food) - getComparableDistance(right as Food);
    if (distanceDiff !== 0) return distanceDiff;
    return compareNumberDesc(getRecommendScore(left as Food), getRecommendScore(right as Food));
  }

  return compareNumberDesc(getRecommendScore(left as Food), getRecommendScore(right as Food));
}

export function selectTopKFoods<T>(items: T[], k: number, scoreFn: (item: T) => number): T[] {
  const limit = Math.floor(k);
  if (limit <= 0 || items.length === 0) return [];

  const heap: Array<{ item: T; score: number; order: number }> = [];

  const isLowerPriority = (
    left: { score: number; order: number },
    right: { score: number; order: number },
  ) => left.score < right.score || (left.score === right.score && left.order > right.order);

  const swap = (leftIndex: number, rightIndex: number) => {
    const current = heap[leftIndex];
    heap[leftIndex] = heap[rightIndex];
    heap[rightIndex] = current;
  };

  const bubbleUp = (index: number) => {
    let current = index;
    while (current > 0) {
      const parent = Math.floor((current - 1) / 2);
      if (!isLowerPriority(heap[current], heap[parent])) break;
      swap(current, parent);
      current = parent;
    }
  };

  const bubbleDown = (index: number) => {
    let current = index;

    while (true) {
      const left = current * 2 + 1;
      const right = left + 1;
      let next = current;

      if (left < heap.length && isLowerPriority(heap[left], heap[next])) next = left;
      if (right < heap.length && isLowerPriority(heap[right], heap[next])) next = right;
      if (next === current) break;

      swap(current, next);
      current = next;
    }
  };

  const push = (entry: { item: T; score: number; order: number }) => {
    heap.push(entry);
    bubbleUp(heap.length - 1);
  };

  const replaceRoot = (entry: { item: T; score: number; order: number }) => {
    heap[0] = entry;
    bubbleDown(0);
  };

  items.forEach((item, order) => {
    const rawScore = scoreFn(item);
    const score = isFiniteNumber(rawScore) ? rawScore : Number.NEGATIVE_INFINITY;
    const entry = { item, score, order };

    if (heap.length < limit) {
      push(entry);
      return;
    }

    if (isLowerPriority(heap[0], entry)) {
      replaceRoot(entry);
    }
  });

  const result: Array<{ item: T; score: number; order: number }> = [];
  while (heap.length > 0) {
    const root = heap[0];
    const last = heap.pop();
    if (root) result.push(root);
    if (heap.length > 0 && last) {
      heap[0] = last;
      bubbleDown(0);
    }
  }

  return result
    .reverse()
    .map((entry) => entry.item);
}

export function buildFoodRankReasons(food: Food): string[] {
  const item = safeFood(food);
  const explicitReasons = collectStringParts(item.rank_reasons).slice(0, MAX_REASON_COUNT);
  if (explicitReasons.length >= MAX_REASON_COUNT) return explicitReasons;

  const reasons = [...explicitReasons];
  const addReason = (reason: string) => {
    if (reasons.length < MAX_REASON_COUNT && !reasons.includes(reason)) reasons.push(reason);
  };

  if (safeNumber(item.rating) >= 4.5) addReason("评分高");
  if (safeNumber(item.heat) >= 80) addReason("热度高");

  const distanceKm = getFoodDistanceKm(item as Food);
  if (distanceKm != null && distanceKm <= 1) addReason("距离近");

  const searchText = normalizeText(getFoodSearchText(food));
  if (searchText.includes("特色") || searchText.includes("本地") || searchText.includes("老字号")) {
    addReason("本地特色");
  }

  if (item.destination_name || searchText.includes("景区") || searchText.includes("景点")) {
    addReason("景点周边");
  }

  if (
    item.venue_type === "canteen" ||
    item.venue_type === "window" ||
    item.canteen_name ||
    item.window_name
  ) {
    addReason(item.venue_type === "window" || item.window_name ? "校园窗口" : "校园食堂");
  }

  if (item.venue_type === "cafe") addReason("咖啡休憩");
  if (item.venue_type === "snack") addReason("小吃补给");

  return reasons.slice(0, MAX_REASON_COUNT);
}
