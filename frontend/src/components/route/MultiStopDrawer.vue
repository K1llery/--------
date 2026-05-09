<template>
  <Transition name="drawer-slide">
    <div v-if="visible" class="route-drawer-backdrop" @click.self="emit('close')">
      <div class="route-drawer">
        <header class="drawer-header">
          <h3>多点路线</h3>
          <button class="icon-btn" type="button" aria-label="关闭" @click="emit('close')">
            ✕
          </button>
        </header>

        <p class="drawer-subtitle">添加 2-8 个想参观的地点，系统会从当前起点出发并自动回到起点</p>

        <ol class="multi-stop-list">
          <li v-for="(stop, idx) in stops" :key="`stop-${idx}`" class="multi-stop-item">
            <span class="stop-index">{{ idx + 1 }}</span>
            <select v-model="stops[idx]" class="select-input stop-select">
              <option value="">— 选择站点 —</option>
              <option v-for="opt in placeOptions" :key="opt.code" :value="opt.code">
                {{ opt.name }}
              </option>
            </select>
            <button
              v-if="stops.length > 2"
              class="icon-btn"
              type="button"
              aria-label="移除"
              @click="removeStop(idx)"
            >
              🗑
            </button>
          </li>
        </ol>

        <button
          v-if="stops.length < 8"
          class="secondary-btn add-stop-btn"
          type="button"
          @click="addStop"
        >
          + 添加站点
        </button>

        <div class="drawer-options">
          <div class="route-loop-note">
            <span class="loop-note-icon">↩</span>
            <span>闭环路线已开启：参观完自动返回当前起点</span>
          </div>

          <label class="planner-field">
            <span>交通方式</span>
            <select v-model="transportMode" class="select-input">
              <option value="walk">步行</option>
              <option value="bike">自行车</option>
              <option value="shuttle">电瓶车</option>
              <option value="mixed">混合（自动选择）</option>
            </select>
          </label>

          <label class="planner-field">
            <span>策略</span>
            <select v-model="strategy" class="select-input">
              <option value="time">最快</option>
              <option value="distance">最短</option>
              <option value="congestion">避开拥挤</option>
              <option value="scenic">景观</option>
            </select>
          </label>
        </div>

        <footer class="drawer-footer">
          <button class="secondary-btn" type="button" @click="emit('close')">取消</button>
          <button
            class="primary-btn"
            type="button"
            :disabled="!canSubmit || loading"
            @click="handleSubmit"
          >
            {{ loading ? "规划中..." : "生成多点路线" }}
          </button>
        </footer>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

import type { SceneNode } from "../../types/models";
import { buildInitialTripTargets } from "../../utils/routeTrip";

const props = defineProps<{
  visible: boolean;
  placeOptions: SceneNode[];
  loading: boolean;
  initialStartCode?: string;
  initialStopCodes?: string[];
}>();

const emit = defineEmits<{
  close: [];
  submit: [payload: {
    target_codes: string[];
    closed_loop: boolean;
    transport_mode: string;
    strategy: string;
  }];
}>();

const stops = ref<string[]>(["", ""]);
const transportMode = ref("mixed");
const strategy = ref("time");

const addStop = () => {
  if (stops.value.length < 8) stops.value.push("");
};

const removeStop = (idx: number) => {
  stops.value.splice(idx, 1);
};

const canSubmit = computed(() => {
  const filled = stops.value.filter((s) => s).length;
  return filled >= 2;
});

watch(
  () => props.visible,
  (v) => {
    if (v) {
      stops.value = buildInitialTripTargets({
        placeOptions: props.placeOptions,
        currentStopCodes: props.initialStopCodes ?? [],
        startCode: props.initialStartCode ?? "",
      });
    }
  },
);

const handleSubmit = () => {
  const filled = stops.value.filter((s) => s);
  emit("submit", {
    target_codes: filled,
    closed_loop: true,
    transport_mode: transportMode.value,
    strategy: strategy.value,
  });
};
</script>
