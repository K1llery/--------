<template>
  <article class="helper-card">
    <h3>出发方式</h3>
    <div class="route-start-row">
      <label class="route-toggle">
        <input
          :checked="modelValue"
          type="checkbox"
          @change="emit('update:modelValue', ($event.target as HTMLInputElement).checked)"
        />
        <span>使用当前位置自动匹配最近起点</span>
      </label>
      <button
        class="secondary-btn"
        type="button"
        :disabled="!geo.supportsGeolocation || geo.locating.value"
        @click="geo.capture()"
      >
        {{ geo.locating.value ? "定位中..." : "刷新定位" }}
      </button>
    </div>
    <p class="toolbar-hint">{{ locationMessage }}</p>
  </article>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";

import { useGeolocation } from "../../composables/useGeolocation";

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
}>();

const geo = useGeolocation();

const locationMessage = computed(() => {
  if (!geo.supportsGeolocation) return "当前浏览器不支持定位，可手动选择起点。";
  if (!props.modelValue) return "可手动选择起点，或开启当前位置自动匹配。";
  if (geo.locating.value) return "正在获取当前位置...";
  if (geo.currentLocation.value) {
    return `已定位：${geo.currentLocation.value.latitude.toFixed(5)}, ${geo.currentLocation.value.longitude.toFixed(5)}（规划时将自动匹配最近点）。`;
  }
  return '尚未定位，点击"刷新定位"后可自动匹配最近起点。';
});

watch(
  () => props.modelValue,
  async (enabled) => {
    if (enabled && !geo.currentLocation.value) {
      await geo.capture();
    }
  },
);

/** 确保定位已就绪（用于父组件在规划前调用） */
const ensureReady = async (): Promise<boolean> => {
  if (!props.modelValue) return true;
  if (geo.currentLocation.value) return true;
  await geo.capture();
  return Boolean(geo.currentLocation.value);
};

defineExpose({
  currentLocation: geo.currentLocation,
  locationPayload: () => geo.locationPayload(props.modelValue),
  ensureReady,
});
</script>
