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
        <button v-ripple class="btn-soft-primary text-sm" @click="load(true)">
          {{ loading ? "正在刷新..." : "刷新推荐" }}
        </button>
      </div>

      <div class="food-filter-bar mt-5">
        <select v-model="cityFilter" class="soft-control text-sm text-slate-700">
          <option value="全部">全部城市</option>
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>
        <select v-model="cuisineFilter" class="soft-control text-sm text-slate-700">
          <option value="全部">全部菜系</option>
          <option v-for="cuisine in cuisines" :key="cuisine" :value="cuisine">
            {{ cuisine }}
          </option>
        </select>
        <select v-model="destinationFilter" class="soft-control text-sm text-slate-700">
          <option value="全部">全部关联目的地</option>
          <option v-for="destination in destinations" :key="destination" :value="destination">
            {{ destination }}
          </option>
        </select>
        <select v-model="sortMode" class="soft-control text-sm text-slate-700">
          <option value="recommended">推荐优先</option>
          <option value="rating">评分降序</option>
          <option value="heat">热度降序</option>
        </select>
        <span v-if="lastUpdated" class="text-xs text-slate-400 self-center">
          最近更新：{{ lastUpdated }}
        </span>
      </div>

      <div v-if="selectedTags.length" class="flex flex-wrap gap-2 mt-4">
        <button v-for="tag in selectedTags" :key="tag.key" class="destination-tag-pill" @click="removeTag(tag.key)">
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

    <div v-if="error" class="alert-soft-error">{{ error }}</div>
    <div v-else-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <SkeletonCard v-for="n in 6" :key="n" />
    </div>
    <EmptyState
      v-else-if="filteredFoods.length === 0"
      title="暂无美食推荐"
      description="当前筛选条件下没有匹配结果，换个城市、菜系或关联目的地再试试看。"
      action-hint="试试切回全部城市，或者先按评分排序。"
    />

    <div v-else class="grid xl:grid-cols-[minmax(0,1.24fr)_360px] gap-6 items-start">
      <section class="card-elevated rounded-[24px] p-5 lg:p-6">
        <div class="flex items-start justify-between gap-4 flex-wrap mb-5">
          <div>
            <span class="route-panel-kicker">推荐列表</span>
            <h3 class="text-lg font-bold text-slate-950 mt-1">共 {{ filteredFoods.length }} 家候选餐饮</h3>
            <p class="text-sm text-slate-500 mt-2">
              当前优先展示
              {{ cityFilter === "全部" ? "全部城市" : cityFilter }}
              的美食内容，方便你直接选中查看详情或补进行程。
            </p>
          </div>
          <span class="route-summary-chip">
            {{
              sortMode === "recommended"
                ? "推荐优先"
                : sortMode === "rating"
                  ? "评分降序"
                  : "热度降序"
            }}
          </span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
          <article
            v-for="item in filteredFoods"
            :key="foodKey(item)"
            v-tilt
            class="food-card"
            :class="{ 'food-card-active': isSelected(item) }"
            @click="select(item)"
          >
            <div class="food-card-media">
              <RealImage
                :src="item.image_url"
                :alt="item.name"
                :name="item.name"
                :search-hint="item.destination_name"
                :city="item.city"
                :latitude="item.latitude"
                :longitude="item.longitude"
                :source-url="item.source_url"
                class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
            </div>
            <div class="p-4 space-y-3">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="text-base font-bold text-slate-900 truncate">{{ item.name }}</h3>
                  <p class="text-sm text-slate-500 mt-1">
                    {{ item.city || "待补充城市" }} · {{ item.cuisine || "特色餐饮" }}
                  </p>
                </div>
                <span class="food-card-badge">{{ item.cuisine || "推荐" }}</span>
              </div>

              <p class="text-sm text-slate-400 truncate">
                {{ item.destination_name || item.address || "适合加入当前城市行程" }}
              </p>

              <div class="flex flex-wrap gap-2">
                <span class="home-score-pill">评分 {{ displayMetric(item.rating) }}</span>
                <span class="home-heat-pill">热度 {{ displayMetric(item.heat) }}</span>
              </div>
            </div>
          </article>
        </div>
      </section>

      <aside class="space-y-5">
        <section
          v-if="selectedFood"
          class="card-elevated rounded-[24px] p-5 sticky top-18 self-start space-y-4 food-detail-card"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <span class="route-panel-kicker">当前详情</span>
              <h3 class="text-xl font-bold text-slate-950 mt-1">{{ selectedFood.name }}</h3>
            </div>
            <span class="route-summary-chip route-summary-chip-accent">
              {{ selectedFood.cuisine || "特色餐饮" }}
            </span>
          </div>

          <RealImage
            :src="selectedFood.image_url"
            :alt="selectedFood.name"
            :name="selectedFood.name"
            :search-hint="selectedFood.destination_name"
            :city="selectedFood.city"
            :latitude="selectedFood.latitude"
            :longitude="selectedFood.longitude"
            :source-url="selectedFood.source_url"
            class="w-full h-60 object-cover rounded-[20px] bg-slate-100"
          />

          <div class="space-y-3">
            <p class="text-sm text-slate-500">
              {{ selectedFood.city || "城市待补充" }} · {{ selectedFood.cuisine || "特色餐饮" }}
            </p>
            <p class="text-sm text-slate-500">
              {{ selectedFood.address || selectedFood.destination_name || "适合加入当前城市行程" }}
            </p>
            <p class="text-sm text-slate-600 leading-7">
              {{
                selectedFood.description ||
                "这条推荐可作为城市探索或景点游览后的餐饮补充，适合直接纳入行程规划。"
              }}
            </p>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="route-metric-tile">
              <strong>{{ displayMetric(selectedFood.rating) }}</strong>
              <span>综合评分</span>
            </div>
            <div class="route-metric-tile">
              <strong>{{ displayMetric(selectedFood.heat) }}</strong>
              <span>平台热度</span>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <span class="route-summary-chip">{{ selectedFood.destination_name || "城市推荐美食" }}</span>
            <span v-if="selectedFood.distance_km != null" class="route-summary-chip">
              距离 {{ selectedFood.distance_km }} km
            </span>
          </div>

          <div class="text-xs text-slate-400 leading-6">
            <p class="m-0">
              数据来源：
              <a
                v-if="selectedFood.source_url"
                :href="selectedFood.source_url"
                target="_blank"
                rel="noreferrer"
                class="text-primary-600 hover:underline"
              >
                {{ selectedFood.source_name || "来源页面" }}
              </a>
              <span v-else>{{ selectedFood.source_name || "平台数据" }}</span>
            </p>
            <p class="m-0">
              图片来源：{{ selectedFood.image_source_name || "Wikipedia / OpenStreetMap" }}
            </p>
          </div>
        </section>

        <section v-else class="card-elevated rounded-[24px] p-5 space-y-3">
          <span class="route-panel-kicker">详情面板</span>
          <h3 class="text-lg font-bold text-slate-950">先从左侧选择一家美食</h3>
          <p class="text-sm text-slate-500 leading-7">
            这里会集中展示当前餐饮的图片、位置、关联目的地和评分热度，方便继续决定是否加入行程。
          </p>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import EmptyState from "../components/EmptyState.vue";
import RealImage from "../components/RealImage.vue";
import SkeletonCard from "../components/SkeletonCard.vue";
import { useTravelStore } from "../stores/travel";
import type { Food } from "../types/models";

type FoodRecommendation = Food & {
  source_id?: string;
  destination_name?: string;
  source_url?: string;
  image_source_name?: string;
};

const store = useTravelStore();

const foods = computed<FoodRecommendation[]>(() => store.foods.items as FoodRecommendation[]);
const selectedFood = computed<FoodRecommendation | null>(
  () => (store.foods.selected as FoodRecommendation | null) ?? null,
);
const loading = computed(() => store.foods.loading);
const error = computed(() => store.foods.error);
const lastUpdated = computed(() => store.foods.lastUpdated);

const cityFilter = ref("全部");
const cuisineFilter = ref("全部");
const destinationFilter = ref("全部");
const sortMode = ref<"recommended" | "rating" | "heat">("recommended");

const cities = computed(() => [...new Set(foods.value.map((item) => item.city).filter(Boolean))]);
const cuisines = computed(() => [
  ...new Set(foods.value.map((item) => item.cuisine).filter(Boolean)),
]);
const destinations = computed(() => [
  ...new Set(foods.value.map((item) => item.destination_name).filter(Boolean)),
]);

const displayMetric = (value: number | null | undefined) => value ?? "待补充";

const foodKey = (item: FoodRecommendation) => item.source_id || item.id || item.name;

const filteredFoods = computed(() => {
  const items = foods.value.filter((item) => {
    const cityMatch = cityFilter.value === "全部" || item.city === cityFilter.value;
    const cuisineMatch = cuisineFilter.value === "全部" || item.cuisine === cuisineFilter.value;
    const destinationMatch =
      destinationFilter.value === "全部" || item.destination_name === destinationFilter.value;

    return cityMatch && cuisineMatch && destinationMatch;
  });

  const ranked = [...items];
  if (sortMode.value === "rating") {
    ranked.sort((left, right) => (right.rating ?? 0) - (left.rating ?? 0));
  } else if (sortMode.value === "heat") {
    ranked.sort((left, right) => (right.heat ?? 0) - (left.heat ?? 0));
  }

  return ranked;
});

const ensureSelection = () => {
  if (!filteredFoods.value.length) {
    store.selectFood(null);
    return;
  }

  const currentSelection = selectedFood.value;
  if (
    !currentSelection ||
    !filteredFoods.value.some((item) => foodKey(item) === foodKey(currentSelection))
  ) {
    store.selectFood(filteredFoods.value[0]);
  }
};

const load = (force = false) => store.loadFoods(force);
const select = (item: FoodRecommendation) => store.selectFood(item);
const isSelected = (item: FoodRecommendation) => {
  const currentSelection = selectedFood.value;
  return currentSelection ? foodKey(item) === foodKey(currentSelection) : false;
};

const removeTag = (key: string) => {
  if (key === "city") cityFilter.value = "全部";
  if (key === "cuisine") cuisineFilter.value = "全部";
  if (key === "destination") destinationFilter.value = "全部";
  if (key === "sort") sortMode.value = "recommended";
};

const selectedTags = computed<Array<{ key: string; label: string }>>(() => {
  const tags: Array<{ key: string; label: string }> = [];

  if (cityFilter.value !== "全部") {
    tags.push({ key: "city", label: `城市：${cityFilter.value}` });
  }

  if (cuisineFilter.value !== "全部") {
    tags.push({ key: "cuisine", label: `菜系：${cuisineFilter.value}` });
  }

  if (destinationFilter.value !== "全部") {
    tags.push({ key: "destination", label: `关联目的地：${destinationFilter.value}` });
  }

  if (sortMode.value !== "recommended") {
    tags.push({
      key: "sort",
      label: sortMode.value === "rating" ? "评分降序" : "热度降序",
    });
  }

  return tags;
});

watch([filteredFoods, selectedFood], ensureSelection, { immediate: false });

onMounted(async () => {
  await load(false);
  ensureSelection();
});
</script>
