<template>
  <div class="helper-grid">
    <div class="helper-card">
      <h3>当前城市</h3>
      <p>{{ selectedCity }}</p>
      <p>{{ currentSceneMessage }}</p>
    </div>
    <div class="helper-card">
      <h3>推荐起点/停靠</h3>
      <p v-for="item in suggestedNodes" :key="item.code">{{ item.name }}</p>
    </div>
    <div class="helper-card">
      <h3>导航摘要</h3>
      <p>{{ navigationSummary || "规划后会显示路段数量、总时长与策略说明。" }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  selectedCity: string;
  currentSceneMessage: string;
  suggestedNodes: Array<{ code: string; name: string }>;
  navigationSummary: string;
}>();
</script>
