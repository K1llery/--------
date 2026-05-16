<template>
  <EmptyState
    title="没有找到符合当前条件的美食"
    description="换个关键词、城市、菜系或关联目的地再试试看。"
  >
    <button class="btn-soft-secondary text-sm mt-4" @click="emit('clearFilters')">清空筛选</button>
  </EmptyState>
</template>

<script setup lang="ts">
import EmptyState from "../EmptyState.vue";

const emit = defineEmits<{
  clearFilters: [];
}>();
</script>
