<template>
  <Transition name="page-fade-slide">
    <div v-if="totalSegments > 0" class="segment-nav-bar">
      <button
        class="secondary-btn"
        type="button"
        :disabled="currentIndex <= 0"
        @click="emit('prev')"
      >
        ← 上一段
      </button>
      <div class="segment-nav-progress">
        <span v-if="currentIndex >= 0">
          第 {{ currentIndex + 1 }} / {{ totalSegments }} 段
        </span>
        <span v-else>点击分段开始导航</span>
        <div class="segment-progress-bar">
          <div
            class="segment-progress-fill"
            :style="{ width: progressPercent + '%' }"
          ></div>
        </div>
      </div>
      <button
        class="secondary-btn"
        type="button"
        :disabled="currentIndex >= totalSegments - 1"
        @click="emit('next')"
      >
        下一段 →
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  currentIndex: number;
  totalSegments: number;
}>();

const emit = defineEmits<{
  prev: [];
  next: [];
  "exit-navigation": [];
}>();

const progressPercent = computed(() => {
  if (props.currentIndex < 0 || props.totalSegments === 0) return 0;
  return ((props.currentIndex + 1) / props.totalSegments) * 100;
});
</script>
