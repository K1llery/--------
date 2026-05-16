<template>
  <div class="food-page space-y-6">
    <section class="card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">美食推荐</p>
          <h2 class="text-2xl font-bold text-slate-950 mt-1">城市风味与景点周边</h2>
          <p class="text-sm text-slate-500 mt-2 leading-7 max-w-3xl">
            从城市代表性餐馆到景点周边高评分餐饮，先按城市、菜系和关联目的地快速筛选，再决定去哪一家补足行程体验。
          </p>
        </div>
      </div>

      <FoodAnchorSelector
        :active-anchor-name="activeAnchorName"
        :anchor-type="anchorType"
        :anchor-id="anchorId"
        :anchor-options="currentAnchorOptions"
        :radius-km="radiusKm"
        :radius-options="radiusOptions"
        @update:anchor-type="setAnchorType"
        @update:anchor-id="anchorId = $event"
        @update:radius-km="radiusKm = $event"
      />

      <FoodFilterBar
        :city-filter="cityFilter"
        :cuisine-filter="cuisineFilter"
        :sort-mode="sortMode"
        :cities="cities"
        :cuisines="cuisines"
        :last-updated="lastUpdated"
        @update:city-filter="cityFilter = $event"
        @update:cuisine-filter="cuisineFilter = $event"
        @update:sort-mode="sortMode = $event"
      >
        <FoodSearchBar :keyword="keyword" @update:keyword="keyword = $event" />
      </FoodFilterBar>

      <div v-if="selectedTags.length" class="flex flex-wrap gap-2 mt-4">
        <button
          v-for="tag in selectedTags"
          :key="tag.key"
          class="destination-tag-pill"
          @click="removeTag(tag.key)"
        >
          {{ tag.label }}
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </section>

    <div v-if="error" class="alert-soft-error flex items-center justify-between gap-3">
      <span>{{ error }}</span>
      <button class="btn-soft-secondary text-sm shrink-0" @click="load(true)">重新加载</button>
    </div>
    <div v-else-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <SkeletonCard v-for="n in 6" :key="n" />
    </div>
    <FoodEmptyState v-else-if="filteredFoods.length === 0" @clear-filters="clearFilters" />

    <section v-else class="card-elevated rounded-[24px] p-5 lg:p-6">
      <FoodResultList
        :items="displayedFoods"
        :active-anchor-name="activeAnchorName"
        @view-detail="openFoodDetail"
      />

      <div v-if="hasMore" class="flex justify-center mt-6">
        <button class="btn-soft-secondary text-sm" @click="loadMore">再看10家</button>
      </div>
      <p v-else class="text-center text-sm text-slate-400 mt-6">
        已显示全部 {{ filteredFoods.length }} 家
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import SkeletonCard from "../components/SkeletonCard.vue";
import FoodAnchorSelector from "../components/food/FoodAnchorSelector.vue";
import FoodEmptyState from "../components/food/FoodEmptyState.vue";
import FoodFilterBar from "../components/food/FoodFilterBar.vue";
import FoodResultList from "../components/food/FoodResultList.vue";
import FoodSearchBar from "../components/food/FoodSearchBar.vue";
import type { AnchorType, FoodAnchorOption, FoodRecommendation } from "../components/food/types";
import { api } from "../api/client";
import { useTravelStore } from "../stores/travel";
import type { NearbyFoodResponse } from "../types/api";
import { compareFoods, matchesFoodKeyword, type FoodSortMode } from "../utils/foodRecommend";

const store = useTravelStore();
const route = useRoute();
const router = useRouter();

const withFoodRouteId = (item: FoodRecommendation): FoodRecommendation => {
  if (item.id || !item.source_id) return item;
  return { ...item, id: item.source_id };
};

const allFoods = computed<FoodRecommendation[]>(() =>
  (store.foods.items as FoodRecommendation[]).map(withFoodRouteId),
);
const nearbyFoods = ref<FoodRecommendation[]>([]);
const nearbyLoading = ref(false);
const nearbyError = ref("");
const nearbyLastUpdated = ref("");

const PAGE_STEP = 10;
const nearbyTopK = 50;
const radiusOptions = [
  { label: "500m", value: 0.5 },
  { label: "1km", value: 1 },
  { label: "2km", value: 2 },
  { label: "3km", value: 3 },
];

const keyword = ref("");
const cityFilter = ref("全部");
const cuisineFilter = ref("全部");
const destinationFilter = ref("全部");
const anchorType = ref<AnchorType>("destination");
const anchorId = ref("");
const anchorName = ref("");
const anchorLatitude = ref<number | null>(null);
const anchorLongitude = ref<number | null>(null);
const radiusKm = ref(3);
const sortMode = ref<FoodSortMode>("recommend");
const visibleCount = ref(PAGE_STEP);

let isApplyingQuery = false;
let isUpdatingQuery = false;
let keywordQueryTimer: ReturnType<typeof window.setTimeout> | null = null;
let nearbyRequestId = 0;

const foods = computed<FoodRecommendation[]>(() =>
  activeAnchorHasCoordinates.value ? nearbyFoods.value : allFoods.value,
);
const loading = computed(() =>
  activeAnchorHasCoordinates.value ? nearbyLoading.value : store.foods.loading,
);
const error = computed(() =>
  activeAnchorHasCoordinates.value ? nearbyError.value : store.foods.error,
);
const lastUpdated = computed(() =>
  activeAnchorHasCoordinates.value ? nearbyLastUpdated.value : store.foods.lastUpdated,
);

const cities = computed<string[]>(() => [
  ...new Set(foods.value.map((item) => item.city).filter((city): city is string => Boolean(city))),
]);
const cuisines = computed<string[]>(() => {
  const source =
    cityFilter.value === "全部"
      ? foods.value
      : foods.value.filter((item) => item.city === cityFilter.value);
  return [
    ...new Set(
      source.map((item) => item.cuisine).filter((cuisine): cuisine is string => Boolean(cuisine)),
    ),
  ];
});

const destinationAnchors = computed<FoodAnchorOption[]>(() => {
  if (store.destinations.items.length > 0) {
    return store.destinations.items.map((destination) => ({
      id: destination.source_id || `destination:${destination.name}`,
      name: destination.name,
      type: "destination",
      city: destination.city,
      latitude: destination.latitude,
      longitude: destination.longitude,
    }));
  }

  const foodDestinations = [
    ...new Set(
      allFoods.value.flatMap((item) => (item.destination_name ? [item.destination_name] : [])),
    ),
  ];

  return foodDestinations.map((destination) => ({
    id: `destination:${destination}`,
    name: destination,
    type: "destination",
  }));
});

const schoolAnchors = computed<FoodAnchorOption[]>(() => {
  const buptDestination = store.destinations.items.find((destination) =>
    destination.name.includes("北京邮电大学"),
  );

  return [
    {
      id: "bupt",
      name: "北京邮电大学",
      type: "school",
      city: "北京",
      latitude: buptDestination?.latitude,
      longitude: buptDestination?.longitude,
    },
  ];
});

const baseAnchorOptions = computed(() =>
  anchorType.value === "school" ? schoolAnchors.value : destinationAnchors.value,
);

const currentAnchorOptions = computed(() => {
  const options = baseAnchorOptions.value;
  const currentName = anchorName.value.trim();
  const currentId = anchorId.value.trim();

  if (
    currentName &&
    !options.some((anchor) => anchor.id === currentId || anchor.name === currentName)
  ) {
    return [
      {
        id: currentId || `${anchorType.value}:${currentName}`,
        name: currentName,
        type: anchorType.value,
      },
      ...options,
    ];
  }

  return options;
});

const selectedAnchor = computed<FoodAnchorOption | null>(() => {
  if (!anchorId.value && !anchorName.value.trim()) return null;
  const currentName = anchorName.value.trim();
  const applyQueryCoordinates = (anchor: FoodAnchorOption): FoodAnchorOption => ({
    ...anchor,
    latitude:
      typeof anchor.latitude === "number" ? anchor.latitude : (anchorLatitude.value ?? undefined),
    longitude:
      typeof anchor.longitude === "number"
        ? anchor.longitude
        : (anchorLongitude.value ?? undefined),
  });

  const matchedAnchor = currentAnchorOptions.value.find(
    (anchor) => anchor.id === anchorId.value || (currentName && anchor.name === currentName),
  );

  if (matchedAnchor) return applyQueryCoordinates(matchedAnchor);

  return applyQueryCoordinates({
    id: anchorId.value || `${anchorType.value}:${currentName}`,
    name: currentName,
    type: anchorType.value,
  });
});

const activeAnchorName = computed(() => selectedAnchor.value?.name || "");

const activeAnchorHasCoordinates = computed(
  () =>
    typeof selectedAnchor.value?.latitude === "number" &&
    typeof selectedAnchor.value?.longitude === "number",
);

const sortLabel = computed(() => {
  if (sortMode.value === "distance") return "距离最近";
  if (sortMode.value === "rating") return "评分最高";
  if (sortMode.value === "heat") return "热度最高";
  return "推荐优先";
});

const firstQueryValue = (value: unknown) => {
  const current = Array.isArray(value) ? value[0] : value;
  return typeof current === "string" ? current : "";
};

const isFoodSortMode = (value: string): value is FoodSortMode =>
  value === "recommend" || value === "rating" || value === "heat" || value === "distance";

const isAnchorType = (value: string): value is AnchorType =>
  value === "destination" || value === "school";

const readQuerySort = (value: unknown): FoodSortMode => {
  const sort = firstQueryValue(value);
  return isFoodSortMode(sort) ? sort : "recommend";
};

const readQueryAnchorType = (value: unknown): AnchorType => {
  const type = firstQueryValue(value);
  return isAnchorType(type) ? type : "destination";
};

const readQueryRadius = (value: unknown) => {
  const radius = Number(firstQueryValue(value));
  return radiusOptions.some((option) => option.value === radius) ? radius : 3;
};

const readQueryNumber = (value: unknown) => {
  const numberValue = Number(firstQueryValue(value));
  return Number.isFinite(numberValue) ? numberValue : null;
};

const normalizeQueryForCompare = (query: Record<string, unknown>) => {
  const normalized: Record<string, string> = {};
  Object.keys(query)
    .sort()
    .forEach((key) => {
      const value = firstQueryValue(query[key]);
      if (value) normalized[key] = value;
    });
  return JSON.stringify(normalized);
};

const buildFoodRouteQuery = (queryKeyword = keyword.value) => {
  const nextQuery: Record<string, string> = {};
  const currentAnchor = selectedAnchor.value;
  const currentAnchorName = activeAnchorName.value.trim();

  if (cityFilter.value !== "全部") nextQuery.city = cityFilter.value;
  if (cuisineFilter.value !== "全部") nextQuery.cuisine = cuisineFilter.value;
  if (anchorType.value !== "destination" || currentAnchorName) {
    nextQuery.anchorType = anchorType.value;
  }
  if (currentAnchor?.id) nextQuery.anchorId = currentAnchor.id;
  if (currentAnchorName) nextQuery.anchorName = currentAnchorName;
  if (currentAnchorName) nextQuery.radius = String(radiusKm.value);
  if (typeof currentAnchor?.latitude === "number" && typeof currentAnchor.longitude === "number") {
    nextQuery.lat = String(currentAnchor.latitude);
    nextQuery.lng = String(currentAnchor.longitude);
  }
  if (sortMode.value !== "recommend" || currentAnchorName) nextQuery.sort = sortMode.value;
  if (queryKeyword.trim()) nextQuery.q = queryKeyword.trim();

  return nextQuery;
};

const syncRouteQuery = async (queryKeyword = keyword.value) => {
  if (isApplyingQuery) return;

  const nextQuery = buildFoodRouteQuery(queryKeyword);
  if (normalizeQueryForCompare(route.query) === normalizeQueryForCompare(nextQuery)) return;

  isUpdatingQuery = true;
  try {
    await router.replace({ query: nextQuery });
  } finally {
    void nextTick(() => {
      isUpdatingQuery = false;
    });
  }
};

const applyRouteQuery = () => {
  isApplyingQuery = true;
  const legacyDestination = firstQueryValue(route.query.destination);
  const routeAnchorType = readQueryAnchorType(route.query.anchorType);
  const routeAnchorName = firstQueryValue(route.query.anchorName) || legacyDestination;

  keyword.value = firstQueryValue(route.query.q);
  cityFilter.value = firstQueryValue(route.query.city) || "全部";
  cuisineFilter.value = firstQueryValue(route.query.cuisine) || "全部";
  anchorType.value = routeAnchorType;
  anchorName.value = routeAnchorName;
  anchorId.value =
    firstQueryValue(route.query.anchorId) ||
    (routeAnchorName ? `${routeAnchorType}:${routeAnchorName}` : "");
  anchorLatitude.value = readQueryNumber(route.query.lat);
  anchorLongitude.value = readQueryNumber(route.query.lng);
  destinationFilter.value =
    routeAnchorType === "destination" && routeAnchorName ? routeAnchorName : "全部";
  radiusKm.value = readQueryRadius(route.query.radius);
  sortMode.value = readQuerySort(route.query.sort);
  visibleCount.value = PAGE_STEP;

  if (keywordQueryTimer) {
    window.clearTimeout(keywordQueryTimer);
    keywordQueryTimer = null;
  }

  void nextTick(() => {
    isApplyingQuery = false;
  });
};

const anchorMatchesFood = (item: FoodRecommendation) => {
  const anchor = selectedAnchor.value;
  if (!anchor) return true;

  if (anchor.type === "school") {
    return anchor.city ? item.city === anchor.city : true;
  }

  return item.destination_name === anchor.name;
};

const filteredFoods = computed(() => {
  return foods.value.filter((item) => {
    const cityMatch = cityFilter.value === "全部" || item.city === cityFilter.value;
    const cuisineMatch = cuisineFilter.value === "全部" || item.cuisine === cuisineFilter.value;
    const destinationMatch = anchorMatchesFood(item);
    const keywordMatch = matchesFoodKeyword(item, keyword.value);

    return cityMatch && cuisineMatch && destinationMatch && keywordMatch;
  });
});

const sortedFoods = computed(() => {
  const ranked = [...filteredFoods.value];
  ranked.sort((left, right) => compareFoods(left, right, sortMode.value));
  return ranked;
});

const displayedFoods = computed(() => sortedFoods.value.slice(0, visibleCount.value));

const hasMore = computed(() => filteredFoods.value.length > visibleCount.value);

const loadMore = () => {
  visibleCount.value = Math.min(
    visibleCount.value + PAGE_STEP,
    filteredFoods.value.length,
  );
};

const loadNearbyFoods = async () => {
  const anchor = selectedAnchor.value;
  if (typeof anchor?.latitude !== "number" || typeof anchor.longitude !== "number") return;

  const requestId = ++nearbyRequestId;
  nearbyLoading.value = true;
  nearbyError.value = "";

  try {
    const params: Record<string, string | number> = {
      lat: anchor.latitude,
      lng: anchor.longitude,
      radius: radiusKm.value,
      top_k: nearbyTopK,
    };
    if (cuisineFilter.value !== "全部") params.cuisine = cuisineFilter.value;

    const { data } = await api.get<NearbyFoodResponse>("/foods", { params });
    if (requestId !== nearbyRequestId) return;

    nearbyFoods.value = ((data.items ?? []) as FoodRecommendation[]).map(withFoodRouteId);
    nearbyLastUpdated.value = new Date().toLocaleString("zh-CN");
  } catch {
    if (requestId !== nearbyRequestId) return;
    nearbyFoods.value = [];
    nearbyError.value = "附近美食加载失败，请稍后重试。";
  } finally {
    if (requestId === nearbyRequestId) nearbyLoading.value = false;
  }
};

const load = async (force = false) => {
  if (activeAnchorHasCoordinates.value) {
    await loadNearbyFoods();
  } else {
    await store.loadFoods(force);
  }
};

const openFoodDetail = (item: FoodRecommendation) => {
  if (!item.id) {
    console.warn("无法打开美食详情：缺少 food.id", item);
    return;
  }

  void router.push({
    path: `/foods/${encodeURIComponent(item.id)}`,
    query: { returnTo: route.fullPath },
  });
};

const clearFilters = () => {
  keyword.value = "";
  cityFilter.value = "全部";
  cuisineFilter.value = "全部";
  destinationFilter.value = "全部";
  anchorType.value = "destination";
  anchorId.value = "";
  anchorName.value = "";
  anchorLatitude.value = null;
  anchorLongitude.value = null;
  radiusKm.value = 3;
  sortMode.value = "recommend";
  visibleCount.value = PAGE_STEP;

  if (keywordQueryTimer) {
    window.clearTimeout(keywordQueryTimer);
    keywordQueryTimer = null;
  }
  void syncRouteQuery("");
};

const removeTag = (key: string) => {
  if (key === "keyword") keyword.value = "";
  if (key === "anchor" || key === "destination") {
    anchorId.value = "";
    anchorName.value = "";
    anchorLatitude.value = null;
    anchorLongitude.value = null;
    destinationFilter.value = "全部";
  }
  if (key === "city") cityFilter.value = "全部";
  if (key === "cuisine") cuisineFilter.value = "全部";
  if (key === "radius") radiusKm.value = 3;
  if (key === "sort") sortMode.value = "recommend";
};

const setAnchorType = (type: AnchorType) => {
  if (anchorType.value === type) return;
  anchorType.value = type;
  anchorId.value = "";
  anchorName.value = "";
  anchorLatitude.value = null;
  anchorLongitude.value = null;
  destinationFilter.value = "全部";
};

const syncAnchorFromSelection = () => {
  const anchor = currentAnchorOptions.value.find((item) => item.id === anchorId.value);

  if (!anchorId.value) {
    anchorName.value = "";
    anchorLatitude.value = null;
    anchorLongitude.value = null;
    destinationFilter.value = "全部";
    return;
  }

  if (anchor) {
    anchorName.value = anchor.name;
    anchorLatitude.value = typeof anchor.latitude === "number" ? anchor.latitude : null;
    anchorLongitude.value = typeof anchor.longitude === "number" ? anchor.longitude : null;
  }

  destinationFilter.value =
    anchorType.value === "destination" && anchorName.value ? anchorName.value : "全部";
};

const syncAnchorIdFromName = () => {
  const currentName = anchorName.value.trim();
  if (!currentName) return;

  const anchor = currentAnchorOptions.value.find((item) => item.name === currentName);
  if (anchor && anchor.id !== anchorId.value) {
    anchorId.value = anchor.id;
  }
};

const selectedTags = computed<Array<{ key: string; label: string }>>(() => {
  const tags: Array<{ key: string; label: string }> = [];

  if (activeAnchorName.value) {
    tags.push({
      key: "anchor",
      label: `${anchorType.value === "school" ? "学校" : "景点"}：${activeAnchorName.value}`,
    });
    tags.push({
      key: "radius",
      label: `半径：${radiusOptions.find((option) => option.value === radiusKm.value)?.label ?? `${radiusKm.value}km`}`,
    });
  }

  if (keyword.value.trim()) {
    tags.push({ key: "keyword", label: `搜索：${keyword.value.trim()}` });
  }

  if (cityFilter.value !== "全部") {
    tags.push({ key: "city", label: `城市：${cityFilter.value}` });
  }

  if (cuisineFilter.value !== "全部") {
    tags.push({ key: "cuisine", label: `菜系：${cuisineFilter.value}` });
  }

  if (sortMode.value !== "recommend") {
    tags.push({ key: "sort", label: sortLabel.value });
  }

  return tags;
});

watch(
  () => route.query,
  () => {
    if (isUpdatingQuery) return;
    applyRouteQuery();
  },
  { immediate: true },
);

watch(cityFilter, () => {
  if (isApplyingQuery) return;
  if (cuisineFilter.value !== "全部" && !cuisines.value.includes(cuisineFilter.value)) {
    cuisineFilter.value = "全部";
  }
});

watch([cityFilter, cuisineFilter, sortMode, radiusKm], () => {
  if (isApplyingQuery) return;
  visibleCount.value = PAGE_STEP;
  void syncRouteQuery();
});

watch([anchorType, anchorId], () => {
  if (isApplyingQuery) return;
  syncAnchorFromSelection();
  visibleCount.value = PAGE_STEP;
  void syncRouteQuery();
});

watch(currentAnchorOptions, () => {
  syncAnchorIdFromName();
});

watch(
  () => [
    selectedAnchor.value?.id,
    selectedAnchor.value?.latitude,
    selectedAnchor.value?.longitude,
    radiusKm.value,
    cuisineFilter.value,
  ],
  () => {
    void load(false);
  },
);

watch(keyword, () => {
  if (isApplyingQuery) return;
  visibleCount.value = PAGE_STEP;

  if (keywordQueryTimer) window.clearTimeout(keywordQueryTimer);
  keywordQueryTimer = window.setTimeout(() => {
    void syncRouteQuery();
  }, 300);
});

onMounted(async () => {
  await store.loadFeaturedDestinations(false);
  await load(false);
});
</script>

<style>
.food-anchor-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.1), transparent 28%),
    linear-gradient(180deg, rgba(248, 250, 252, 0.98), rgba(255, 255, 255, 0.98));
  border: 1px solid rgba(191, 219, 254, 0.82);
  border-radius: 1.25rem;
}

.food-anchor-controls {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.75rem;
}

.food-anchor-type-group {
  display: inline-flex;
  min-height: 2.75rem;
  overflow: hidden;
  background: #eef6ff;
  border: 1px solid rgba(191, 219, 254, 0.92);
  border-radius: 999px;
  padding: 0.2rem;
}

.food-anchor-type-button {
  display: inline-flex;
  min-width: 4.5rem;
  align-items: center;
  justify-content: center;
  padding: 0 0.85rem;
  color: #475569;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 800;
  transition:
    color 0.18s ease,
    background 0.18s ease,
    box-shadow 0.18s ease;
}

.food-anchor-type-button-active {
  color: #ffffff;
  background: linear-gradient(135deg, #2563eb, #0f766e);
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2);
}

.food-rank-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 4.25rem;
  min-height: 2rem;
  padding: 0 0.75rem;
  color: #ffffff;
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.48);
  border-radius: 999px;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.22);
  font-size: 0.76rem;
  font-weight: 800;
}

.food-rank-badge-premium {
  min-width: 5rem;
  min-height: 2.3rem;
  background: linear-gradient(135deg, #f97316, #dc2626);
  box-shadow: 0 16px 30px rgba(220, 38, 38, 0.3);
  font-size: 0.84rem;
}

.food-card:nth-child(1) .food-rank-badge-premium {
  background: linear-gradient(135deg, #facc15, #f97316);
  color: #1f2937;
}

.food-card:nth-child(2) .food-rank-badge-premium {
  background: linear-gradient(135deg, #e2e8f0, #64748b);
}

.food-card:nth-child(3) .food-rank-badge-premium {
  background: linear-gradient(135deg, #fb923c, #b45309);
}

.food-image-placeholder {
  display: flex;
  width: 100%;
  height: 100%;
  min-height: 10rem;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  color: #64748b;
  background:
    radial-gradient(circle at top left, rgba(249, 115, 22, 0.16), transparent 30%),
    linear-gradient(135deg, #f8fafc 0%, #eef6ff 100%);
  text-align: center;
}

.food-image-placeholder-detail {
  min-height: 15rem;
  border-radius: 1.25rem;
}

.food-image-icon {
  display: inline-flex;
  width: 3.5rem;
  height: 3.5rem;
  align-items: center;
  justify-content: center;
  color: #0f172a;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 999px;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
  font-weight: 900;
}

.food-image-placeholder strong {
  color: #334155;
  font-size: 0.95rem;
}

.food-image-placeholder small {
  color: #94a3b8;
  font-size: 0.75rem;
}

@media (max-width: 768px) {
  .food-anchor-panel {
    align-items: stretch;
    flex-direction: column;
  }

  .food-anchor-controls {
    justify-content: flex-start;
  }
}

.food-card-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}

.food-card-metrics span {
  display: flex;
  min-height: 3.25rem;
  flex-direction: column;
  justify-content: center;
  gap: 0.2rem;
  padding: 0.55rem 0.65rem;
  background: #ffffff;
  border: 1px solid rgba(214, 228, 241, 0.88);
  border-radius: 0.9rem;
}

.food-card-metrics small,
.food-detail-label {
  color: #94a3b8;
  font-size: 0.72rem;
  font-weight: 800;
}

.food-card-metrics strong {
  color: #0f172a;
  font-size: 0.92rem;
}

.food-reason-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.food-dish-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.food-dish-pill {
  display: inline-flex;
  align-items: center;
  min-height: 1.65rem;
  padding: 0 0.62rem;
  color: #7c2d12;
  background: rgba(255, 247, 237, 0.96);
  border: 1px solid rgba(253, 186, 116, 0.52);
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
}

.food-reason-pill {
  display: inline-flex;
  align-items: center;
  min-height: 1.65rem;
  padding: 0 0.62rem;
  color: #0f766e;
  background: rgba(240, 253, 250, 0.96);
  border: 1px solid rgba(94, 234, 212, 0.46);
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
}

.food-card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  padding-top: 0.2rem;
}

.food-action-button {
  display: inline-flex;
  min-height: 2.25rem;
  align-items: center;
  justify-content: center;
  padding: 0 0.85rem;
  color: #334155;
  background: #f8fafc;
  border: 1px solid rgba(203, 213, 225, 0.88);
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
  text-decoration: none;
  transition:
    transform 0.18s ease,
    border-color 0.18s ease,
    background 0.18s ease;
}

.food-action-button:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #ffffff;
  border-color: rgba(59, 130, 246, 0.42);
}

.food-action-button:disabled {
  cursor: not-allowed;
  color: #94a3b8;
  background: #f1f5f9;
}

.food-action-primary {
  color: #ffffff;
  background: linear-gradient(135deg, #2563eb, #0f766e);
  border-color: transparent;
}
</style>
