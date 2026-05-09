<template>
  <div class="status-card route-empty-state">
    <p>{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  context: "initial" | "segments" | "alternatives";
}>();

const message = computed(() => {
  switch (props.context) {
    case "segments":
      return "生成路线后，分段导航将显示在这里。";
    case "alternatives":
      return "当前策略无备选路线，尝试切换策略查看更多方案。";
    case "initial":
    default:
      return "搜索目的地即可规划路线，也可以把多个地点加入行程后优化游览顺序。";
  }
});
</script>
