<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
    <!-- Illustration -->
    <svg
      class="w-32 h-32 text-gray-300 mb-5"
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle
        cx="60"
        cy="60"
        r="56"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-dasharray="4 4"
        opacity="0.5"
      />
      <rect
        x="35"
        y="40"
        width="50"
        height="36"
        rx="6"
        stroke="currentColor"
        stroke-width="1.5"
      />
      <path
        d="M35 64l12-10 8 6 14-12 16 16"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        opacity="0.6"
      />
      <circle
        cx="52"
        cy="52"
        r="4"
        stroke="currentColor"
        stroke-width="1.5"
        opacity="0.6"
      />
      <path
        d="M54 88h12"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        opacity="0.3"
      />
      <path
        d="M48 94h24"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        opacity="0.2"
      />
    </svg>
    <p class="text-sm font-medium text-gray-500">{{ title }}</p>
    <p v-if="description" class="text-xs text-gray-400 mt-1.5 max-w-xs">
      {{ description }}
    </p>
    <slot />
  </div>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ title?: string; description?: string }>(), {
  title: "暂无数据",
  description: "",
});
</script>
