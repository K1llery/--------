<template>
  <section class="diary-aigc-panel space-y-4">
    <div class="flex items-start justify-between gap-3 flex-wrap">
      <div>
        <h2 class="text-base font-bold text-slate-900">AI 旅行分镜预览</h2>
        <p class="text-xs text-slate-500 mt-1">
          根据日记自动拆解镜头脚本与旁白，仅作为静态分镜预览，不生成真实视频。
        </p>
      </div>
      <button
        class="btn-soft-primary text-sm"
        :disabled="loading"
        @click="generate"
      >
        {{ loading ? "生成中..." : result ? "重新生成分镜" : "生成 AI 分镜" }}
      </button>
    </div>

    <div v-if="error" class="alert-soft-error">{{ error }}</div>

    <template v-if="result">
      <div class="diary-aigc-hero">
        <RealImage
          :src="activeShot?.media_url || fallbackImage"
          :alt="activeShot?.caption || subject"
          :name="subject"
          :search-hint="subject"
          class="w-full h-56 object-cover bg-slate-100"
        />
        <div v-if="activeShot" class="diary-aigc-hero-overlay">
          <span class="diary-aigc-pill">镜头 {{ activeShot.index }}</span>
          <p class="diary-aigc-caption">{{ activeShot.caption }}</p>
          <span class="diary-aigc-meta">
            转场：{{ activeShot.transition }} · {{ activeShot.duration_seconds }} 秒
          </span>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button
          class="btn-soft-secondary text-sm"
          :disabled="!result.shots.length"
          @click="togglePlay"
        >
          {{ playing ? "暂停预览" : "播放分镜预览" }}
        </button>
        <span class="text-xs text-slate-400">
          {{ result.generation_mode }} · 共 {{ result.shots.length }} 镜，总时长 {{ result.total_duration_seconds }} 秒
        </span>
      </div>

      <p v-if="result.narration_script" class="text-sm text-slate-600 leading-7">
        <strong class="text-slate-900">AI 旁白脚本：</strong>{{ result.narration_script }}
      </p>

      <div class="diary-aigc-timeline" aria-label="AI 分镜时间轴">
        <button
          v-for="(shot, idx) in result.shots"
          :key="`timeline-${shot.index}`"
          type="button"
          :class="{ 'diary-aigc-timeline-active': activeIndex === idx }"
          :style="{ flexGrow: Math.max(1, shot.duration_seconds) }"
          @click="setActive(idx)"
        >
          <span>{{ shot.start_second }}s</span>
          <strong>{{ shot.duration_seconds }}s</strong>
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <article
          v-for="(shot, idx) in result.shots"
          :key="shot.index"
          class="diary-aigc-shot"
          :class="{ 'diary-aigc-shot-active': activeIndex === idx }"
          @click="setActive(idx)"
        >
          <RealImage
            :src="shot.media_url || fallbackImage"
            :alt="shot.caption"
            :name="subject"
            :search-hint="subject"
            class="diary-aigc-shot-image"
          />
          <div class="diary-aigc-shot-body">
            <div class="flex items-center justify-between gap-2">
              <h4 class="text-sm font-bold text-slate-900">镜头 {{ shot.index }}</h4>
              <span class="text-xs text-slate-400">{{ shot.duration_seconds }}s</span>
            </div>
            <p class="text-xs text-slate-500 mt-1 line-clamp-2">{{ shot.caption }}</p>
            <span class="text-xs text-slate-400 mt-1 block">转场：{{ shot.transition }}</span>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";

import RealImage from "../../../components/RealImage.vue";
import { generateDiaryAnimation } from "../api/diaryApi";
import type { DiaryAnimationResult } from "../types/diary";

const props = withDefaults(
  defineProps<{
    diaryId: number;
    subject?: string;
    fallbackImage?: string;
  }>(),
  {
    subject: "旅行日记",
    fallbackImage: "",
  },
);

const result = ref<DiaryAnimationResult | null>(null);
const loading = ref(false);
const error = ref("");
const activeIndex = ref(0);
const playing = ref(false);
let timer: number | null = null;

const activeShot = computed(() => result.value?.shots[activeIndex.value] ?? null);

const stop = () => {
  if (timer !== null) {
    window.clearInterval(timer);
    timer = null;
  }
  playing.value = false;
};

const play = () => {
  const shots = result.value?.shots;
  if (!shots?.length) return;
  stop();
  timer = window.setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % shots.length;
  }, 2200);
  playing.value = true;
};

const togglePlay = () => {
  if (playing.value) stop();
  else play();
};

const setActive = (idx: number) => {
  activeIndex.value = idx;
  stop();
};

const generate = async () => {
  stop();
  loading.value = true;
  error.value = "";
  try {
    result.value = await generateDiaryAnimation(props.diaryId);
    activeIndex.value = 0;
    play();
  } catch {
    error.value = "AI 分镜生成失败，请稍后再试";
    result.value = null;
  } finally {
    loading.value = false;
  }
};

watch(
  () => props.diaryId,
  () => {
    stop();
    result.value = null;
    activeIndex.value = 0;
  },
);

onBeforeUnmount(stop);
</script>

<style scoped>
.diary-aigc-hero {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
}

.diary-aigc-hero-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 14px 18px;
  background: linear-gradient(to top, rgba(15, 23, 42, 0.85), transparent);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.diary-aigc-pill {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 11px;
  font-weight: 600;
  width: fit-content;
}

.diary-aigc-caption {
  font-size: 14px;
  color: white;
  line-height: 1.5;
}

.diary-aigc-meta {
  font-size: 11px;
  color: rgb(203 213 225);
}

.diary-aigc-shot {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 14px;
  background: rgb(248 250 252);
  border: 1px solid rgb(226 232 240);
  cursor: pointer;
  transition: border-color 120ms ease, background 120ms ease;
}

.diary-aigc-shot:hover {
  border-color: rgb(148 163 184);
}

.diary-aigc-shot-active {
  border-color: rgb(59 130 246);
  background: rgb(239 246 255);
}

.diary-aigc-shot-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 12px;
  background: rgb(241 245 249);
  flex-shrink: 0;
}

.diary-aigc-shot-body {
  min-width: 0;
  flex: 1;
}

.diary-aigc-timeline {
  display: flex;
  gap: 6px;
  min-height: 54px;
  padding: 8px;
  border: 1px solid rgba(186, 216, 241, 0.95);
  border-radius: 18px;
  background: #f7fbff;
}

.diary-aigc-timeline button {
  display: flex;
  min-width: 54px;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
  border: 1px solid transparent;
  border-radius: 12px;
  color: #64748b;
  background: #ffffff;
  font-size: 11px;
  font-weight: 700;
  transition:
    background-color 0.16s ease,
    border-color 0.16s ease,
    color 0.16s ease;
}

.diary-aigc-timeline strong {
  color: #172331;
}

.diary-aigc-timeline button:hover,
.diary-aigc-timeline-active {
  border-color: #1475c4 !important;
  color: #1475c4 !important;
  background: #e8f4ff !important;
}

@media (max-width: 640px) {
  .diary-aigc-timeline {
    overflow-x: auto;
  }

  .diary-aigc-timeline button {
    flex: 0 0 72px !important;
  }
}
</style>
