<template class="space-y-5">
  <!-- 单点路线表单 -->
  <form class="flex flex-wrap gap-3" @submit.prevent="handlePlanSingle">
    <select v-model="startCode" class="soft-control flex-1 min-w-32" :disabled="disableStartSelect">
      <option v-for="node in placeOptions" :key="node.code" :value="node.code">
        {{ node.name }}
      </option>
    </select>
    <select v-model="endCode" class="soft-control flex-1 min-w-32">
      <option v-for="node in placeOptions" :key="node.code" :value="node.code">
        {{ node.name }}
      </option>
    </select>
    <button class="btn-soft-primary" type="submit">
      {{ planner.singleLoading.value ? "规划中..." : "规划单点路线" }}
    </button>
  </form>

  <!-- 单点路线结果 -->
  <div v-if="planner.singleRoute.value" class="card-elevated p-5">
    <div class="flex items-center justify-between gap-3 mb-3">
      <h3 class="text-base font-bold text-gray-900 m0">{{ planner.singleRoute.value.strategy_label }}</h3>
      <button class="btn-soft-secondary text-sm" @click="handleSaveRoute">收藏当前路线</button>
    </div>
    <p class="text-sm text-gray-500 mt-2">{{ planner.singleRoute.value.explanation }}</p>
    <p v-if="planner.singleRoute.value.resolved_start_name" class="text-xs text-gray-400 mt-1">
      实际起点：{{ planner.singleRoute.value.resolved_start_name }}
    </p>
    <div class="flex flex-wrap gap-2 mt-3">
      <span class="stat-pill">{{ planner.singleRoute.value.total_distance_m }} m</span>
      <span class="stat-pill">{{ planner.singleRoute.value.estimated_minutes }} 分钟</span>
      <span class="stat-pill">平均拥堵 {{ planner.singleRoute.value.average_congestion }}</span>
    </div>
    <p class="text-sm text-gray-600 mt-3">
      <strong>路线：</strong> {{ planner.singleRoute.value.path_names.join(" → ") }}
    </p>
  </div>

  <!-- 备选路线 -->
  <section v-if="planner.singleRoute.value?.alternatives?.length">
    <div class="flex items-center justify-between gap-3 mb-3">
      <h3 class="text-base font-bold text-gray-900">备选路线</h3>
      <span class="text-xs text-gray-400">点击卡片可切换地图高亮</span>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      <article
        v-for="item in planner.singleRoute.value.alternatives"
        :key="item.strategy"
        class="card-elevated p-4 cursor-pointer glow-border"
        :class="{ 'ring-2 ring-primary-300': planner.selectedAlternativeStrategy.value === item.strategy }"
        @click="planner.selectedAlternativeStrategy.value = item.strategy"
      >
        <h4 class="text-sm font-bold text-gray-900">{{ item.strategy_label }}</h4>
        <p class="text-xs text-gray-500 mt-1">{{ item.explanation }}</p>
        <p class="text-xs text-gray-400 mt-1">{{ item.total_distance_m }} m · {{ item.estimated_minutes }} 分钟</p>
      </article>
    </div>
  </section>

  <!-- 多点闭环表单 -->
  <form class="flex flex-wrap gap-3 items-start" @submit.prevent="handlePlanMulti">
    <select v-model="multiTargetCodes" class="soft-control flex-1 min-w-40" multiple size="4">
      <option v-for="node in placeOptions" :key="node.code" :value="node.code">
        {{ node.name }}
      </option>
    </select>
    <button class="btn-soft-primary" type="submit">
      {{ planner.multiLoading.value ? "规划中..." : "规划多点闭环" }}
    </button>
  </form>

  <!-- 多点闭环结果 -->
  <div v-if="planner.multiRoute.value" class="card-elevated p-5">
    <h3 class="text-base font-bold text-gray-900">{{ planner.multiRoute.value.optimization_label }}</h3>
    <p class="text-sm text-gray-500 mt-2">{{ planner.multiRoute.value.explanation }}</p>
    <p v-if="planner.multiRoute.value.resolved_start_name" class="text-xs text-gray-400 mt-1">
      实际起点：{{ planner.multiRoute.value.resolved_start_name }}
    </p>
    <div class="flex flex-wrap gap-2 mt-3">
      <span class="stat-pill">{{ planner.multiRoute.value.total_distance_m }} m</span>
      <span class="stat-pill">{{ planner.multiRoute.value.estimated_minutes }} 分钟</span>
      <span class="stat-pill">{{ planner.multiRoute.value.strategy_label }}</span>
    </div>
    <p class="text-sm text-gray-600 mt-3">
      <strong>闭环停靠：</strong> {{ planner.multiRoute.value.ordered_stop_names.join(" → ") }}
    </p>
  </div>

  <!-- 分段导航 -->
  <section v-if="activeSegments.length">
    <div class="flex items-center justify-between gap-3 mb-3">
      <h3 class="text-base font-bold text-gray-900">分段导航</h3>
      <span class="text-xs text-gray-400">按顺序执行即可完成整段行程</span>
    </div>
    <ol class="timeline-list">
      <li
        v-for="segment in activeSegments"
        :key="`segment-${segment.index}-${segment.from_code}-${segment.to_code}`"
        class="timeline-item !bg-gray-50"
      >
        <span class="timeline-index">{{ segment.index }}</span>
        <div class="timeline-content">
          <strong class="text-sm font-bold text-gray-900">{{ segment.from_name }} → {{ segment.to_name }}</strong>
          <p class="text-xs text-gray-500 mt-0.5">{{ segment.instruction }}</p>
          <p class="text-xs text-gray-400 mt-0.5">
            {{ segment.distance_m }} 米 · {{ segment.estimated_minutes }} 分钟 · 累计
            {{ segment.cumulative_distance_m }} 米
          </p>
        </div>
      </li>
    </ol>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

import { useRoutePlanner } from "../../composables/useRoutePlanner";
import type { RouteSegment } from "../../types/models";

const props = defineProps<{
  sceneName: string;
  placeOptions: Array<{ code: string; name: string; latitude: number; longitude: number }>;
  strategy: string;
  transportMode: string;
  disableStartSelect?: boolean;
  locationPayloadFn: () => Record<string, unknown>;
  ensureLocationReadyFn: () => Promise<boolean>;
}>();

const emit = defineEmits<{
  "route-error": [message: string];
  "save-route": [payload: Record<string, unknown>];
}>();

const planner = useRoutePlanner();
const startCode = ref("");
const endCode = ref("");
const multiTargetCodes = ref<string[]>([]);

const activeSegments = computed<RouteSegment[]>(() => {
  if (
    planner.selectedAlternativeStrategy.value &&
    planner.singleRoute.value?.alternatives?.length
  ) {
    const alt = planner.singleRoute.value.alternatives.find(
      (item) => item.strategy === planner.selectedAlternativeStrategy.value,
    );
    if (alt?.segments?.length) return alt.segments;
  }
  return planner.multiRoute.value?.segments || planner.singleRoute.value?.segments || [];
});

const syncDefaults = () => {
  startCode.value = props.placeOptions[0]?.code ?? "";
  endCode.value = props.placeOptions[1]?.code ?? startCode.value;
  multiTargetCodes.value = props.placeOptions.slice(1, 4).map((item) => item.code);
};

watch(() => props.placeOptions, syncDefaults, { immediate: true });

const handlePlanSingle = async () => {
  const ready = await props.ensureLocationReadyFn();
  if (!ready) {
    emit("route-error", "无法获取当前位置，请改为手动起点或重试定位。");
    return;
  }
  await planner.planSingle({
    scene_name: props.sceneName,
    start_code: startCode.value,
    end_code: endCode.value,
    strategy: props.strategy,
    transport_mode: props.transportMode,
    ...props.locationPayloadFn(),
  });
  if (planner.error.value) emit("route-error", planner.error.value);
};

const handlePlanMulti = async () => {
  const ready = await props.ensureLocationReadyFn();
  if (!ready) {
    emit("route-error", "无法获取当前位置，请改为手动起点或重试定位。");
    return;
  }
  await planner.planMulti({
    scene_name: props.sceneName,
    start_code: startCode.value,
    target_codes: multiTargetCodes.value,
    strategy: props.strategy,
    transport_mode: props.transportMode,
    ...props.locationPayloadFn(),
  });
  if (planner.error.value) emit("route-error", planner.error.value);
};

const handleSaveRoute = () => {
  const route =
    planner.selectedAlternativeStrategy.value && planner.singleRoute.value?.alternatives?.length
      ? planner.singleRoute.value.alternatives.find(
          (item) => item.strategy === planner.selectedAlternativeStrategy.value,
        ) || planner.singleRoute.value
      : planner.singleRoute.value;
  if (!route) return;
  emit("save-route", {
    scene_name: props.sceneName,
    strategy: route.strategy,
    transport_mode: props.transportMode,
    path_codes: route.path_codes,
    path_names: route.path_names,
    total_distance_m: route.total_distance_m,
    estimated_minutes: route.estimated_minutes,
    explanation: route.explanation,
  });
};

/** 当前活跃的导航摘要 */
const activeNavigationSummary = computed(() => {
  if (
    planner.selectedAlternativeStrategy.value &&
    planner.singleRoute.value?.alternatives?.length
  ) {
    const alt = planner.singleRoute.value.alternatives.find(
      (item) => item.strategy === planner.selectedAlternativeStrategy.value,
    );
    if (alt) return alt.navigation_summary;
  }
  return (
    planner.multiRoute.value?.navigation_summary ||
    planner.singleRoute.value?.navigation_summary ||
    ""
  );
});

/** 当前显示路径码（供地图高亮） */
const displayPathCodes = computed<string[]>(() => {
  if (
    planner.selectedAlternativeStrategy.value &&
    planner.singleRoute.value?.alternatives?.length
  ) {
    const alt = planner.singleRoute.value.alternatives.find(
      (item) => item.strategy === planner.selectedAlternativeStrategy.value,
    );
    if (alt) return alt.path_codes;
  }
  if (
    Array.isArray(planner.multiRoute.value?.path_codes) &&
    planner.multiRoute.value!.path_codes.length
  ) {
    return planner.multiRoute.value!.path_codes;
  }
  return planner.singleRoute.value?.path_codes ?? [];
});

defineExpose({
  displayPathCodes,
  activeNavigationSummary,
  reset: planner.reset,
});
</script>
