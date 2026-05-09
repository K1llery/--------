<template>
  <section v-if="buildings.length" class="card-elevated p-5 space-y-4">
    <div class="flex items-center justify-between gap-3">
      <h3 class="text-base font-bold text-gray-900">室内导航模拟</h3>
      <span class="text-xs text-gray-400">支持大门到电梯、跨层换乘和楼层内房间导航</span>
    </div>

    <form class="flex flex-wrap gap-3" @submit.prevent="handlePlanRoute">
      <select v-model="indoor.selectedBuildingCode.value" class="soft-control flex-1 min-w-36">
        <option
          v-for="building in buildings"
          :key="building.building_code"
          :value="building.building_code"
        >
          {{ building.building_name }}
        </option>
      </select>
      <select v-model="indoor.startNodeCode.value" class="soft-control flex-1 min-w-36">
        <option v-for="node in nodeOptions" :key="`indoor-start-${node.code}`" :value="node.code">
          {{ node.name }}（{{ node.floor }}层）
        </option>
      </select>
      <select v-model="indoor.endNodeCode.value" class="soft-control flex-1 min-w-36">
        <option v-for="node in nodeOptions" :key="`indoor-end-${node.code}`" :value="node.code">
          {{ node.name }}（{{ node.floor }}层）
        </option>
      </select>
      <select v-model="indoor.strategy.value" class="soft-control flex-1 min-w-28">
        <option value="time">最快通过</option>
        <option value="distance">最短距离</option>
        <option value="accessible">无障碍优先</option>
      </select>
      <select v-model="indoor.mobilityMode.value" class="soft-control flex-1 min-w-28">
        <option value="normal">常规通行</option>
        <option value="wheelchair">轮椅通行</option>
      </select>
      <button class="btn-soft-primary" type="submit">
        {{ indoor.indoorLoading.value ? "规划中..." : "规划室内路径" }}
      </button>
    </form>

    <div v-if="indoor.indoorRoute.value" class="space-y-3">
      <p class="text-sm text-gray-600">{{ indoor.indoorRoute.value.summary }}</p>
      <div class="flex flex-wrap gap-2">
        <span class="stat-pill">{{ indoor.indoorRoute.value.total_distance_m }} m</span>
        <span class="stat-pill">{{ indoor.indoorRoute.value.estimated_seconds }} 秒</span>
        <span class="stat-pill">{{
          indoor.indoorRoute.value.mobility_mode === "wheelchair" ? "轮椅模式" : "常规模式"
        }}</span>
      </div>
      <ol class="timeline-list">
        <li
          v-for="step in indoor.indoorRoute.value.steps"
          :key="`indoor-step-${step.index}`"
          class="timeline-item !bg-gray-50"
        >
          <span class="timeline-index">{{ step.index }}</span>
          <div class="timeline-content">
            <strong class="text-sm font-bold text-gray-900">
              {{ step.from_name }}（{{ step.from_floor }}层） → {{ step.to_name }}（{{
                step.to_floor
              }}层）
            </strong>
            <p class="text-xs text-gray-500 mt-0.5">{{ step.instruction }}</p>
            <p class="text-xs text-gray-400 mt-0.5">
              {{ step.distance_m }} 米 · {{ step.estimated_seconds }} 秒 · {{ step.connector }}
            </p>
          </div>
        </li>
      </ol>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";

import { useIndoorNavigation } from "../../composables/useIndoorNavigation";
import type { IndoorBuilding, IndoorNode } from "../../types/models";

const props = defineProps<{
  buildings: IndoorBuilding[];
}>();

const emit = defineEmits<{
  "route-error": [message: string];
}>();

const indoor = useIndoorNavigation();

const activeBuilding = computed(() => {
  if (!props.buildings.length) return null;
  return (
    props.buildings.find((item) => item.building_code === indoor.selectedBuildingCode.value) ??
    props.buildings[0]
  );
});

const nodeOptions = computed<IndoorNode[]>(() => activeBuilding.value?.nodes ?? []);

const syncDefaults = () => {
  indoor.selectedBuildingCode.value = props.buildings[0]?.building_code ?? "";
  indoor.startNodeCode.value = nodeOptions.value[0]?.code ?? "";
  indoor.endNodeCode.value = nodeOptions.value[1]?.code ?? indoor.startNodeCode.value;
  indoor.reset();
};

watch(() => props.buildings, syncDefaults, { immediate: true });

watch(indoor.selectedBuildingCode, () => {
  indoor.startNodeCode.value = nodeOptions.value[0]?.code ?? "";
  indoor.endNodeCode.value = nodeOptions.value[1]?.code ?? indoor.startNodeCode.value;
  indoor.reset();
});

const handlePlanRoute = async () => {
  const errorMsg = await indoor.planRoute();
  if (errorMsg) emit("route-error", errorMsg);
};

defineExpose({
  reset: indoor.reset,
});
</script>
