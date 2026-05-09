<template>
  <div class="route-trip-bar">
    <div class="trip-route-line">
      <span class="trip-origin">{{ originLabel }}</span>
      <template v-for="stop in stops" :key="stop.code">
        <span class="trip-arrow">→</span>
        <button
          class="trip-stop-chip"
          type="button"
          :title="`移除 ${stop.name}`"
          @click="emit('remove-stop', stop.code)"
        >
          <span>{{ stop.name }}</span>
          <span class="trip-remove">×</span>
        </button>
      </template>
      <template v-if="stops.length >= 2">
        <span class="trip-arrow">→</span>
        <span class="trip-origin">回到起点</span>
      </template>
    </div>

    <div class="trip-actions">
      <button
        class="primary-btn compact-btn"
        type="button"
        :disabled="stops.length < 2 || loading"
        @click="emit('plan-trip')"
      >
        {{ loading ? "优化中..." : stops.length < 2 ? "再添加 1 个" : "优化顺序" }}
      </button>
      <button class="secondary-btn compact-btn" type="button" @click="emit('open-multi-stop')">
        编辑
      </button>
      <button class="secondary-btn compact-btn" type="button" @click="emit('clear')">
        清空
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SceneNode } from "../../types/models";

defineProps<{
  stops: SceneNode[];
  loading: boolean;
  originLabel: string;
}>();

const emit = defineEmits<{
  "remove-stop": [code: string];
  "plan-trip": [];
  "open-multi-stop": [];
  clear: [];
}>();
</script>
