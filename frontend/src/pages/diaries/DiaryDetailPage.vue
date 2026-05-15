<template>
  <div class="diary-detail-page space-y-6">
    <div>
      <router-link to="/diaries" class="text-sm text-slate-500 hover:text-slate-900">
        ← 返回日记列表
      </router-link>
    </div>

    <div v-if="loading" class="card-elevated rounded-[24px] p-6 text-sm text-slate-500">
      加载中...
    </div>
    <div v-else-if="error" class="alert-soft-error">{{ error }}</div>
    <article
      v-else-if="diary"
      class="card-elevated rounded-[28px] p-6 lg:p-7 space-y-6"
    >
      <header class="space-y-3">
        <div class="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <p class="home-section-kicker">旅游日记</p>
            <h1 class="text-2xl font-bold text-slate-950 mt-1">{{ diary.title }}</h1>
          </div>
          <router-link
            v-if="canEdit"
            :to="`/diaries/${diary.id}/edit`"
            class="btn-soft-secondary text-sm"
          >
            编辑
          </router-link>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <span class="route-summary-chip route-summary-chip-accent">
            {{ diary.destination_name }}
          </span>
          <span class="text-sm text-slate-500">
            作者：{{ diary.author_name || "匿名旅行者" }}
          </span>
          <span v-if="diary.created_at" class="text-sm text-slate-400">
            · {{ diary.created_at }}
          </span>
        </div>
        <div class="grid grid-cols-2 gap-3 max-w-md">
          <div class="route-metric-tile">
            <strong>{{ diary.views }}</strong>
            <span>浏览量</span>
          </div>
          <div class="route-metric-tile">
            <strong>{{ diary.rating.toFixed(1) }}</strong>
            <span>平均评分</span>
          </div>
        </div>
      </header>

      <DiaryMediaGallery
        v-if="mediaItems.length"
        :media="mediaItems"
        :subject="diary.destination_name || diary.title"
      />

      <section class="space-y-3">
        <h2 class="text-base font-bold text-slate-900">正文</h2>
        <p class="text-sm text-slate-700 leading-7 whitespace-pre-wrap">
          {{ diary.content }}
        </p>
      </section>

      <section class="space-y-3">
        <h2 class="text-base font-bold text-slate-900">为这篇日记打分</h2>
        <DiaryRatingStars
          :diary-id="diary.id"
          :average-rating="diary.rating"
          :rating-count="ratingCount"
          @rated="onRated"
        />
      </section>

      <DiaryCompressionPanel :content="diary.content" />

      <DiaryAlgorithmPanel />

      <DiaryAigcPanel
        :diary-id="diary.id"
        :subject="diary.destination_name || diary.title"
        :fallback-image="diary.media_urls?.[0] || ''"
      />
    </article>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { getDiary, incrementDiaryView } from "../../features/diary/api/diaryApi";
import DiaryAigcPanel from "../../features/diary/components/DiaryAigcPanel.vue";
import DiaryAlgorithmPanel from "../../features/diary/components/DiaryAlgorithmPanel.vue";
import DiaryCompressionPanel from "../../features/diary/components/DiaryCompressionPanel.vue";
import DiaryMediaGallery from "../../features/diary/components/DiaryMediaGallery.vue";
import DiaryRatingStars from "../../features/diary/components/DiaryRatingStars.vue";
import type { Diary } from "../../features/diary/types/diary";
import { normalizeDiaryMedia } from "../../features/diary/utils/media";
import { useAuthStore } from "../../stores/auth";

const route = useRoute();
const auth = useAuthStore();
const diary = ref<Diary | null>(null);
const loading = ref(false);
const error = ref("");
const ratingCount = ref<number | null>(null);

const mediaItems = computed(() => normalizeDiaryMedia(diary.value));

const canEdit = computed(
  () =>
    auth.isLoggedIn &&
    auth.user !== null &&
    diary.value !== null &&
    diary.value.author_id !== undefined &&
    diary.value.author_id === auth.user.id,
);

const onRated = (payload: { diary: Diary; userScore: number; ratingCount: number }) => {
  diary.value = payload.diary;
  ratingCount.value = payload.ratingCount;
};

const VIEW_LOG_KEY = "diary_view_log";

const todayStr = () => new Date().toISOString().slice(0, 10);

const reportView = async (id: number) => {
  try {
    const log = JSON.parse(localStorage.getItem(VIEW_LOG_KEY) || "{}") as Record<string, string>;
    if (log[String(id)] === todayStr()) return;
    const data = await incrementDiaryView(id);
    log[String(id)] = todayStr();
    localStorage.setItem(VIEW_LOG_KEY, JSON.stringify(log));
    if (diary.value && diary.value.id === data.diary.id) {
      diary.value = data.diary;
    }
  } catch {
    // 静默失败：浏览量上报不影响阅读
  }
};

const load = async (idParam: string | string[]) => {
  const raw = Array.isArray(idParam) ? idParam[0] : idParam;
  const id = Number(raw);
  if (!Number.isFinite(id)) {
    error.value = "无效的日记 ID";
    return;
  }
  loading.value = true;
  error.value = "";
  ratingCount.value = null;
  try {
    diary.value = await getDiary(id);
    reportView(id);
  } catch {
    error.value = "加载日记详情失败";
  } finally {
    loading.value = false;
  }
};

onMounted(() => load(route.params.id));

watch(
  () => route.params.id,
  (id) => {
    if (id) load(id);
  },
);
</script>
