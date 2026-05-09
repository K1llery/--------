<template>
  <Transition name="page-fade-slide">
    <div v-if="visible" class="route-planning-overlay">
      <div class="planning-indicator">
        <div class="planning-dots">
          <span class="planning-dot"></span>
          <span class="planning-dot"></span>
          <span class="planning-dot"></span>
        </div>
        <p>正在规划路线...</p>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean;
}>();
</script>
