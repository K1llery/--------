<template>
  <section class="panel-card">
    <div class="section-top">
      <div>
        <h2>旅游日记</h2>
        <p>浏览他人的路线心得，也可以登录后写下自己的城市散步记录。</p>
      </div>
      <button class="primary-btn" @click="openComposer">
        {{ showComposer ? "收起发布区" : "发布日记" }}
      </button>
    </div>

    <section v-if="showComposer" class="status-card">
      <div class="section-top compact">
        <h3>写一篇新的游记</h3>
        <span class="toolbar-hint">封面图会优先加载真实图源，失败时回落到地图实景。</span>
      </div>
      <form class="search-form" @submit.prevent="publishDiary">
        <select v-model="draft.destination_name" class="select-input">
          <option v-for="item in destinations" :key="item.source_id" :value="item.name">
            {{ item.name }}
          </option>
        </select>
        <input v-model="draft.title" placeholder="标题" />
        <textarea
          v-model="draft.content"
          class="text-area"
          placeholder="写下你的游览体验、路线建议或踩坑提醒"
        ></textarea>
        <div class="hero-actions ai-compose-actions">
          <button
            class="secondary-btn"
            type="button"
            :disabled="aiDrafting"
            @click="generateDiaryDraft"
          >
            {{ aiDrafting ? "正在写..." : "AI帮写日记" }}
          </button>
          <button
            class="secondary-btn"
            type="button"
            :disabled="aiImageGenerating || !draft.title || !draft.content"
            @click="generateCoverImage"
          >
            {{ aiImageGenerating ? "正在生图..." : "AI生成封面" }}
          </button>
        </div>
        <div v-if="aiError" class="status-card error-card">{{ aiError }}</div>
        <button class="primary-btn" type="submit">
          {{ publishing ? "发布中..." : "确认发布" }}
        </button>
      </form>
      <div v-if="coverPreview" class="draft-cover">
        <RealImage
          :src="coverPreview.image_url"
          :alt="draft.destination_name"
          :name="draft.destination_name"
          :city="coverPreview.city"
          :latitude="coverPreview.latitude"
          :longitude="coverPreview.longitude"
          :source-url="coverPreview.source_url"
          class="detail-image"
        />
      </div>
    </section>

    <form class="search-form" @submit.prevent="search">
      <input v-model="query" placeholder="输入关键字搜索日记" />
      <button class="primary-btn" type="submit">{{ searching ? "搜索中..." : "搜索" }}</button>
    </form>
    <div v-if="error" class="status-card error-card">{{ error }}</div>

    <section>
      <h3 class="section-title">推荐日记</h3>
      <div class="card-grid">
        <article
          v-for="item in diaries"
          :key="item.id"
          class="item-card media-card"
          :class="{ selected: selected?.id === item.id }"
          @click="store.selectDiary(item)"
        >
          <RealImage
            :src="item.media_urls?.[0]"
            :alt="item.title"
            :name="item.destination_name || item.title"
            :city="item.city"
            :search-hint="item.destination_name"
            class="media-thumb"
          />
          <div class="media-body">
            <h3>{{ item.title }}</h3>
            <p>{{ item.destination_name }}</p>
            <p>作者 {{ item.author_name || "匿名旅行者" }}</p>
          </div>
        </article>
      </div>
    </section>

    <section>
      <h3 class="section-title">搜索结果</h3>
      <div v-if="searching" class="status-card">正在搜索日记...</div>
      <div v-else-if="searchResults.length === 0" class="status-card">
        输入关键字后，这里会显示匹配到的日记。
      </div>
      <div v-else class="card-grid">
        <article
          v-for="item in searchResults"
          :key="`search-${item.id}`"
          class="item-card"
          :class="{ selected: selected?.id === item.id }"
          @click="store.selectDiary(item)"
        >
          <h3>{{ item.title }}</h3>
          <p>{{ item.destination_name }}</p>
          <p>浏览 {{ item.views }} · 评分 {{ item.rating }}</p>
        </article>
      </div>
    </section>

    <section v-if="selected" class="detail-panel detail-stack">
      <RealImage
        :src="selected.media_urls?.[0]"
        :alt="selected.title"
        :name="selected.destination_name || selected.title"
        :city="selected.city"
        :search-hint="selected.destination_name"
        class="detail-image"
      />
      <div>
        <h3>{{ selected.title }}</h3>
        <p>{{ selected.destination_name }}</p>
        <p>
          作者：{{ selected.author_name || "匿名旅行者" }} · 发布于
          {{ selected.created_at || "演示数据" }}
        </p>
        <div class="detail-stats">
          <span class="stat-pill">浏览 {{ selected.views }}</span>
          <span class="stat-pill">评分 {{ selected.rating }}</span>
        </div>
        <p>{{ selected.content }}</p>
        <div class="hero-actions">
          <button class="primary-btn" @click="compress">压缩正文演示</button>
          <button class="primary-btn" @click="decompress" :disabled="!compressionPayload">
            解压回放
          </button>
          <button class="primary-btn" @click="addView">手动+1浏览</button>
          <button class="primary-btn" @click="rateDiary(4.0)">评分 4.0</button>
          <button class="primary-btn" @click="rateDiary(5.0)">评分 5.0</button>
          <button class="primary-btn" @click="generateAnimation">
            {{ animationLoading ? "生成中..." : "生成AIGC动画" }}
          </button>
          <button
            class="secondary-btn"
            @click="playAnimation"
            :disabled="!animationResult?.shots?.length"
          >
            播放预览
          </button>
          <button
            class="secondary-btn"
            @click="pauseAnimation"
            :disabled="!animationResult?.shots?.length"
          >
            暂停预览
          </button>
        </div>
        <pre v-if="compressionResult">{{ compressionResult }}</pre>
        <pre v-if="decompressedContent">解压结果:\n{{ decompressedContent }}</pre>

        <section v-if="animationResult" class="aigc-panel">
          <div class="section-top compact">
            <h3>AIGC 旅游动画脚本</h3>
            <span class="toolbar-hint"
              >{{ animationResult.generation_mode }} · 总时长
              {{ animationResult.total_duration_seconds }} 秒</span
            >
          </div>

          <div v-if="activeShot" class="aigc-preview">
            <RealImage
              :src="activeShot.media_url || selected.media_urls?.[0]"
              :alt="activeShot.caption"
              :name="selected.destination_name || selected.title"
              :city="selected.city"
              :search-hint="selected.destination_name"
              class="detail-image"
            />
            <div class="aigc-overlay">
              <strong>第 {{ activeShot.index }} 镜</strong>
              <p>{{ activeShot.caption }}</p>
              <p class="timeline-meta">
                {{ activeShot.transition }} · {{ activeShot.duration_seconds }} 秒
              </p>
            </div>
          </div>

          <p><strong>旁白串联：</strong>{{ animationResult.narration_script }}</p>
          <div class="card-grid compact-grid">
            <article
              v-for="shot in animationResult.shots"
              :key="`shot-${shot.index}`"
              class="item-card"
              :class="{ selected: activeShot?.index === shot.index }"
              @click="activeShotIndex = shot.index - 1"
            >
              <h3>镜头 {{ shot.index }}</h3>
              <p>{{ shot.caption }}</p>
              <p class="timeline-meta">{{ shot.transition }} · {{ shot.duration_seconds }} 秒</p>
            </article>
          </div>
        </section>
      </div>
    </section>
  </section>
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
  await store.searchDiaries(query.value);
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
