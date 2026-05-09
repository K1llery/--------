<template>
  <div class="space-y-6">
    <!-- Search bar -->
    <div class="bg-white rounded-3xl card-elevated p-6">
      <h2 class="text-xl font-bold text-gray-900">搜索目的地</h2>
      <p class="text-sm text-gray-500 mt-1">支持名称搜索，并按城市和类别进一步缩小范围。</p>
      <form class="relative flex flex-wrap gap-3 mt-5" @submit.prevent="search">
        <div class="relative flex-1 min-w-[200px]">
          <input
            v-model="query"
            placeholder="搜索景点、高校、商圈名称"
            class="w-full soft-control text-sm pr-10"
            @focus="showDropdown = true"
            @blur="onInputBlur"
            @input="showDropdown = true"
          />
          <button
            v-if="query"
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            @click="query = ''"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
          <!-- Dropdown -->
          <div
            v-if="showDropdown && (historyItems.length || suggestionItems.length)"
            class="absolute z-20 top-full left-0 right-0 mt-1 bg-white rounded-xl card-elevated shadow-lg overflow-hidden"
          >
            <div v-if="historyItems.length" class="px-3 py-2">
              <p class="text-xs text-gray-400 font-medium mb-1.5">历史记录</p>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="item in historyItems"
                  :key="item"
                  class="text-xs px-2.5 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-primary-50 hover:text-primary-700 transition-colors"
                  @mousedown.prevent="applyHistory(item)"
                >
                  {{ item }}
                </button>
              </div>
            </div>
            <div v-if="suggestionItems.length" class="px-3 py-2 border-t border-gray-100">
              <p class="text-xs text-gray-400 font-medium mb-1.5">关键词提示</p>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="item in suggestionItems"
                  :key="item"
                  class="text-xs px-2.5 py-1 rounded-full bg-primary-50 text-primary-700 hover:bg-primary-100 transition-colors"
                  @mousedown.prevent="applySuggestion(item)"
                >
                  {{ item }}
                </button>
              </div>
            </div>
          </div>
        </div>
        <select v-model="cityFilter" class="soft-control text-sm text-gray-700">
          <option value="全部">全部城市</option>
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>
        <select v-model="categoryFilter" class="soft-control text-sm text-gray-700">
          <option value="全部">全部类别</option>
          <option value="scenic">景点</option>
          <option value="shopping">商场/商圈</option>
          <option value="campus">高校/校园</option>
        </select>
        <button type="submit" v-ripple class="btn-soft-primary text-sm">
          {{ loading ? "搜索中..." : "搜索" }}
        </button>
      </form>
    </div>
    <!-- Status -->
    <div v-if="error" class="alert-soft-error">{{ error }}</div>
    <div v-else-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <SkeletonCard v-for="n in 6" :key="n" />
    </div>
    <EmptyState
      v-else-if="!displayResults.length"
      title="未找到匹配结果"
      description="试试更短的关键词或切换城市。"
    />
    <!-- Results -->
    <div v-else class="grid lg:grid-cols-[1.4fr_1fr] gap-6">
      <div class="space-y-6">
        <!-- Exact -->
        <section v-if="exactResults.length">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold text-gray-900">精确匹配</h3>
            <span class="text-xs text-gray-400">{{ exactResults.length }} 条</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
            <article
              v-for="item in exactResults"
              :key="`exact-${item.source_id}`"
              v-tilt
              class="group rounded-2xl bg-white overflow-hidden cursor-pointer transition-all duration-300"
              :class="
                selected?.source_id === item.source_id
                  ? ' shadow-md shadow-primary-500/10 ring-1 ring-primary-200'
                  : ' hover:shadow-lg '
              "
              @click="selected = item"
            >
              <div class="h-28 bg-gray-100 overflow-hidden">
                <RealImage
                  :src="item.image_url"
                  :alt="item.name"
                  :name="item.name"
                  :city="item.city"
                  :latitude="item.latitude"
                  :longitude="item.longitude"
                  :source-url="item.source_url"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div class="p-3">
                <h3 class="font-semibold text-gray-900 text-sm">
                  {{ item.name }}
                </h3>
                <p class="text-xs text-gray-500 mt-1">
                  {{ categoryLabel(item.category) }} · {{ item.city }}
                </p>
                <div class="flex gap-2 mt-1.5">
                  <span
                    class="text-xs px-2 py-0.5 rounded-full bg-primary-50 text-primary-600 font-medium"
                    >{{ displayMetric(item.rating) }}</span
                  ><span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
                    >热度 {{ displayMetric(item.heat) }}</span
                  >
                </div>
              </div>
            </article>
          </div>
        </section>
        <!-- Fuzzy -->
        <section>
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold text-gray-900">相关结果</h3>
            <span class="text-xs text-gray-400">{{ fuzzyResults.length }} 条</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
            <article
              v-for="item in fuzzyResults"
              :key="`fuzzy-${item.source_id}`"
              v-tilt
              class="group rounded-2xl bg-white overflow-hidden cursor-pointer glow-border shadow-md shadow-gray-200/50 transition-all duration-300"
              :class="
                selected?.source_id === item.source_id
                  ? ' shadow-md shadow-primary-500/10 ring-1 ring-primary-200'
                  : ' '
              "
              @click="selected = item"
            >
              <div class="h-28 bg-gray-100 overflow-hidden">
                <RealImage
                  :src="item.image_url"
                  :alt="item.name"
                  :name="item.name"
                  :city="item.city"
                  :latitude="item.latitude"
                  :longitude="item.longitude"
                  :source-url="item.source_url"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div class="p-3">
                <h3 class="font-semibold text-gray-900 text-sm">
                  {{ item.name }}
                </h3>
                <p class="text-xs text-gray-500 mt-1">
                  {{ categoryLabel(item.category) }} · {{ item.city || "北京" }}
                </p>
                <div class="flex gap-2 mt-1.5">
                  <span
                    class="text-xs px-2 py-0.5 rounded-full bg-primary-50 text-primary-600 font-medium"
                    >{{ displayMetric(item.rating) }}</span
                  ><span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
                    >热度 {{ displayMetric(item.heat) }}</span
                  >
                </div>
              </div>
            </article>
          </div>
        </section>
      </div>
      <!-- Detail -->
      <div
        v-if="selected"
        class="bg-white rounded-3xl card-elevated p-5 sticky top-16 self-start space-y-4"
      >
        <RealImage
          :src="selected.image_url"
          :alt="selected.name"
          :name="selected.name"
          :city="selected.city"
          :latitude="selected.latitude"
          :longitude="selected.longitude"
          :source-url="selected.source_url"
          class="w-full h-56 object-cover rounded-2xl bg-gray-100"
        />
        <div>
          <h3 class="text-lg font-bold text-gray-900">{{ selected.name }}</h3>
          <p class="text-sm text-gray-500 mt-1">
            {{ categoryLabel(selected.category) }} ·
            {{ selected.city || "北京" }}
          </p>
          <p class="text-sm text-gray-500 mt-0.5">
            {{ selected.address || "地址待补充" }}
          </p>
          <p class="text-sm text-gray-600 mt-3 leading-relaxed">
            {{ selected.description || "这是一个值得进一步探索的城市目的地。" }}
          </p>
          <div class="flex flex-wrap gap-2 mt-4">
            <span
              class="text-xs px-3 py-1.5 rounded-full bg-primary-50 text-primary-700 font-medium"
              >评分 {{ displayMetric(selected.rating) }}</span
            >
            <span class="text-xs px-3 py-1.5 rounded-full bg-accent-50 text-accent-600 font-medium"
              >热度 {{ displayMetric(selected.heat) }}</span
            >
          </div>
          <p v-if="selected.source_url" class="text-xs text-gray-400 mt-3">
            数据来源：<a
              :href="selected.source_url"
              target="_blank"
              rel="noreferrer"
              class="text-primary-600 hover:underline"
              >{{ selected.source_name || "公开来源" }}</a
            >
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { api } from "../api/client";
import EmptyState from "../components/EmptyState.vue";
import RealImage from "../components/RealImage.vue";
import SkeletonCard from "../components/SkeletonCard.vue";
import { useTravelStore } from "../stores/travel";
const store = useTravelStore();
const query = ref("外滩");
const cityFilter = ref("全部");
const categoryFilter = ref("全部");
const loading = ref(false);
const error = ref("");
const exactRaw = ref<any[]>([]);
const fuzzyRaw = ref<any[]>([]);
const selected = ref<any | null>(null);
const showDropdown = ref(false);
const historyKey = "search_history";
const history = ref<string[]>(JSON.parse(localStorage.getItem(historyKey) || "[]"));
const historyItems = computed(() => {
  if (!query.value.trim()) return history.value.slice(0, 8);
  const q = query.value.toLowerCase();
  return history.value.filter((item) => item.toLowerCase().includes(q)).slice(0, 6);
});
const suggestionItems = computed(() => {
  const q = query.value.trim().toLowerCase();
  console.log("[SearchPage] query=", query.value, "allDestinations count=", allDestinations.value.length, "suggestion filter:", q);
  if (!q) return [];
  return allDestinations.value
    .filter((d) => d.name.toLowerCase().includes(q) || (d.city && d.city.toLowerCase().includes(q)))
    .slice(0, 6)
    .map((d) => d.name);
});
const allDestinations = computed(() => store.destinations.items);
const onInputBlur = () => setTimeout(() => (showDropdown.value = false), 150);
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
const cities = ["北京", "上海", "广州", "深圳"];
const categoryLabel = (value: string) => {
  if (value === "shopping") return "商场/商圈";
  if (value === "campus") return "高校/校园";
  return "景点";
};
const displayMetric = (value: number | null | undefined) => value ?? "待补充";
const filtered = (items: any[]) =>
  items.filter((item) => {
    const cityMatch = cityFilter.value === "全部" || item.city === cityFilter.value;
    const categoryMatch = categoryFilter.value === "全部" || item.category === categoryFilter.value;
    return cityMatch && categoryMatch;
  });
const exactResults = computed(() => filtered(exactRaw.value));
const fuzzyResults = computed(() => filtered(fuzzyRaw.value));
const displayResults = computed(() => [...exactResults.value, ...fuzzyResults.value]);
const uniqueMerge = (...groups: any[][]) => {
  const seen = new Set<string>();
  return groups.flat().filter((item) => {
    const key = item.source_id || item.name;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
};
const search = async () => {
  if (!query.value.trim()) return;
  const q = query.value.trim();
  const exists = history.value.indexOf(q);
  if (exists !== -1) history.value.splice(exists, 1);
  history.value.unshift(q);
  history.value = history.value.slice(0, 10);
  localStorage.setItem(historyKey, JSON.stringify(history.value));
  showDropdown.value = false;
  loading.value = true;
  error.value = "";
  try {
    const { data } = await api.post("/destinations/search", {
      query: q,
      keywords: q.split(/\s+/).filter(Boolean),
      category: categoryFilter.value === "全部" ? null : categoryFilter.value,
    });
    exactRaw.value = data.exact ? [data.exact] : [];
    fuzzyRaw.value = uniqueMerge(data.fuzzy ?? [], data.featured ?? []);
    selected.value = exactRaw.value[0] ?? fuzzyRaw.value[0] ?? null;
  } catch (searchError) {
    error.value = "搜索失败，请稍后再试。";
  } finally {
    loading.value = false;
  }
};
onMounted(async () => {
  await store.loadFeaturedDestinations(true);
  await search();
});
</script>
