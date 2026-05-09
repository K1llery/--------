<template>
  <component
    :is="asDrawer ? 'div' : 'section'"
    v-if="(buildings.length && !asDrawer) || (asDrawer && drawerOpen)"
    :class="asDrawer ? 'route-drawer-backdrop' : 'route-summary route-card indoor-card'"
    @click.self="asDrawer && emit('close')"
  >
    <div :class="asDrawer ? 'route-drawer' : ''">
      <div :class="asDrawer ? 'drawer-header' : 'section-top compact'">
        <h3>室内导航</h3>
        <span v-if="!asDrawer" class="toolbar-hint">
          支持大门到电梯、跨层换乘、楼层内房间导航
        </span>
        <button
          v-if="asDrawer"
          class="icon-btn"
          type="button"
          aria-label="关闭"
          @click="emit('close')"
        >
          ✕
        </button>
      </div>

      <p v-if="!buildings.length" class="toolbar-hint">
        当前场景没有可用的室内建筑数据。
      </p>

      <form v-else class="search-form" @submit.prevent="handlePlanRoute">
        <label class="planner-field">
          <span>建筑</span>
          <select v-model="indoor.selectedBuildingCode.value" class="select-input">
            <option
              v-for="building in buildings"
              :key="building.building_code"
              :value="building.building_code"
            >
              {{ building.building_name }}
            </option>
          </select>
        </label>

        <label class="planner-field">
          <span>起点</span>
          <select v-model="indoor.startNodeCode.value" class="select-input">
            <option v-for="node in nodeOptions" :key="`indoor-start-${node.code}`" :value="node.code">
              {{ node.name }}（{{ node.floor }}层）
            </option>
          </select>
        </label>

        <label class="planner-field">
          <span>目的地</span>
          <select v-model="indoor.endNodeCode.value" class="select-input">
            <option v-for="node in nodeOptions" :key="`indoor-end-${node.code}`" :value="node.code">
              {{ node.name }}（{{ node.floor }}层）
            </option>
          </select>
        </label>

        <div class="indoor-options">
          <label class="planner-field">
            <span>策略</span>
            <select v-model="indoor.strategy.value" class="select-input">
              <option value="time">最快通过</option>
              <option value="distance">最短距离</option>
              <option value="accessible">无障碍优先</option>
            </select>
          </label>

          <label class="planner-field">
            <span>通行方式</span>
            <select v-model="indoor.mobilityMode.value" class="select-input">
              <option value="normal">常规通行</option>
              <option value="wheelchair">轮椅通行</option>
            </select>
          </label>
        </div>

        <button class="primary-btn" type="submit" :disabled="indoor.indoorLoading.value">
          {{ indoor.indoorLoading.value ? "规划中..." : "规划室内路径" }}
        </button>
      </form>

      <div v-if="indoor.indoorRoute.value" class="results-section">
        <p class="result-explanation">{{ indoor.indoorRoute.value.summary }}</p>
        <div class="result-summary">
          <span>{{ indoor.indoorRoute.value.total_distance_m }} 米</span>
          <span class="summary-divider">·</span>
          <span>{{ indoor.indoorRoute.value.estimated_seconds }} 秒</span>
          <span class="summary-divider">·</span>
          <span>
            {{ indoor.indoorRoute.value.mobility_mode === "wheelchair" ? "轮椅模式" : "常规模式" }}
          </span>
        </div>
        <ol class="timeline-list">
          <li
            v-for="step in indoor.indoorRoute.value.steps"
            :key="`indoor-step-${step.index}`"
            class="timeline-item"
          >
            <span class="timeline-index">{{ step.index }}</span>
            <div class="timeline-content">
              <strong>
                {{ step.from_name }}（{{ step.from_floor }}层） →
                {{ step.to_name }}（{{ step.to_floor }}层）
              </strong>
              <p>{{ step.instruction }}</p>
              <p class="timeline-meta-compact">
                {{ step.distance_m }} 米 · {{ step.estimated_seconds }} 秒 · {{ step.connector }}
              </p>
            </div>
          </li>
        </ol>
      </div>
    </div>
  </component>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";

import { useIndoorNavigation } from "../../composables/useIndoorNavigation";
import type { IndoorBuilding, IndoorNode } from "../../types/models";

const props = defineProps<{
  buildings: IndoorBuilding[];
  /** When true, render as drawer (backdrop + close button) */
  asDrawer?: boolean;
  /** When asDrawer, controls visibility */
  drawerOpen?: boolean;
  /** Pre-select a building code (e.g. handoff from outdoor route end) */
  initialBuildingCode?: string;
  /** Pre-select an entry node code as the indoor start */
  initialStartNode?: string;
}>();

const emit = defineEmits<{
  "route-error": [message: string];
  close: [];
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
  if (!props.buildings.length) return;
  // Prefer the explicitly-passed building, else pick first.
  const initialBuilding = props.initialBuildingCode
    ? props.buildings.find((b) => b.building_code === props.initialBuildingCode)
    : null;
  indoor.selectedBuildingCode.value =
    initialBuilding?.building_code ?? props.buildings[0]?.building_code ?? "";

  // Initial start node: explicit prop wins, else first node.
  const opts = activeBuilding.value?.nodes ?? [];
  if (props.initialStartNode && opts.some((n) => n.code === props.initialStartNode)) {
    indoor.startNodeCode.value = props.initialStartNode;
  } else {
    indoor.startNodeCode.value = opts[0]?.code ?? "";
  }
  indoor.endNodeCode.value =
    opts.find((n) => n.code !== indoor.startNodeCode.value)?.code ?? indoor.startNodeCode.value;
  indoor.reset();
};

watch(() => [props.buildings, props.initialBuildingCode, props.initialStartNode], syncDefaults, {
  immediate: true,
});

watch(
  () => props.drawerOpen,
  (v) => {
    if (v) syncDefaults();
  },
);

watch(indoor.selectedBuildingCode, () => {
  const opts = activeBuilding.value?.nodes ?? [];
  indoor.startNodeCode.value = opts[0]?.code ?? "";
  indoor.endNodeCode.value = opts[1]?.code ?? indoor.startNodeCode.value;
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
