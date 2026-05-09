<template>
  <section class="results-section">
    <div class="section-top compact">
      <h3>备选路线</h3>
      <span class="toolbar-hint">悬停卡片可在地图上预览</span>
    </div>
    <div class="card-grid compact-grid">
      <article
        v-for="(item, i) in alternatives"
        :key="item.strategy"
        class="item-card"
        :class="{ selected: selectedStrategy === item.strategy }"
        @click="emit('select', item.strategy)"
        @mouseenter="emit('hover', i)"
        @mouseleave="emit('hover', null)"
      >
        <div class="alt-card-header">
          <span class="alt-color-dot" :style="{ background: altColors[i % altColors.length] }"></span>
          <h3>{{ item.strategy_label }}</h3>
        </div>
        <p>{{ item.total_distance_m }} m · {{ item.estimated_minutes }} 分钟</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { SingleRouteResult } from "../../types/models";

defineProps<{
  alternatives: SingleRouteResult[];
  selectedStrategy: string;
}>();

const emit = defineEmits<{
  select: [strategy: string];
  hover: [index: number | null];
}>();

const altColors = ["#4f8cf7", "#34a853", "#ea4335", "#fbbc04"];
</script>
