<template>
  <div class="diary-page space-y-6">
    <section class="card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">旅游日记</p>
          <h2 class="text-2xl font-bold text-slate-950 mt-1">日记发现</h2>
          <p class="text-sm text-slate-500 mt-2 leading-7 max-w-3xl">
            浏览别人的路线心得、踩坑提醒和目的地故事，点击卡片查看详情；写下自己的旅行记录可以使用顶部的发布按钮。
          </p>
        </div>
        <div class="flex items-center gap-2">
          <router-link to="/diaries/me" class="btn-soft-secondary text-sm">
            我的日记
          </router-link>
          <button class="btn-soft-primary text-sm" @click="openEditor">
            写日记
          </button>
        </div>
      </div>
    </section>

    <section class="card-elevated rounded-[24px] p-5 lg:p-6 space-y-4">
      <div>
        <span class="route-panel-kicker">内容搜索</span>
        <h3 class="text-lg font-bold text-slate-950 mt-1">按关键词查找目的地故事</h3>
      </div>

      <DiarySearchBar
        v-model="query"
        :history-items="historyItems"
        :suggestion-items="suggestionItems"
        :searching="loading"
        :placeholder="searchPlaceholder"
        @submit="onSearch"
        @clear="onClearSearch"
        @apply-history="applyHistory"
        @apply-suggestion="applySuggestion"
      />

      <DiaryFilterBar
        :search-type="searchType"
        :sort="sort"
        @update:searchType="onSearchTypeChange"
        @update:sort="onSortChange"
      />
    </section>

    <div v-if="error" class="alert-soft-error">{{ error }}</div>

    <section class="card-elevated rounded-[24px] p-5 lg:p-6">
      <div class="flex items-start justify-between gap-4 flex-wrap mb-5">
        <div v-if="hasSearched">
          <span class="route-panel-kicker">搜索结果</span>
          <h3 class="text-lg font-bold text-slate-950 mt-1">
            {{ currentSearchTypeLabel }} ·「{{ submittedQuery }}」
          </h3>
          <p class="text-xs text-slate-500 mt-1">排序：{{ currentSortLabel }}</p>
        </div>
        <div v-else>
          <span class="route-panel-kicker">推荐日记</span>
          <h3 class="text-lg font-bold text-slate-950 mt-1">从别人的路线经验开始看</h3>
          <p class="text-xs text-slate-500 mt-1">排序：{{ currentSortLabel }}</p>
        </div>
        <span v-if="hasSearched" class="route-summary-chip route-summary-chip-accent">
          {{ loading ? "搜索中" : `${items.length} 条结果` }}
        </span>
        <span v-else class="route-summary-chip">{{ items.length }} 篇</span>
      </div>

      <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <SkeletonCard v-for="n in 4" :key="n" />
      </div>
      <div
        v-else-if="hasSearched && items.length === 0"
        class="rounded-[20px] border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500"
      >
        没有找到匹配的日记，换个关键词或搜索方式试试。
      </div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
        <DiaryCard
          v-for="item in items"
          :key="`${hasSearched ? 'search' : 'recommend'}-${item.id}`"
          :diary="item"
          :variant="hasSearched ? 'search' : 'recommend'"
          @select="selectDiary"
        />
      </div>

      <DiaryAlgorithmPanel
        class="mt-5"
        :search-type="hasSearched ? searchType : null"
        :sort="sort"
        :debug="lastDebug"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import SkeletonCard from "../components/SkeletonCard.vue";
import { discoverDiaries } from "../features/diary/api/diaryApi";
import DiaryAlgorithmPanel from "../features/diary/components/DiaryAlgorithmPanel.vue";
import DiaryCard from "../features/diary/components/DiaryCard.vue";
import DiaryFilterBar from "../features/diary/components/DiaryFilterBar.vue";
import DiarySearchBar from "../features/diary/components/DiarySearchBar.vue";
import type {
  Diary,
  DiaryAlgorithmDebug,
  DiarySearchType,
  DiarySortKey,
} from "../features/diary/types/diary";
import { useAuthStore } from "../stores/auth";

const SEARCH_TYPE_LABELS: Record<DiarySearchType, string> = {
  destination: "目的地搜索",
  title_exact: "标题精确查询",
  fulltext: "正文全文检索",
};

const SORT_LABELS: Record<DiarySortKey, string> = {
  recommend: "综合推荐",
  views: "热度最高",
  rating: "评分最高",
  latest: "最新发布",
};

const SEARCH_TYPE_PLACEHOLDERS: Record<DiarySearchType, string> = {
  destination: "输入目的地名称，例如：故宫博物院",
  title_exact: "输入完整的日记标题",
  fulltext: "输入正文中的关键词，多个空格分隔",
};

const isSearchType = (value: unknown): value is DiarySearchType =>
  value === "destination" || value === "title_exact" || value === "fulltext";

const isSortKey = (value: unknown): value is DiarySortKey =>
  value === "recommend" || value === "views" || value === "rating" || value === "latest";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const items = ref<Diary[]>([]);
const loading = ref(false);
const error = ref("");
const submittedQuery = ref("");
const lastDebug = ref<DiaryAlgorithmDebug | null>(null);

const query = ref("");
const searchType = ref<DiarySearchType>("destination");
const sort = ref<DiarySortKey>("recommend");

const historyKey = "diary_search_history";
const history = ref<string[]>([]);

const hasSearched = computed(() => Boolean(submittedQuery.value));
const currentSearchTypeLabel = computed(() => SEARCH_TYPE_LABELS[searchType.value]);
const currentSortLabel = computed(() => SORT_LABELS[sort.value]);
const searchPlaceholder = computed(() => SEARCH_TYPE_PLACEHOLDERS[searchType.value]);

const historyItems = computed(() => {
  if (!query.value.trim()) return history.value.slice(0, 8);
  const lowered = query.value.toLowerCase();
  return history.value.filter((item) => item.toLowerCase().includes(lowered)).slice(0, 6);
});

const suggestionItems = computed(() => {
  const lowered = query.value.trim().toLowerCase();
  if (!lowered) return [];

  const titles = items.value.map((item) => item.title).filter(Boolean);
  const destinationNames = items.value.map((item) => item.destination_name).filter(Boolean);
  const allItems = [...titles, ...destinationNames];
  return [...new Set(allItems.filter((item) => item.toLowerCase().includes(lowered)))].slice(0, 6);
});

const saveToHistory = (value: string) => {
  const existingIndex = history.value.indexOf(value);
  if (existingIndex !== -1) {
    history.value.splice(existingIndex, 1);
  }
  history.value.unshift(value);
  history.value = history.value.slice(0, 10);
  localStorage.setItem(historyKey, JSON.stringify(history.value));
};

const syncUrl = () => {
  const next: Record<string, string> = {
    search_type: searchType.value,
    sort: sort.value,
  };
  if (submittedQuery.value) next.q = submittedQuery.value;
  router.replace({ query: next }).catch(() => undefined);
};

const load = async () => {
  loading.value = true;
  error.value = "";
  try {
    const res = await discoverDiaries({
      q: submittedQuery.value || undefined,
      search_type: submittedQuery.value ? searchType.value : undefined,
      sort: sort.value,
    });
    items.value = res.items ?? [];
    lastDebug.value = res.debug ?? null;
  } catch {
    error.value = "加载日记失败，请稍后再试。";
    items.value = [];
    lastDebug.value = null;
  } finally {
    loading.value = false;
  }
};

const onSearch = async () => {
  const normalized = query.value.trim();
  submittedQuery.value = normalized;
  if (normalized) saveToHistory(normalized);
  syncUrl();
  await load();
};

const onClearSearch = async () => {
  submittedQuery.value = "";
  syncUrl();
  await load();
};

const onSearchTypeChange = async (next: DiarySearchType) => {
  searchType.value = next;
  syncUrl();
  if (submittedQuery.value) await load();
};

const onSortChange = async (next: DiarySortKey) => {
  sort.value = next;
  syncUrl();
  await load();
};

const applyHistory = async (item: string) => {
  query.value = item;
  await onSearch();
};

const applySuggestion = async (item: string) => {
  query.value = item;
  await onSearch();
};

const selectDiary = (item: Diary) => {
  router.push(`/diaries/${item.id}`);
};

const openEditor = () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  router.push("/diaries/new");
};

onMounted(async () => {
  history.value = JSON.parse(localStorage.getItem(historyKey) || "[]");

  // Restore state from URL
  const q = route.query;
  if (typeof q.q === "string") {
    query.value = q.q;
    submittedQuery.value = q.q;
  }
  if (isSearchType(q.search_type)) searchType.value = q.search_type;
  if (isSortKey(q.sort)) sort.value = q.sort;

  await load();
});
</script>
