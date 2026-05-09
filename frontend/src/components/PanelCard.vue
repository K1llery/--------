<template>
  <section class="bg-white rounded-3xl card-elevated p-6 md:p-8 animate-[card-enter_0.4s_ease]">
    <header v-if="title" class="mb-4">
      <h2 class="text-xl font-bold text-gray-900">{{ title }}</h2>
      <p v-if="subtitle" class="text-sm text-gray-500 mt-1">{{ subtitle }}</p>
    </header>
    <slot />
  </section>
</template>
<script setup lang="ts">
defineProps<{ title?: string; subtitle?: string }>();
</script>
