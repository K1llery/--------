<template>
  <div
    class="rounded-2xl border-0 shadow-md shadow-gray-200/50 bg-white overflow-hidden animate-pulse"
  >
    <div
      v-if="showImage"
      class="h-36 bg-gradient-to-r from-gray-100 via-gray-200/70 to-gray-100 skeleton-shimmer"
    />
    <div class="p-4 space-y-2.5">
      <div class="h-4 w-3/4 rounded-md bg-gray-200/80" />
      <div class="h-3 w-1/2 rounded-md bg-gray-100" />
      <div class="flex gap-2">
        <div class="h-5 w-14 rounded-full bg-primary-50" />
        <div class="h-5 w-14 rounded-full bg-gray-100" />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ showImage?: boolean }>(), { showImage: true });
</script>
<style scoped>
.skeleton-shimmer {
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
