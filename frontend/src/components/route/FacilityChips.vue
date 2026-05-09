<template>
  <div class="facility-chips">
    <button
      v-for="chip in chips"
      :key="chip.value"
      type="button"
      class="facility-chip"
      :class="{ active: activeType === chip.value }"
      @click="toggle(chip.value)"
    >
      <span class="facility-chip-icon">{{ chip.icon }}</span>
      <span class="facility-chip-label">{{ chip.label }}</span>
      <span v-if="counts[chip.value]" class="facility-chip-count">{{ counts[chip.value] }}</span>
    </button>
    <button
      v-if="activeType"
      type="button"
      class="facility-chip facility-chip-clear"
      @click="toggle('')"
      title="清除筛选"
    >
      ✕ 清除
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { Facility } from "../../types/models";

const props = defineProps<{
  facilities: Facility[];
  activeType: string;
}>();

const emit = defineEmits<{
  "update:activeType": [value: string];
}>();

const chips = [
  { value: "restroom", icon: "🚻", label: "厕所" },
  { value: "restaurant", icon: "🍽️", label: "餐厅" },
  { value: "supermarket", icon: "🛒", label: "超市" },
  { value: "service", icon: "☕", label: "服务点" },
  { value: "shop", icon: "🏪", label: "商店" },
  { value: "sports", icon: "🏃", label: "运动" },
];

const counts = computed<Record<string, number>>(() => {
  const result: Record<string, number> = {};
  for (const f of props.facilities) {
    const t = f.normalized_type || f.facility_type;
    result[t] = (result[t] || 0) + 1;
  }
  return result;
});

const toggle = (value: string) => {
  if (props.activeType === value) {
    emit("update:activeType", "");
  } else {
    emit("update:activeType", value);
  }
};
</script>
