<template>
  <article
    class="diary-card"
    :class="[{ 'diary-card-compact': variant === 'search' }, { 'diary-card-active': active }]"
    @click="$emit('select', diary)"
  >
    <RealImage
      v-if="variant !== 'search'"
      :src="diary.media_urls?.[0]"
      :alt="diary.title"
      :name="diary.destination_name || diary.title"
      :search-hint="diary.destination_name"
      class="w-full h-40 object-cover rounded-[18px] bg-slate-100"
    />
    <div class="space-y-3" :class="{ 'mt-4': variant !== 'search' }">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <h4 class="text-base font-bold text-slate-900 line-clamp-1">{{ diary.title }}</h4>
          <p class="text-sm text-slate-500 mt-1">{{ diary.destination_name }}</p>
        </div>
        <span v-if="variant === 'search'" class="diary-meta-pill diary-meta-pill-accent">匹配</span>
        <span v-else class="diary-meta-pill">{{ diary.rating.toFixed(1) }}</span>
      </div>
      <p class="text-sm text-slate-400 line-clamp-2">{{ diary.content }}</p>
      <div class="flex flex-wrap gap-2">
        <span class="home-score-pill">浏览 {{ diary.views }}</span>
        <span v-if="variant === 'search'" class="home-heat-pill">评分 {{ diary.rating.toFixed(1) }}</span>
        <span v-else class="home-heat-pill">作者 {{ diary.author_name || "匿名旅行者" }}</span>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import RealImage from "../../../components/RealImage.vue";
import type { Diary } from "../types/diary";

withDefaults(
  defineProps<{
    diary: Diary;
    variant?: "recommend" | "search";
    active?: boolean;
  }>(),
  {
    variant: "recommend",
    active: false,
  },
);

defineEmits<{
  (e: "select", diary: Diary): void;
}>();
</script>
