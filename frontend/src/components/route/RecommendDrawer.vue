<template>
  <Transition name="drawer-slide">
    <div v-if="visible" class="route-drawer-backdrop" @click.self="emit('close')">
      <div class="route-drawer">
        <header class="drawer-header">
          <h3>🤖 为我规划行程</h3>
          <button class="icon-btn" type="button" aria-label="关闭" @click="emit('close')">
            ✕
          </button>
        </header>

        <p class="drawer-subtitle">告诉我你有多少时间，我帮你挑路线</p>

        <div class="recommend-form">
          <label class="planner-field">
            <span>可用时长：<strong>{{ duration }} 分钟</strong></span>
            <input
              v-model.number="duration"
              type="range"
              class="range-input"
              :min="15"
              :max="120"
              :step="5"
            />
            <span class="range-labels">
              <small>15 分钟</small>
              <small>120 分钟</small>
            </span>
          </label>

          <div class="recommend-presets">
            <button
              v-for="preset in presets"
              :key="preset.value"
              type="button"
              class="strategy-chip"
              :class="{ active: duration === preset.value }"
              @click="duration = preset.value"
            >
              {{ preset.label }}
            </button>
          </div>

          <label class="planner-field">
            <span>偏好</span>
            <div class="strategy-chips inline">
              <button
                v-for="p in preferences"
                :key="p.value"
                type="button"
                class="strategy-chip"
                :class="{ active: preference === p.value }"
                @click="preference = p.value"
              >
                {{ p.icon }} {{ p.label }}
              </button>
            </div>
          </label>

          <label class="planner-field">
            <span>交通方式</span>
            <select v-model="transportMode" class="select-input">
              <option value="walk">🚶 步行</option>
              <option value="bike">🚲 自行车</option>
              <option value="shuttle">🚐 电瓶车</option>
            </select>
          </label>
        </div>

        <footer class="drawer-footer">
          <button class="secondary-btn" type="button" @click="emit('close')">取消</button>
          <button
            class="primary-btn"
            type="button"
            :disabled="loading"
            @click="handleSubmit"
          >
            {{ loading ? "推荐中..." : "生成推荐路线" }}
          </button>
        </footer>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

const props = defineProps<{
  visible: boolean;
  loading: boolean;
}>();

const emit = defineEmits<{
  close: [];
  submit: [payload: {
    duration_minutes: number;
    transport_mode: string;
    strategy: string;
  }];
}>();

const duration = ref(45);
const preference = ref("scenic");
const transportMode = ref("walk");

const presets = [
  { value: 30, label: "半小时快走" },
  { value: 60, label: "1 小时" },
  { value: 90, label: "1.5 小时深度" },
];

const preferences = [
  { value: "scenic", icon: "🌳", label: "景观" },
  { value: "time", icon: "⚡", label: "效率" },
  { value: "distance", icon: "📏", label: "近距离" },
];

watch(
  () => props.visible,
  (v) => {
    if (v) {
      // reset to defaults each open
      duration.value = 45;
      preference.value = "scenic";
      transportMode.value = "walk";
    }
  },
);

const handleSubmit = () => {
  emit("submit", {
    duration_minutes: duration.value,
    transport_mode: transportMode.value,
    strategy: preference.value,
  });
};
</script>
