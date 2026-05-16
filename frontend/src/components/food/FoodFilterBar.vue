<template>
  <div class="food-filter-bar mt-5">
    <slot />
    <select
      :value="cityFilter"
      class="soft-control text-sm text-slate-700"
      @change="emit('update:cityFilter', ($event.target as HTMLSelectElement).value)"
    >
      <option value="全部">全部城市</option>
      <option v-for="city in cities" :key="city" :value="city">
        {{ city }}
      </option>
    </select>
    <select
      :value="cuisineFilter"
      class="soft-control text-sm text-slate-700"
      @change="emit('update:cuisineFilter', ($event.target as HTMLSelectElement).value)"
    >
      <option value="全部">全部菜系</option>
      <option v-for="cuisine in cuisines" :key="cuisine" :value="cuisine">
        {{ cuisine }}
      </option>
    </select>
    <select
      :value="sortMode"
      class="soft-control text-sm text-slate-700"
      @change="emit('update:sortMode', ($event.target as HTMLSelectElement).value as FoodSortMode)"
    >
      <option value="recommend">推荐优先</option>
      <option value="distance">距离最近</option>
      <option value="rating">评分最高</option>
      <option value="heat">热度最高</option>
    </select>
    <span v-if="lastUpdated" class="text-xs text-slate-400 self-center">
      最近更新：{{ lastUpdated }}
    </span>
  </div>
</template>

<script setup lang="ts">
import type { FoodSortMode } from "../../utils/foodRecommend";

defineProps<{
  cityFilter: string;
  cuisineFilter: string;
  sortMode: FoodSortMode;
  cities: string[];
  cuisines: string[];
  lastUpdated: string;
}>();

const emit = defineEmits<{
  "update:cityFilter": [value: string];
  "update:cuisineFilter": [value: string];
  "update:sortMode": [value: FoodSortMode];
}>();
</script>
