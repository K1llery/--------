<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 2xl:grid-cols-3 gap-4 stagger-children">
    <FoodCard
      v-for="(item, index) in items"
      :key="foodKey(item)"
      :item="item"
      :index="index"
      :active-anchor-name="activeAnchorName"
      @view-detail="emit('viewDetail', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import FoodCard from "./FoodCard.vue";
import type { FoodRecommendation } from "./types";

defineProps<{
  items: FoodRecommendation[];
  activeAnchorName: string;
}>();

const emit = defineEmits<{
  viewDetail: [item: FoodRecommendation];
}>();

const foodKey = (item: FoodRecommendation) => item.source_id || item.id || item.name;
</script>
