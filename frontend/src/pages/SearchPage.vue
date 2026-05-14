<template>
  <div class="search-page space-y-6">
    <section class="card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">目的地搜索</p>
          <h2 class="text-2xl font-bold text-slate-950 mt-1">从关键词快速定位目的地</h2>
          <p class="text-sm text-slate-500 mt-2 leading-7 max-w-3xl">
            支持名称搜索、历史记录和联想提示，再结合城市与类别筛选，把景点、高校和商圈快速缩小到可操作范围。
          </p>
        </div>
        <button type="button" v-ripple class="btn-soft-primary text-sm" @click="search">
          {{ loading ? "正在搜索..." : "立即搜索" }}
        </button>
      </div>

      <form class="search-workbench mt-5" @submit.prevent="search">
        <div class="search-input-shell">
          <div class="relative">
            <input
              v-model="query"
              placeholder="搜索景点、高校、商圈或地标名称"
              class="soft-control search-input-control w-full pr-10 text-sm"
              @focus="showDropdown = true"
              @blur="onInputBlur"
              @input="showDropdown = true"
            />
            <button
              v-if="query"
              type="button"
              class="search-input-clear"
              @click="query = ''"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div
            v-if="showDropdown && (historyItems.length || suggestionItems.length)"
            class="search-dropdown"
          >
            <div v-if="historyItems.length" class="px-4 py-3">
              <p class="search-dropdown-kicker">历史记录</p>
              <div class="flex flex-wrap gap-2 mt-2">
                <button
                  v-for="item in historyItems"
                  :key="item"
                  type="button"
                  class="destination-tag-pill"
                  @mousedown.prevent="applyHistory(item)"
                >
                  {{ item }}
                </button>
              </div>
            </div>
            <div
              v-if="suggestionItems.length"
              class="px-4 py-3 border-t border-slate-100"
            >
              <p class="search-dropdown-kicker">关键词联想</p>
              <div class="flex flex-wrap gap-2 mt-2">
                <button
                  v-for="item in suggestionItems"
                  :key="item"
                  type="button"
                  class="search-suggestion-pill"
                  @mousedown.prevent="applySuggestion(item)"
                >
                  {{ item }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="search-filter-row">
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
          <button type="submit" v-ripple class="btn-soft-primary text-sm min-w-[120px]">
            {{ loading ? "搜索中..." : "搜索" }}
          </button>
        </div>
      </form>

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

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <section class="route-insight-card">
        <span class="route-panel-kicker">当前关键词</span>
        <h3>{{ query.trim() || "等待输入" }}</h3>
        <p>搜索结果会优先返回精确匹配，再补充模糊结果和精选推荐，避免空白页。</p>
      </section>
      <section class="route-insight-card">
        <span class="route-panel-kicker">筛选范围</span>
        <h3>{{ cityFilter === "全部" ? "全部城市" : cityFilter }}</h3>
        <p>{{ categoryFilter === "全部" ? "未限制类别，适合先广搜再收窄。" : `当前只看${categoryLabel(categoryFilter)}。` }}</p>
      </section>
      <section class="route-insight-card">
        <span class="route-panel-kicker">结果规模</span>
        <div class="grid grid-cols-2 gap-3 mt-4">
          <div class="route-metric-tile">
            <strong>{{ exactResults.length }}</strong>
            <span>精确匹配</span>
          </div>
          <div class="route-metric-tile">
            <strong>{{ fuzzyResults.length }}</strong>
            <span>相关结果</span>
          </div>
        </div>
      </section>
    </div>

    <div v-if="error" class="alert-soft-error">{{ error }}</div>
    <div v-else-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <SkeletonCard v-for="n in 6" :key="n" />
    </div>
    <EmptyState
      v-else-if="!displayResults.length"
      title="未找到匹配结果"
      description="换一个更短或更常见的关键词，或者切回全部城市、全部类别再试试看。"
      action-hint="例如先搜“大学”“公园”“外滩”这类主关键词。"
    />

    <div v-else class="grid xl:grid-cols-[minmax(0,1.22fr)_360px] gap-6 items-start">
      <div class="space-y-6">
        <section v-if="exactResults.length" class="card-elevated rounded-[24px] p-5 lg:p-6">
          <div class="flex items-start justify-between gap-4 flex-wrap mb-5">
            <div>
              <span class="route-panel-kicker">精确匹配</span>
              <h3 class="text-lg font-bold text-slate-950 mt-1">共 {{ exactResults.length }} 条直接命中</h3>
              <p class="text-sm text-slate-500 mt-2">
                这些结果与当前关键词高度一致，适合作为优先查看对象。
              </p>
            </div>
            <span class="route-summary-chip">优先结果</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
            <article
              v-for="item in exactResults"
              :key="`exact-${item.source_id}`"
              v-tilt
              class="search-card"
              :class="{ 'search-card-active': selected?.source_id === item.source_id }"
              @click="selected = item"
            >
              <div class="search-card-media">
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
              <div class="p-4 space-y-3">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <h3 class="text-base font-bold text-slate-900 truncate">{{ item.name }}</h3>
                    <p class="text-sm text-slate-500 mt-1">
                      {{ categoryLabel(item.category) }} · {{ item.city || "城市待补充" }}
                    </p>
                  </div>
                  <span class="search-card-badge">精确</span>
                </div>

                <p class="text-sm text-slate-400 truncate">
                  {{ item.address || item.district || "可进一步查看详情与位置" }}
                </p>

                <div class="flex flex-wrap gap-2">
                  <span class="home-score-pill">评分 {{ displayMetric(item.rating) }}</span>
                  <span class="home-heat-pill">热度 {{ displayMetric(item.heat) }}</span>
                </div>
              </div>
            </article>
          </div>
        </section>

        <section class="card-elevated rounded-[24px] p-5 lg:p-6">
          <div class="flex items-start justify-between gap-4 flex-wrap mb-5">
            <div>
              <span class="route-panel-kicker">相关结果</span>
              <h3 class="text-lg font-bold text-slate-950 mt-1">共 {{ fuzzyResults.length }} 条延展结果</h3>
              <p class="text-sm text-slate-500 mt-2">
                这里包含模糊搜索与精选补充，适合在没有直接命中时继续收窄目标。
              </p>
            </div>
            <span class="route-summary-chip route-summary-chip-accent">扩展搜索</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
            <article
              v-for="item in fuzzyResults"
              :key="`fuzzy-${item.source_id}`"
              v-tilt
              class="search-card"
              :class="{ 'search-card-active': selected?.source_id === item.source_id }"
              @click="selected = item"
            >
              <div class="search-card-media">
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
              <div class="p-4 space-y-3">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <h3 class="text-base font-bold text-slate-900 truncate">{{ item.name }}</h3>
                    <p class="text-sm text-slate-500 mt-1">
                      {{ categoryLabel(item.category) }} · {{ item.city || "城市待补充" }}
                    </p>
                  </div>
                  <span class="search-card-badge search-card-badge-accent">相关</span>
                </div>

                <p class="text-sm text-slate-400 truncate">
                  {{ item.address || item.district || "可作为联想结果继续比较" }}
                </p>

                <div class="flex flex-wrap gap-2">
                  <span class="home-score-pill">评分 {{ displayMetric(item.rating) }}</span>
                  <span class="home-heat-pill">热度 {{ displayMetric(item.heat) }}</span>
                </div>
              </div>
            </article>
          </div>
        </section>
      </div>

      <aside class="space-y-5">
        <section
          v-if="selected"
          class="card-elevated rounded-[24px] p-5 sticky top-18 self-start space-y-4 search-detail-card"
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
              {{ selected.city || "城市待补充" }} · {{ selected.address || "地址待补充" }}
            </p>
            <p class="text-sm text-slate-600 leading-7">
              {{ selected.description || "这是一个值得进一步进入导航、收藏或加入行程的城市目的地。" }}
            </p>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="route-metric-tile">
              <strong>{{ displayMetric(selected.rating) }}</strong>
              <span>综合评分</span>
            </div>
            <div class="route-metric-tile">
              <strong>{{ displayMetric(selected.heat) }}</strong>
              <span>平台热度</span>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <span class="route-summary-chip">{{ categoryLabel(selected.category) }}</span>
            <span class="route-summary-chip">{{ selected.city || "城市待补充" }}</span>
          </div>

          <div v-if="selected.source_url" class="text-xs text-slate-400 leading-6">
            <p class="m-0">
              数据来源：
              <a
                :href="selected.source_url"
                target="_blank"
                rel="noreferrer"
                class="text-primary-600 hover:underline"
              >
                {{ selected.source_name || "公开来源" }}
              </a>
            </p>
          </div>
        </section>

        <section v-else class="card-elevated rounded-[24px] p-5 space-y-3">
          <span class="route-panel-kicker">详情面板</span>
          <h3 class="text-lg font-bold text-slate-950">先从左侧选择一个结果</h3>
          <p class="text-sm text-slate-500 leading-7">
            这里会集中展示当前搜索结果的图片、位置、类别和描述，方便继续进入路线、收藏或行程。
          </p>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import { api } from "../api/client";
import EmptyState from "../components/EmptyState.vue";
import RealImage from "../components/RealImage.vue";
import SkeletonCard from "../components/SkeletonCard.vue";
import { useTravelStore } from "../stores/travel";
import type { Destination } from "../types/models";
import type { DestinationSearchResponse } from "../types/api";

const store = useTravelStore();

const query = ref("外滩");
const cityFilter = ref("全部");
const categoryFilter = ref("全部");
const loading = ref(false);
const error = ref("");
const exactRaw = ref<Destination[]>([]);
const fuzzyRaw = ref<Destination[]>([]);
const selected = ref<Destination | null>(null);
const showDropdown = ref(false);

const historyKey = "search_history";
const history = ref<string[]>([]);
const cities = ["北京", "上海", "广州", "深圳"];

const allDestinations = computed(() => store.destinations.items as Destination[]);

const historyItems = computed(() => {
  if (!query.value.trim()) return history.value.slice(0, 8);

  const lowered = query.value.toLowerCase();
  return history.value.filter((item) => item.toLowerCase().includes(lowered)).slice(0, 6);
});

const suggestionItems = computed(() => {
  const lowered = query.value.trim().toLowerCase();
  if (!lowered) return [];

  return allDestinations.value
    .filter(
      (item) =>
        item.name.toLowerCase().includes(lowered) ||
        (item.city && item.city.toLowerCase().includes(lowered)),
    )
    .slice(0, 6)
    .map((item) => item.name);
});

const categoryLabel = (value: string) => {
  if (value === "shopping") return "商场 / 商圈";
  if (value === "campus") return "高校 / 校园";
  return "景点";
};

const displayMetric = (value: number | null | undefined) => value ?? "待补充";

const filtered = (items: Destination[]) =>
  items.filter((item) => {
    const cityMatch = cityFilter.value === "全部" || item.city === cityFilter.value;
    const categoryMatch = categoryFilter.value === "全部" || item.category === categoryFilter.value;
    return cityMatch && categoryMatch;
  });

const exactResults = computed(() => filtered(exactRaw.value));
const fuzzyResults = computed(() => filtered(fuzzyRaw.value));
const displayResults = computed(() => [...exactResults.value, ...fuzzyResults.value]);

const selectedTags = computed<Array<{ key: string; label: string }>>(() => {
  const tags: Array<{ key: string; label: string }> = [];

  if (cityFilter.value !== "全部") {
    tags.push({ key: "city", label: `城市：${cityFilter.value}` });
  }

  if (categoryFilter.value !== "全部") {
    tags.push({ key: "category", label: `类别：${categoryLabel(categoryFilter.value)}` });
  }

  return tags;
});

const ensureSelection = () => {
  if (!displayResults.value.length) {
    selected.value = null;
    return;
  }

  if (!selected.value || !displayResults.value.some((item) => item.source_id === selected.value?.source_id)) {
    selected.value = displayResults.value[0];
  }
};

const uniqueMerge = (...groups: Destination[][]) => {
  const seen = new Set<string>();
  return groups.flat().filter((item) => {
    const key = item.source_id || item.name;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
};

const onInputBlur = () => {
  setTimeout(() => {
    showDropdown.value = false;
  }, 150);
};

const applyHistory = (item: string) => {
  query.value = item;
  showDropdown.value = false;
  search();
};

const applySuggestion = (item: string) => {
  query.value = item;
  showDropdown.value = false;
  search();
};

const removeTag = (key: string) => {
  if (key === "city") cityFilter.value = "全部";
  if (key === "category") categoryFilter.value = "全部";
};

const search = async () => {
  if (!query.value.trim()) return;

  const normalized = query.value.trim();
  const existingIndex = history.value.indexOf(normalized);
  if (existingIndex !== -1) {
    history.value.splice(existingIndex, 1);
  }
  history.value.unshift(normalized);
  history.value = history.value.slice(0, 10);
  localStorage.setItem(historyKey, JSON.stringify(history.value));

  showDropdown.value = false;
  loading.value = true;
  error.value = "";

  try {
    const { data } = await api.post<DestinationSearchResponse>("/destinations/search", {
      query: normalized,
      keywords: normalized.split(/\s+/).filter(Boolean),
      category: categoryFilter.value === "全部" ? null : categoryFilter.value,
    });

    exactRaw.value = data.exact ? [data.exact] : [];
    fuzzyRaw.value = uniqueMerge(data.fuzzy ?? [], data.featured ?? []);
    ensureSelection();
  } catch {
    error.value = "搜索失败，请稍后再试。";
  } finally {
    loading.value = false;
  }
};

watch([exactResults, fuzzyResults], ensureSelection, { immediate: false });

onMounted(async () => {
  history.value = JSON.parse(localStorage.getItem(historyKey) || "[]");
  await store.loadFeaturedDestinations(true);
  await search();
});
</script>
