<template>
  <div class="bg-white rounded-3xl card-elevated p-6 space-y-5">
    <!-- 页面标题 -->
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <h2 class="text-xl font-bold text-gray-900">旅游日记</h2>
        <p class="text-sm text-gray-500 mt-1">
          浏览他人的路线心得，也可以登录后写下自己的城市散步记录。
        </p>
      </div>
      <button class="btn-soft-primary text-sm" @click="openComposer">
        {{ showComposer ? "收起发布区" : "发布日记" }}
      </button>
    </div>

    <!-- 发布日记区域 -->
    <section v-if="showComposer" class="card-elevated p-5 space-y-4">
      <div class="flex items-center justify-between gap-3">
        <h3 class="text-base font-bold text-gray-900">写一篇新的游记</h3>
        <span class="text-xs text-gray-400">封面图会优先加载真实图源，失败时回落到地图实景。</span>
      </div>
      <form class="flex flex-wrap gap-3" @submit.prevent="publishDiary">
        <select v-model="draft.destination_name" class="soft-control flex-1 min-w-40">
          <option v-for="item in destinations" :key="item.source_id" :value="item.name">
            {{ item.name }}
          </option>
        </select>
        <input v-model="draft.title" class="soft-control flex-1 min-w-48" placeholder="标题" />
        <textarea
          v-model="draft.content"
          class="soft-control w-full min-h-32"
          placeholder="写下你的游览体验、路线建议或踩坑提醒"
        ></textarea>
        <div class="flex flex-wrap gap-3 w-full">
          <button
            class="btn-soft-secondary text-sm"
            type="button"
            :disabled="aiDrafting"
            @click="generateDiaryDraft"
          >
            {{ aiDrafting ? "正在写..." : "AI帮写日记" }}
          </button>
          <button
            class="btn-soft-secondary text-sm"
            type="button"
            :disabled="aiImageGenerating || !draft.title || !draft.content"
            @click="generateCoverImage"
          >
            {{ aiImageGenerating ? "正在生图..." : "AI生成封面" }}
          </button>
        </div>
        <div v-if="aiError" class="alert-soft-error w-full">{{ aiError }}</div>
        <button class="btn-soft-primary w-full" type="submit">
          {{ publishing ? "发布中..." : "确认发布" }}
        </button>
      </form>
      <div v-if="coverPreview" class="mt-3">
        <RealImage
          :src="coverPreview.image_url"
          :alt="draft.destination_name"
          :name="draft.destination_name"
          :city="coverPreview.city"
          :latitude="coverPreview.latitude"
          :longitude="coverPreview.longitude"
          :source-url="coverPreview.source_url"
          class="w-full h-48 object-cover rounded-2xl"
        />
      </div>
    </section>

    <!-- 搜索栏 -->
    <form class="relative flex flex-wrap gap-3" @submit.prevent="search">
      <div class="relative flex-1">
        <input
          v-model="query"
          class="w-full soft-control pr-10"
          placeholder="输入关键字搜索日记"
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
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
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
      <button class="btn-soft-primary" type="submit">{{ searching ? "搜索中..." : "搜索" }}</button>
    </form>
    <div v-if="error" class="alert-soft-error">{{ error }}</div>

    <!-- 推荐日记 -->
    <section>
      <h3 class="text-base font-bold text-gray-900 mb-3">推荐日记</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <article
          v-for="item in diaries"
          :key="item.id"
          class="card-elevated p-4 cursor-pointer glow-border"
          :class="{ 'ring-2 ring-primary-300': selected?.id === item.id }"
          @click="store.selectDiary(item)"
        >
          <RealImage
            :src="item.media_urls?.[0]"
            :alt="item.title"
            :name="item.destination_name || item.title"
            :city="item.city"
            :search-hint="item.destination_name"
            class="w-full h-36 object-cover rounded-xl mb-3"
          />
          <h4 class="text-sm font-bold text-gray-900">{{ item.title }}</h4>
          <p class="text-xs text-gray-500 mt-1">{{ item.destination_name }}</p>
          <p class="text-xs text-gray-400 mt-0.5">作者 {{ item.author_name || "匿名旅行者" }}</p>
        </article>
      </div>
    </section>

    <!-- 搜索结果 -->
    <section>
      <h3 class="text-base font-bold text-gray-900 mb-3">搜索结果</h3>
      <div v-if="searching" class="card-elevated p-4 text-sm text-gray-500">正在搜索日记...</div>
      <div v-else-if="searchResults.length === 0" class="card-elevated p-4 text-sm text-gray-500">
        输入关键字后，这里会显示匹配到的日记。
      </div>
      <div v-else class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <article
          v-for="item in searchResults"
          :key="`search-${item.id}`"
          class="card-elevated p-4 cursor-pointer glow-border"
          :class="{ 'ring-2 ring-primary-300': selected?.id === item.id }"
          @click="store.selectDiary(item)"
        >
          <h4 class="text-sm font-bold text-gray-900">{{ item.title }}</h4>
          <p class="text-xs text-gray-500 mt-1">{{ item.destination_name }}</p>
          <p class="text-xs text-gray-400 mt-0.5">浏览 {{ item.views }} · 评分 {{ item.rating }}</p>
        </article>
      </div>
    </section>

    <!-- 日记详情 -->
    <section v-if="selected" class="card-elevated p-5 space-y-4">
      <div class="grid lg:grid-cols-[1fr_1.2fr] gap-5">
        <RealImage
          :src="selected.media_urls?.[0]"
          :alt="selected.title"
          :name="selected.destination_name || selected.title"
          :city="selected.city"
          :search-hint="selected.destination_name"
          class="w-full h-56 object-cover rounded-2xl"
        />
        <div class="space-y-2">
          <h3 class="text-lg font-bold text-gray-900">{{ selected.title }}</h3>
          <p class="text-sm text-gray-500">{{ selected.destination_name }}</p>
          <p class="text-xs text-gray-400">
            作者：{{ selected.author_name || "匿名旅行者" }} · 发布于
            {{ selected.created_at || "演示数据" }}
          </p>
          <div class="flex flex-wrap gap-2">
            <span class="stat-pill">浏览 {{ selected.views }}</span>
            <span class="stat-pill">评分 {{ selected.rating }}</span>
          </div>
          <p class="text-sm text-gray-600">{{ selected.content }}</p>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex flex-wrap gap-2">
        <button class="btn-soft-primary text-sm" @click="compress">压缩正文演示</button>
        <button
          class="btn-soft-primary text-sm"
          @click="decompress"
          :disabled="!compressionPayload"
        >
          解压回放
        </button>
        <button class="btn-soft-primary text-sm" @click="addView">手动+1浏览</button>
        <button class="btn-soft-primary text-sm" @click="rateDiary(4.0)">评分 4.0</button>
        <button class="btn-soft-primary text-sm" @click="rateDiary(5.0)">评分 5.0</button>
        <button class="btn-soft-primary text-sm" @click="generateAnimation">
          {{ animationLoading ? "生成中..." : "生成AIGC动画" }}
        </button>
        <button
          class="btn-soft-secondary text-sm"
          @click="playAnimation"
          :disabled="!animationResult?.shots?.length"
        >
          播放预览
        </button>
        <button
          class="btn-soft-secondary text-sm"
          @click="pauseAnimation"
          :disabled="!animationResult?.shots?.length"
        >
          暂停预览
        </button>
      </div>

      <pre
        v-if="compressionResult"
        class="text-xs text-gray-600 bg-gray-50 p-3 rounded-xl overflow-auto"
        >{{ compressionResult }}</pre
      >
      <pre
        v-if="decompressedContent"
        class="text-xs text-gray-600 bg-gray-50 p-3 rounded-xl overflow-auto"
      >
解压结果:\n{{ decompressedContent }}</pre
      >

      <!-- AIGC 动画 -->
      <section v-if="animationResult" class="space-y-3">
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-base font-bold text-gray-900">AIGC 旅游动画脚本</h3>
          <span class="text-xs text-gray-400">
            {{ animationResult.generation_mode }} · 总时长
            {{ animationResult.total_duration_seconds }} 秒
          </span>
        </div>

        <div v-if="activeShot" class="relative rounded-2xl overflow-hidden">
          <RealImage
            :src="activeShot.media_url || selected.media_urls?.[0]"
            :alt="activeShot.caption"
            :name="selected.destination_name || selected.title"
            :city="selected.city"
            :search-hint="selected.destination_name"
            class="w-full h-48 object-cover"
          />
          <div
            class="absolute inset-x-0 bottom-0 p-4 rounded-b-2xl"
            style="background: rgba(79, 70, 229, 0.72); backdrop-filter: blur(10px)"
          >
            <strong class="text-sm font-bold text-white">第 {{ activeShot.index }} 镜</strong>
            <p class="text-xs text-gray-200 mt-1">{{ activeShot.caption }}</p>
            <p class="text-xs text-gray-300 mt-0.5">
              {{ activeShot.transition }} · {{ activeShot.duration_seconds }} 秒
            </p>
          </div>
        </div>

        <p class="text-sm text-gray-600">
          <strong>旁白串联：</strong>{{ animationResult.narration_script }}
        </p>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <article
            v-for="shot in animationResult.shots"
            :key="`shot-${shot.index}`"
            class="card-elevated p-3 cursor-pointer"
            :class="{ 'ring-2 ring-primary-300': activeShot?.index === shot.index }"
            @click="activeShotIndex = shot.index - 1"
          >
            <h4 class="text-sm font-bold text-gray-900">镜头 {{ shot.index }}</h4>
            <p class="text-xs text-gray-500 mt-1 line-clamp-2">{{ shot.caption }}</p>
            <p class="text-xs text-gray-400 mt-0.5">
              {{ shot.transition }} · {{ shot.duration_seconds }} 秒
            </p>
          </article>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";

import { api } from "../api/client";
import RealImage from "../components/RealImage.vue";
import { useAuthStore } from "../stores/auth";
import { useTravelStore } from "../stores/travel";
import type { DiaryDraftResponse, ImageGenerateResponse } from "../types/api";
import { resolveRealMedia } from "../utils/realMedia";

const store = useTravelStore();
const auth = useAuthStore();
const diaries = computed(() => store.diaries.items);
const selected = computed(() => store.diaries.selected);
const error = computed(() => store.diaries.error);
const searchResults = computed(() => store.diarySearchResults.items);
const searching = computed(() => store.diarySearchResults.loading);
const destinations = computed(() => store.destinations.items);
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
const history = ref<string[]>(JSON.parse(localStorage.getItem(historyKey) || "[]"));
const historyItems = computed(() => {
  if (!query.value.trim()) return history.value.slice(0, 8);
  const q = query.value.toLowerCase();
  return history.value.filter((item) => item.toLowerCase().includes(q)).slice(0, 6);
});
const suggestionItems = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return [];
  const titles = diaries.value.map((d) => d.title).filter(Boolean);
  const destinations = diaries.value.map((d) => d.destination_name).filter(Boolean);
  const all = [...titles, ...destinations];
  return [...new Set(all.filter((item) => item.toLowerCase().includes(q)))].slice(0, 6);
});
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
const saveToHistory = (q: string) => {
  const exists = history.value.indexOf(q);
  if (exists !== -1) history.value.splice(exists, 1);
  history.value.unshift(q);
  history.value = history.value.slice(0, 10);
  localStorage.setItem(historyKey, JSON.stringify(history.value));
};
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
type ApiFailure = {
  response?: {
    data?: {
      detail?: string;
    };
  };
};
const apiErrorDetail = (error: unknown, fallback: string) =>
  (error as ApiFailure)?.response?.data?.detail || fallback;
const animationResult = ref<DiaryAnimationResult | null>(null);
const animationLoading = ref(false);
const activeShotIndex = ref(0);
let animationTimer: number | null = null;
const draft = reactive({
  destination_name: "",
  title: "",
  content: "",
});

const draftCover = computed(
  () => destinations.value.find((item) => item.name === draft.destination_name) ?? null,
);
const coverPreview = computed(() => {
  if (generatedCoverUrl.value) {
    return {
      image_url: generatedCoverUrl.value,
      city: draftCover.value?.city,
      latitude: draftCover.value?.latitude,
      longitude: draftCover.value?.longitude,
      source_url: generatedCoverUrl.value,
    };
  }
  return draftCover.value;
});
const activeShot = computed(() => animationResult.value?.shots?.[activeShotIndex.value] ?? null);

const search = async () => {
  const q = query.value.trim();
  if (q) saveToHistory(q);
  await store.searchDiaries(q);
};

const compress = async () => {
  if (!selected.value) return;
  const { data } = await api.post("/diaries/compress", { content: selected.value.content });
  compressionPayload.value = { encoded: data.encoded, codes: data.codes };
  decompressedContent.value = "";
  compressionResult.value = JSON.stringify(data, null, 2);
};

const decompress = async () => {
  if (!compressionPayload.value) return;
  const { data } = await api.post("/diaries/decompress", compressionPayload.value);
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
    const { data } = await api.post(`/diaries/${selected.value.id}/aigc-animation`);
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

const openComposer = async () => {
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
    aiError.value = apiErrorDetail(draftError, "AI日记生成失败，请检查百炼配置。");
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
    aiError.value = apiErrorDetail(imageError, "AI封面生成失败，请检查百炼配置。");
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
    const coverImage = draftCover.value
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
    const finalCoverImage = generatedCoverUrl.value || coverImage || draftCover.value?.image_url;
    await api.post("/diaries", {
      destination_name: draft.destination_name,
      title: draft.title,
      content: draft.content,
      cover_image_url: finalCoverImage,
      media_urls: finalCoverImage
        ? [finalCoverImage]
        : draftCover.value?.image_url
          ? [draftCover.value.image_url]
          : [],
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

onBeforeUnmount(() => {
  pauseAnimation();
});
</script>
