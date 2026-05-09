<template>
  <section class="results-section">
    <div class="section-top compact">
      <h3>分段导航</h3>
      <span class="toolbar-hint">点击任意段可在地图上聚焦</span>
    </div>
    <ol ref="listRef" class="timeline-list">
      <li
        v-for="(segment, i) in segments"
        :key="`seg-${segment.index}-${segment.from_code}`"
        class="timeline-item"
        :class="{ 'timeline-item--active': activeIndex === i }"
        @click="emit('select-segment', i)"
      >
        <span class="timeline-index" :class="{ 'timeline-index--active': activeIndex === i }">
          {{ segment.index }}
        </span>
        <div class="timeline-content">
          <strong>{{ segment.from_name }} → {{ segment.to_name }}</strong>
          <Transition name="page-fade-slide">
            <div v-if="activeIndex === i" class="timeline-detail">
              <p>{{ segment.instruction }}</p>
              <div class="timeline-meta">
                <span class="stat-pill">{{ segment.distance_m }} 米</span>
                <span class="stat-pill">{{ segment.estimated_minutes }} 分钟</span>
                <span class="stat-pill">累计 {{ segment.cumulative_distance_m }} 米</span>
              </div>
              <div v-if="segment.congestion >= 0.8" class="congestion-warn">
                人流较大，建议放慢节奏
              </div>
            </div>
          </Transition>
          <p v-if="activeIndex !== i" class="timeline-meta-compact">
            {{ segment.distance_m }} 米 · {{ segment.estimated_minutes }} 分钟
          </p>
        </div>
      </li>
    </ol>
  </section>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue";

import type { RouteSegment } from "../../types/models";

const props = defineProps<{
  segments: RouteSegment[];
  activeIndex: number | null;
}>();

const emit = defineEmits<{
  "select-segment": [index: number];
}>();

const listRef = ref<HTMLElement | null>(null);

watch(
  () => props.activeIndex,
  async (idx) => {
    if (idx === null || !listRef.value) return;
    await nextTick();
    const items = listRef.value.querySelectorAll(".timeline-item");
    items[idx]?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  },
);
</script>
