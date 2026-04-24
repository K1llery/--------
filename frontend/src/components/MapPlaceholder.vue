<template>
  <div class="map-placeholder">
    <div>
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps<{ title: string; description: string }>();
</script>
