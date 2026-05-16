<template>
  <div class="food-anchor-panel mt-5">
    <div class="min-w-0">
      <p class="route-panel-kicker">推荐锚点</p>
      <h3 class="text-base font-bold text-slate-950 mt-1">
        {{ activeAnchorName ? `${activeAnchorName} 周边美食` : "先选择景点或学校锚点" }}
      </h3>
      <p class="text-sm text-slate-500 mt-1">
        以锚点为中心查看周边餐饮；未选择时仍按当前筛选条件展示综合推荐。
      </p>
    </div>
    <div class="food-anchor-controls">
      <div class="food-anchor-type-group" aria-label="锚点类型">
        <button
          type="button"
          class="food-anchor-type-button"
          :class="{ 'food-anchor-type-button-active': anchorType === 'destination' }"
          @click="emit('update:anchorType', 'destination')"
        >
          景点
        </button>
        <button
          type="button"
          class="food-anchor-type-button"
          :class="{ 'food-anchor-type-button-active': anchorType === 'school' }"
          @click="emit('update:anchorType', 'school')"
        >
          学校
        </button>
      </div>
      <select
        :value="anchorId"
        class="soft-control text-sm text-slate-700 min-w-[16rem]"
        @change="emit('update:anchorId', ($event.target as HTMLSelectElement).value)"
      >
        <option value="">
          {{ anchorType === "school" ? "选择学校锚点" : "选择景点锚点" }}
        </option>
        <option v-for="anchor in anchorOptions" :key="anchor.id" :value="anchor.id">
          {{ anchor.name }}
        </option>
      </select>
      <select
        :value="radiusKm"
        class="soft-control text-sm text-slate-700 min-w-[8rem]"
        @change="emit('update:radiusKm', Number(($event.target as HTMLSelectElement).value))"
      >
        <option v-for="option in radiusOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AnchorType, FoodAnchorOption, RadiusOption } from "./types";

defineProps<{
  activeAnchorName: string;
  anchorType: AnchorType;
  anchorId: string;
  anchorOptions: FoodAnchorOption[];
  radiusKm: number;
  radiusOptions: RadiusOption[];
}>();

const emit = defineEmits<{
  "update:anchorType": [value: AnchorType];
  "update:anchorId": [value: string];
  "update:radiusKm": [value: number];
}>();
</script>
