<template>
  <div class="diary-page space-y-6">
    <section class="card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">旅游日记</p>
          <h2 class="text-2xl font-bold text-slate-950 mt-1">内容交流与旅途记录</h2>
          <p class="text-sm text-slate-500 mt-2 leading-7 max-w-3xl">
            先浏览别人的路线心得、踩坑提醒和目的地故事，再决定是否写下自己的旅行记录，补充 AI 帮写、封面生成与动画演示。
          </p>
        </div>
        <button class="btn-soft-primary text-sm" @click="openComposer">
          {{ showComposer ? "收起创作区" : "发布日记" }}
        </button>
      </div>
    </section>

    <section v-if="showComposer" class="card-elevated rounded-[24px] p-5 lg:p-6 space-y-5">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <span class="route-panel-kicker">创作面板</span>
          <h3 class="text-lg font-bold text-slate-950 mt-1">写一篇新的旅行日记</h3>
          <p class="text-sm text-slate-500 mt-2">
            这里保留课程演示需要的 AI 帮写、AI 封面和真实图片兜底能力，但默认收起，不打断内容浏览。
          </p>
        </div>
        <span class="route-summary-chip route-summary-chip-accent">登录后可用</span>
      </div>

      <form class="space-y-4" @submit.prevent="publishDiary">
        <div class="grid lg:grid-cols-[minmax(0,1fr)_320px] gap-5 items-start">
          <div class="space-y-4">
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="field-label">目的地</label>
                <select v-model="draft.destination_name" class="soft-control w-full">
                  <option v-for="item in destinations" :key="item.source_id" :value="item.name">
                    {{ item.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="field-label">标题</label>
                <input
                  v-model="draft.title"
                  class="soft-control w-full"
                  placeholder="例如：一天走完鼓浪屿的轻松路线"
                />
              </div>
            </div>

            <div>
              <label class="field-label">正文</label>
              <textarea
                v-model="draft.content"
                class="soft-control w-full min-h-40"
                placeholder="写下游览体验、路线建议、避坑提醒或值得停留的细节。"
              ></textarea>
            </div>

            <div class="flex flex-wrap gap-3">
              <button
                class="btn-soft-secondary text-sm"
                type="button"
                :disabled="aiDrafting"
                @click="generateDiaryDraft"
              >
                {{ aiDrafting ? "正在生成..." : "AI 帮写日记" }}
              </button>
              <button
                class="btn-soft-secondary text-sm"
                type="button"
                :disabled="aiImageGenerating || !draft.title || !draft.content"
                @click="generateCoverImage"
              >
                {{ aiImageGenerating ? "正在生成..." : "AI 生成封面" }}
              </button>
              <button class="btn-soft-primary text-sm" type="submit" :disabled="publishing">
                {{ publishing ? "发布中..." : "确认发布" }}
              </button>
            </div>

            <div v-if="aiError" class="alert-soft-error">{{ aiError }}</div>
          </div>

          <aside class="diary-composer-preview">
            <span class="route-panel-kicker">封面预览</span>
            <RealImage
              v-if="coverPreview"
              :src="coverPreview.image_url"
              :alt="draft.destination_name || '日记封面'"
              :name="draft.destination_name || '旅行日记'"
              :city="coverPreview.city"
              :latitude="coverPreview.latitude"
              :longitude="coverPreview.longitude"
              :source-url="coverPreview.source_url"
              class="w-full h-52 object-cover rounded-[20px] bg-slate-100 mt-3"
            />
            <div v-else class="diary-composer-empty mt-3">
              <p>选择目的地并填写内容后，这里会显示真实图源或 AI 封面结果。</p>
            </div>
          </aside>
        </div>
      </form>
    </section>

    <section class="card-elevated rounded-[24px] p-5 lg:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <span class="route-panel-kicker">内容搜索</span>
          <h3 class="text-lg font-bold text-slate-950 mt-1">按关键词查找目的地故事</h3>
        </div>
        <span class="text-xs text-slate-400">
          推荐会优先展示精选日记，搜索结果单独列出
        </span>
      </div>

      <form class="search-workbench" @submit.prevent="search">
        <div class="search-input-shell">
          <div class="relative">
            <input
              v-model="query"
              class="soft-control search-input-control w-full pr-10"
              placeholder="输入目的地、标题关键词或旅行主题"
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
          <button class="btn-soft-primary text-sm min-w-[120px]" type="submit">
            {{ searching ? "搜索中..." : "搜索日记" }}
          </button>
        </div>
      </form>
    </section>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <section class="route-insight-card">
        <span class="route-panel-kicker">推荐内容</span>
        <h3>{{ diaries.length }} 篇</h3>
        <p>推荐区适合展示热门或最新日记，帮助用户先进入内容浏览状态。</p>
      </section>
      <section class="route-insight-card">
        <span class="route-panel-kicker">搜索结果</span>
        <h3>{{ searchResults.length }} 篇</h3>
        <p>输入关键词后，这里会聚焦返回匹配内容，便于精确查找特定目的地经验。</p>
      </section>
      <section class="route-insight-card">
        <span class="route-panel-kicker">当前阅读</span>
        <h3>{{ selected?.title || "等待选择" }}</h3>
        <p>右侧详情会集中展示正文、互动指标、压缩演示和 AIGC 动画脚本。</p>
      </section>
    </div>

    <div v-if="error" class="alert-soft-error">{{ error }}</div>

    <div class="grid xl:grid-cols-[minmax(0,1.2fr)_380px] gap-6 items-start">
      <div class="space-y-6">
        <section class="card-elevated rounded-[24px] p-5 lg:p-6">
          <div class="flex items-start justify-between gap-4 flex-wrap mb-5">
            <div>
              <span class="route-panel-kicker">推荐日记</span>
              <h3 class="text-lg font-bold text-slate-950 mt-1">从别人的路线经验开始看</h3>
              <p class="text-sm text-slate-500 mt-2">
                先看推荐内容，快速判断哪些目的地值得继续进入导航、收藏或行程规划。
              </p>
            </div>
            <span class="route-summary-chip">{{ diaries.length }} 篇</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
            <article
              v-for="item in diaries"
              :key="item.id"
              class="diary-card"
              :class="{ 'diary-card-active': selected?.id === item.id }"
              @click="selectDiary(item)"
            >
              <RealImage
                :src="item.media_urls?.[0]"
                :alt="item.title"
                :name="item.destination_name || item.title"
                :search-hint="item.destination_name"
                class="w-full h-40 object-cover rounded-[18px] bg-slate-100"
              />
              <div class="space-y-3 mt-4">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <h4 class="text-base font-bold text-slate-900 line-clamp-1">{{ item.title }}</h4>
                    <p class="text-sm text-slate-500 mt-1">{{ item.destination_name }}</p>
                  </div>
                  <span class="diary-meta-pill">{{ item.rating.toFixed(1) }}</span>
                </div>
                <p class="text-sm text-slate-400 line-clamp-2">{{ item.content }}</p>
                <div class="flex flex-wrap gap-2">
                  <span class="home-score-pill">浏览 {{ item.views }}</span>
                  <span class="home-heat-pill">作者 {{ item.author_name || "匿名旅行者" }}</span>
                </div>
              </div>
            </article>
          </div>
        </section>

        <section class="card-elevated rounded-[24px] p-5 lg:p-6">
          <div class="flex items-start justify-between gap-4 flex-wrap mb-5">
            <div>
              <span class="route-panel-kicker">搜索结果</span>
              <h3 class="text-lg font-bold text-slate-950 mt-1">按关键词继续收窄内容</h3>
              <p class="text-sm text-slate-500 mt-2">
                搜索区专门承接精确查找，不会覆盖推荐区，方便横向比较和回看。
              </p>
            </div>
            <span class="route-summary-chip route-summary-chip-accent">
              {{ searching ? "搜索中" : `${searchResults.length} 条结果` }}
            </span>
          </div>

          <div v-if="searching" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <SkeletonCard v-for="n in 4" :key="n" />
          </div>
          <div
            v-else-if="searchResults.length === 0"
            class="rounded-[20px] border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500"
          >
            输入关键词后，这里会显示匹配到的旅行日记。
          </div>
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
            <article
              v-for="item in searchResults"
              :key="`search-${item.id}`"
              class="diary-card diary-card-compact"
              :class="{ 'diary-card-active': selected?.id === item.id }"
              @click="selectDiary(item)"
            >
              <div class="space-y-3">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <h4 class="text-base font-bold text-slate-900 line-clamp-1">{{ item.title }}</h4>
                    <p class="text-sm text-slate-500 mt-1">{{ item.destination_name }}</p>
                  </div>
                  <span class="diary-meta-pill diary-meta-pill-accent">匹配</span>
                </div>
                <p class="text-sm text-slate-400 line-clamp-2">{{ item.content }}</p>
                <div class="flex flex-wrap gap-2">
                  <span class="home-score-pill">浏览 {{ item.views }}</span>
                  <span class="home-heat-pill">评分 {{ item.rating.toFixed(1) }}</span>
                </div>
              </div>
            </article>
          </div>
        </section>
      </div>

      <aside class="space-y-5">
        <section
          v-if="selected"
          class="card-elevated rounded-[24px] p-5 sticky top-18 self-start space-y-5 diary-detail-card"
        >
          <RealImage
            :src="selected.media_urls?.[0]"
            :alt="selected.title"
            :name="selected.destination_name || selected.title"
            :search-hint="selected.destination_name"
            class="w-full h-56 object-cover rounded-[20px] bg-slate-100"
          />

          <div class="space-y-3">
            <div class="flex items-start justify-between gap-4">
              <div>
                <span class="route-panel-kicker">当前详情</span>
                <h3 class="text-xl font-bold text-slate-950 mt-1">{{ selected.title }}</h3>
              </div>
              <span class="route-summary-chip route-summary-chip-accent">{{ selected.destination_name }}</span>
            </div>
            <p class="text-sm text-slate-500">
              作者：{{ selected.author_name || "匿名旅行者" }} · 发布时间：{{ selected.created_at || "演示数据" }}
            </p>
            <p class="text-sm text-slate-600 leading-7">{{ selected.content }}</p>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="route-metric-tile">
              <strong>{{ selected.views }}</strong>
              <span>浏览量</span>
            </div>
            <div class="route-metric-tile">
              <strong>{{ selected.rating.toFixed(1) }}</strong>
              <span>平均评分</span>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <button class="btn-soft-primary text-sm" @click="compress">压缩正文演示</button>
            <button class="btn-soft-secondary text-sm" :disabled="!compressionPayload" @click="decompress">
              解压回放
            </button>
            <button class="btn-soft-secondary text-sm" @click="addView">浏览 +1</button>
            <button class="btn-soft-secondary text-sm" @click="rateDiary(4)">评分 4.0</button>
            <button class="btn-soft-secondary text-sm" @click="rateDiary(5)">评分 5.0</button>
          </div>

          <div class="flex flex-wrap gap-2">
            <button class="btn-soft-primary text-sm" @click="generateAnimation">
              {{ animationLoading ? "生成中..." : "生成 AIGC 动画" }}
            </button>
            <button class="btn-soft-secondary text-sm" :disabled="!animationResult?.shots?.length" @click="playAnimation">
              播放预览
            </button>
            <button class="btn-soft-secondary text-sm" :disabled="!animationResult?.shots?.length" @click="pauseAnimation">
              暂停预览
            </button>
          </div>

          <pre v-if="compressionResult" class="diary-code-block">{{ compressionResult }}</pre>
          <pre v-if="decompressedContent" class="diary-code-block">解压结果:
{{ decompressedContent }}</pre>

          <section v-if="animationResult" class="space-y-4">
            <div class="flex items-center justify-between gap-3">
              <h4 class="text-base font-bold text-slate-950">AIGC 旅行动画脚本</h4>
              <span class="text-xs text-slate-400">
                {{ animationResult.generation_mode }} · {{ animationResult.total_duration_seconds }} 秒
              </span>
            </div>

            <div v-if="activeShot" class="diary-shot-preview">
              <RealImage
                :src="activeShot.media_url || selected.media_urls?.[0]"
                :alt="activeShot.caption"
                :name="selected.destination_name || selected.title"
                :search-hint="selected.destination_name"
                class="w-full h-48 object-cover"
              />
              <div class="diary-shot-overlay">
                <strong>镜头 {{ activeShot.index }}</strong>
                <p>{{ activeShot.caption }}</p>
                <span>{{ activeShot.transition }} · {{ activeShot.duration_seconds }} 秒</span>
              </div>
            </div>

            <p class="text-sm text-slate-600 leading-7">
              <strong>旁白串联：</strong>{{ animationResult.narration_script }}
            </p>

            <div class="grid grid-cols-1 gap-3">
              <article
                v-for="shot in animationResult.shots"
                :key="`shot-${shot.index}`"
                class="diary-shot-card"
                :class="{ 'diary-shot-card-active': activeShot?.index === shot.index }"
                @click="activeShotIndex = shot.index - 1"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <h5 class="text-sm font-bold text-slate-900">镜头 {{ shot.index }}</h5>
                    <p class="text-xs text-slate-500 mt-1">{{ shot.caption }}</p>
                  </div>
                  <span class="text-xs text-slate-400">{{ shot.duration_seconds }} 秒</span>
                </div>
              </article>
            </div>
          </section>
        </section>

        <section v-else class="card-elevated rounded-[24px] p-5 space-y-3">
          <span class="route-panel-kicker">详情面板</span>
          <h3 class="text-lg font-bold text-slate-950">先从左侧选择一篇日记</h3>
          <p class="text-sm text-slate-500 leading-7">
            这里会集中展示正文、互动指标、压缩演示和 AIGC 动画脚本，方便课堂展示和内容浏览。
          </p>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";

import { api } from "../api/client";
import RealImage from "../components/RealImage.vue";
import SkeletonCard from "../components/SkeletonCard.vue";
import { useAuthStore } from "../stores/auth";
import { useTravelStore } from "../stores/travel";
import type {
  CompressionResponse,
  DiaryDraftResponse,
  ImageGenerateResponse,
} from "../types/api";
import type { Destination, Diary } from "../types/models";
import { resolveRealMedia } from "../utils/realMedia";

interface DiaryAnimationShot {
  index: number;
  caption: string;
  media_url: string;
  transition: string;
  duration_seconds: number;
}

interface DiaryAnimationResult {
  generation_mode: string;
  total_duration_seconds: number;
  narration_script: string;
  shots: DiaryAnimationShot[];
}

type CoverPreview = {
  image_url: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  source_url?: string;
};

type ApiFailure = {
  response?: {
    data?: {
      detail?: string;
    };
  };
};

const store = useTravelStore();
const auth = useAuthStore();

const diaries = computed(() => store.diaries.items as Diary[]);
const selected = computed(() => store.diaries.selected as Diary | null);
const error = computed(() => store.diaries.error);
const searchResults = computed(() => store.diarySearchResults.items as Diary[]);
const searching = computed(() => store.diarySearchResults.loading);
const destinations = computed(() => store.destinations.items as Destination[]);

const query = ref("故宫");
const compressionResult = ref("");
const compressionPayload = ref<{ encoded: string; codes: Record<string, string> } | null>(null);
const decompressedContent = ref("");
const showComposer = ref(false);
const publishing = ref(false);
const aiDrafting = ref(false);
const aiImageGenerating = ref(false);
const aiError = ref("");
const generatedCoverUrl = ref("");
const showDropdown = ref(false);

const historyKey = "diary_search_history";
const history = ref<string[]>([]);

const animationResult = ref<DiaryAnimationResult | null>(null);
const animationLoading = ref(false);
const activeShotIndex = ref(0);
let animationTimer: number | null = null;

const draft = reactive({
  destination_name: "",
  title: "",
  content: "",
});

const historyItems = computed(() => {
  if (!query.value.trim()) return history.value.slice(0, 8);
  const lowered = query.value.toLowerCase();
  return history.value.filter((item) => item.toLowerCase().includes(lowered)).slice(0, 6);
});

const suggestionItems = computed(() => {
  const lowered = query.value.trim().toLowerCase();
  if (!lowered) return [];

  const titles = diaries.value.map((item) => item.title).filter(Boolean);
  const destinationNames = diaries.value.map((item) => item.destination_name).filter(Boolean);
  const allItems = [...titles, ...destinationNames];
  return [...new Set(allItems.filter((item) => item.toLowerCase().includes(lowered)))].slice(0, 6);
});

const draftCover = computed(
  () => destinations.value.find((item) => item.name === draft.destination_name) ?? null,
);

const coverPreview = computed<CoverPreview | null>(() => {
  if (generatedCoverUrl.value) {
    return {
      image_url: generatedCoverUrl.value,
      city: draftCover.value?.city,
      latitude: draftCover.value?.latitude,
      longitude: draftCover.value?.longitude,
      source_url: generatedCoverUrl.value,
    };
  }

  if (!draftCover.value?.image_url) return null;

  return {
    image_url: draftCover.value.image_url,
    city: draftCover.value.city,
    latitude: draftCover.value.latitude,
    longitude: draftCover.value.longitude,
    source_url: draftCover.value.source_url,
  };
});

const activeShot = computed(() => animationResult.value?.shots?.[activeShotIndex.value] ?? null);

const apiErrorDetail = (error: unknown, fallback: string) =>
  (error as ApiFailure)?.response?.data?.detail || fallback;

const onInputBlur = () => {
  setTimeout(() => {
    showDropdown.value = false;
  }, 150);
};

const saveToHistory = (value: string) => {
  const existingIndex = history.value.indexOf(value);
  if (existingIndex !== -1) {
    history.value.splice(existingIndex, 1);
  }
  history.value.unshift(value);
  history.value = history.value.slice(0, 10);
  localStorage.setItem(historyKey, JSON.stringify(history.value));
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

const selectDiary = async (item: Diary) => {
  await store.selectDiary(item);
};

const search = async () => {
  const normalized = query.value.trim();
  if (normalized) saveToHistory(normalized);
  await store.searchDiaries(normalized);
};

const compress = async () => {
  if (!selected.value) return;
  const { data } = await api.post<CompressionResponse>("/diaries/compress", {
    content: selected.value.content,
  });
  compressionPayload.value = { encoded: data.encoded, codes: data.codes };
  decompressedContent.value = "";
  compressionResult.value = JSON.stringify(data, null, 2);
};

const decompress = async () => {
  if (!compressionPayload.value) return;
  const { data } = await api.post<{ content: string }>("/diaries/decompress", compressionPayload.value);
  decompressedContent.value = data.content;
};

const pauseAnimation = () => {
  if (animationTimer !== null) {
    window.clearInterval(animationTimer);
    animationTimer = null;
  }
};

const playAnimation = () => {
  const shotCount = animationResult.value?.shots?.length ?? 0;
  if (!shotCount) return;

  pauseAnimation();
  animationTimer = window.setInterval(() => {
    activeShotIndex.value = (activeShotIndex.value + 1) % shotCount;
  }, 2200);
};

const generateAnimation = async () => {
  if (!selected.value) return;

  animationLoading.value = true;
  pauseAnimation();

  try {
    const { data } = await api.post<DiaryAnimationResult>(`/diaries/${selected.value.id}/aigc-animation`);
    animationResult.value = data;
    activeShotIndex.value = 0;
    playAnimation();
  } finally {
    animationLoading.value = false;
  }
};

const addView = async () => {
  if (!selected.value) return;
  await store.selectDiary(selected.value, true);
};

const rateDiary = async (score: number) => {
  if (!selected.value) return;
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }

  try {
    await store.rateDiary(selected.value.id, score);
  } catch (ratingError: unknown) {
    store.diaries.error = apiErrorDetail(ratingError, "评分失败，请稍后再试。");
  }
};

const openComposer = () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  showComposer.value = !showComposer.value;
};

const generateDiaryDraft = async () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }

  aiDrafting.value = true;
  aiError.value = "";

  try {
    const { data } = await api.post<DiaryDraftResponse>("/ai/diary/draft", {
      destination_name: draft.destination_name,
      keywords: [draft.destination_name, query.value].filter(Boolean),
      style: "轻松真实，适合课程演示",
    });
    draft.title = data.title;
    draft.content = data.content;
  } catch (draftError: unknown) {
    aiError.value = apiErrorDetail(draftError, "AI 日记生成失败，请检查模型配置。");
  } finally {
    aiDrafting.value = false;
  }
};

const generateCoverImage = async () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }

  aiImageGenerating.value = true;
  aiError.value = "";

  try {
    const { data } = await api.post<ImageGenerateResponse>("/ai/images/generate", {
      destination_name: draft.destination_name,
      title: draft.title,
      content: draft.content,
    });
    generatedCoverUrl.value = data.image_url;
  } catch (imageError: unknown) {
    aiError.value = apiErrorDetail(imageError, "AI 封面生成失败，请检查模型配置。");
  } finally {
    aiImageGenerating.value = false;
  }
};

const publishDiary = async () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }

  publishing.value = true;

  try {
    const fallbackCover = draftCover.value
      ? await resolveRealMedia({
          src: draftCover.value.image_url,
          name: draftCover.value.name,
          city: draftCover.value.city,
          latitude: draftCover.value.latitude,
          longitude: draftCover.value.longitude,
          sourceUrl: draftCover.value.source_url,
          searchHint: draft.destination_name,
        })
      : "";

    const finalCoverImage = generatedCoverUrl.value || fallbackCover || draftCover.value?.image_url || "";

    await api.post("/diaries", {
      destination_name: draft.destination_name,
      title: draft.title,
      content: draft.content,
      cover_image_url: finalCoverImage,
      media_urls: finalCoverImage ? [finalCoverImage] : [],
    });

    showComposer.value = false;
    draft.title = "";
    draft.content = "";
    generatedCoverUrl.value = "";
    await store.loadDiaries(true);
  } finally {
    publishing.value = false;
  }
};

onMounted(async () => {
  history.value = JSON.parse(localStorage.getItem(historyKey) || "[]");
  await Promise.all([store.loadDiaries(false), store.loadFeaturedDestinations(false)]);
  draft.destination_name = destinations.value[0]?.name ?? "";
});

watch(
  () => draft.destination_name,
  () => {
    generatedCoverUrl.value = "";
    aiError.value = "";
  },
);

watch(selected, () => {
  pauseAnimation();
  animationResult.value = null;
  activeShotIndex.value = 0;
});

watch(diaries, (items) => {
  if (!selected.value && items.length) {
    store.selectDiary(items[0], false);
  }
});

onBeforeUnmount(() => {
  pauseAnimation();
});
</script>
