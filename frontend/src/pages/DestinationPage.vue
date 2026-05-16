<template>
  <div class="destination-page space-y-6">
    <section class="card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">目的地浏览</p>
          <h2 class="text-2xl font-bold text-slate-950 mt-1">目的地推荐</h2>
          <p class="text-sm text-slate-500 mt-2 leading-7 max-w-3xl">
            按城市、类别和排序快速筛选，先确定值得去的地点，再继续进入导航、收藏或行程规划。
          </p>
        </div>
        <button v-ripple class="btn-soft-primary text-sm" @click="load(true)">
          {{ loading ? "正在刷新..." : "刷新推荐" }}
        </button>
      </div>

      <div class="destination-filter-bar mt-5">
        <select v-model="cityFilter" class="soft-control text-sm text-slate-700">
          <option value="全部">全部城市</option>
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>
        <select v-model="categoryFilter" class="soft-control text-sm text-slate-700">
          <option value="全部">全部类别</option>
          <option value="scenic">景点</option>
          <option value="shopping">商场 / 商圈</option>
          <option value="campus">高校 / 校园</option>
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

    <div v-if="error" class="alert-soft-error">{{ error }}</div>
    <div v-else-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <SkeletonCard v-for="n in 6" :key="n" />
    </div>
    <EmptyState
      v-else-if="filteredDestinations.length === 0"
      title="暂无匹配结果"
      description="当前筛选条件下没有匹配的目的地，换个城市、类别或排序方式再试试。"
      action-hint="试试切回全部城市或景点类别。"
    />

    <div v-else class="grid xl:grid-cols-[minmax(0,1.28fr)_360px] gap-6 items-start">
      <section class="card-elevated rounded-[24px] p-5 lg:p-6">
        <div class="flex items-start justify-between gap-4 flex-wrap mb-5">
          <div>
            <span class="route-panel-kicker">结果列表</span>
            <h3 class="text-lg font-bold text-slate-950 mt-1">
              共 {{ filteredDestinations.length }} 个候选目的地
            </h3>
            <p class="text-sm text-slate-500 mt-2">
              当前优先展示 {{ cityFilter === "全部" ? "全部城市" : cityFilter }} 的内容，方便直接选择并查看详情。
            </p>
          </div>
          <span class="route-summary-chip">
            {{ sortMode === "recommended" ? "推荐优先" : sortMode === "rating" ? "评分降序" : "热度降序" }}
          </span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
          <article
            v-for="item in filteredDestinations"
            :key="item.source_id"
            v-tilt
            class="destination-card"
            :class="{ 'destination-card-active': selected?.source_id === item.source_id }"
            @click="select(item)"
          >
            <div class="destination-card-media">
              <RealImage
                :src="item.image_url"
                :alt="item.name"
                :name="item.name"
                :city="item.city"
                :latitude="item.latitude"
                :longitude="item.longitude"
                :source-url="item.source_url"
                class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
            </div>
            <div class="p-4">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="text-base font-bold text-slate-900 truncate">{{ item.name }}</h3>
                  <p class="text-sm text-slate-500 mt-1">
                    {{ categoryLabel(item.category) }} · {{ item.city }}
                  </p>
                </div>
                <span class="destination-card-badge">
                  {{ item.category === "campus" ? "校园" : item.category === "shopping" ? "商圈" : "景点" }}
                </span>
              </div>
              <p class="text-sm text-slate-400 mt-2 truncate">
                {{ item.district || item.address }}
              </p>
              <div class="flex flex-wrap gap-2 mt-3">
                <span class="home-score-pill">评分 {{ displayMetric(item.rating) }}</span>
                <span class="home-heat-pill">热度 {{ displayMetric(item.heat) }}</span>
              </div>
              <RouterLink
                class="destination-detail-link"
                :to="destinationDetailPath(item.source_id)"
                @click.stop
              >
                查看工作台详情
              </RouterLink>
            </div>
          </article>
        </div>
      </section>

      <aside class="space-y-5">
        <section
          v-if="selected"
          class="card-elevated rounded-[24px] p-5 sticky top-18 self-start space-y-4 destination-detail-card"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <span class="route-panel-kicker">当前详情</span>
              <h3 class="text-xl font-bold text-slate-950 mt-1">{{ selected.name }}</h3>
            </div>
            <span class="route-summary-chip route-summary-chip-accent">
              {{ categoryLabel(selected.category) }}
            </span>
          </div>

          <RealImage
            :src="selected.image_url"
            :alt="selected.name"
            :name="selected.name"
            :city="selected.city"
            :latitude="selected.latitude"
            :longitude="selected.longitude"
            :source-url="selected.source_url"
            class="w-full h-60 object-cover rounded-[20px] bg-slate-100"
          />

          <div class="space-y-3">
            <p class="text-sm text-slate-500">
              {{ selected.city }} · {{ selected.district || "热门区域" }}
            </p>
            <p class="text-sm text-slate-500">{{ selected.address }}</p>
            <p class="text-sm text-slate-600 leading-7">
              {{ selected.description }}
            </p>
          </div>

          <div class="flex flex-wrap gap-2">
            <span class="route-summary-chip">评分 {{ displayMetric(selected.rating) }}</span>
            <span class="route-summary-chip">热度 {{ displayMetric(selected.heat) }}</span>
            <span class="route-summary-chip">{{ selected.heat_metric || "平台热度" }}</span>
          </div>

          <button
            class="w-full text-sm"
            :class="
              isFavorite(selected.source_id)
                ? 'btn-soft-secondary text-primary-700 bg-primary-50'
                : 'btn-soft-primary'
            "
            v-ripple
            @click="toggleFavorite(selected.source_id)"
          >
            {{ isFavorite(selected.source_id) ? "已收藏，点击取消" : "收藏目的地" }}
          </button>

          <RouterLink
            class="btn-soft-secondary w-full text-sm text-center"
            :to="destinationDetailPath(selected.source_id)"
          >
            打开详情工作台
          </RouterLink>

          <div class="text-xs text-slate-400 leading-6">
            <p class="m-0">
              数据来源：
              <a
                :href="selected.source_url"
                target="_blank"
                rel="noreferrer"
                class="text-primary-600 hover:underline"
              >
                {{ selected.source_name }}
              </a>
            </p>
            <p class="m-0">
              图片来源：{{ selected.image_source_name || "Wikipedia / OpenStreetMap" }}
            </p>
          </div>
        </section>

        <section v-else class="card-elevated rounded-[24px] p-5 space-y-3">
          <span class="route-panel-kicker">详情面板</span>
          <h3 class="text-lg font-bold text-slate-950">先从左侧选择一个目的地</h3>
          <p class="text-sm text-slate-500 leading-7">
            这里会集中展示当前地点的图片、位置、描述和收藏动作，方便继续进入路线或行程。
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
import { useAuthStore } from "../stores/auth";
import { useToastStore } from "../stores/toast";
import { useTravelStore } from "../stores/travel";
import type { Destination } from "../types/models";

const store = useTravelStore();
const auth = useAuthStore();
const toast = useToastStore();

const cityFilter = ref("全部");
const categoryFilter = ref("全部");
const sortMode = ref("recommended");

const destinations = computed(() => store.destinations.items);
const selected = computed(() => store.destinations.selected);
const loading = computed(() => store.destinations.loading);
const error = computed(() => store.destinations.error);
const lastUpdated = computed(() => store.destinations.lastUpdated);

const cities = computed(() => [
  ...new Set(destinations.value.map((item) => item.city).filter(Boolean)),
]);

const displayMetric = (value: number | null | undefined) => value ?? "待补充";

const categoryLabel = (value: string) => {
  if (value === "shopping") return "商场 / 商圈";
  if (value === "campus") return "高校 / 校园";
  return "景点";
};

const filteredDestinations = computed(() => {
  const items = destinations.value.filter((item) => {
    const cityMatch = cityFilter.value === "全部" || item.city === cityFilter.value;
    const categoryMatch =
      categoryFilter.value === "全部" || item.category === categoryFilter.value;
    return cityMatch && categoryMatch;
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
  if (!filteredDestinations.value.length) {
    store.selectDestination(null);
    return;
  }

  if (
    !selected.value ||
    !filteredDestinations.value.some((item) => item.source_id === selected.value?.source_id)
  ) {
    store.selectDestination(filteredDestinations.value[0]);
  }
};

const select = (item: Destination) => store.selectDestination(item);
const load = (force = false) => store.loadFeaturedDestinations(force);
const isFavorite = (sourceId: string) => auth.user?.favorite_destination_ids?.includes(sourceId);
const destinationDetailPath = (sourceId: string) => `/destinations/${encodeURIComponent(sourceId)}`;

const toggleFavorite = async (sourceId: string) => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }

  const alreadyFavorite = Boolean(isFavorite(sourceId));
  await auth.toggleDestinationFavorite(sourceId);
  toast.success(alreadyFavorite ? "已取消收藏" : "已添加到收藏");
};

const removeTag = (key: string) => {
  if (key === "city") cityFilter.value = "全部";
  if (key === "category") categoryFilter.value = "全部";
  if (key === "sort") sortMode.value = "recommended";
};

const selectedTags = computed<Array<{ key: string; label: string }>>(() => {
  const tags: Array<{ key: string; label: string }> = [];

  if (cityFilter.value !== "全部") {
    tags.push({ key: "city", label: `城市：${cityFilter.value}` });
  }

  if (categoryFilter.value !== "全部") {
    tags.push({ key: "category", label: `类别：${categoryFilter.value}` });
  }

  if (sortMode.value !== "recommended") {
    tags.push({
      key: "sort",
      label: sortMode.value === "rating" ? "评分降序" : "热度降序",
    });
  }

  return tags;
});

watch([filteredDestinations, selected], ensureSelection, { immediate: false });

onMounted(async () => {
  await load(false);
  ensureSelection();
});
</script>

<style scoped>
.destination-detail-link {
  display: inline-flex;
  margin-top: 0.85rem;
  color: #1475c4;
  font-size: 0.82rem;
  font-weight: 800;
}

.destination-detail-link:hover {
  color: #0f5f9f;
  text-decoration: underline;
}
</style>
