<template>
  <div class="filter-bar route-context-bar">
    <select
      :value="modelCity"
      class="select-input"
      @change="emit('update:modelCity', ($event.target as HTMLSelectElement).value)"
    >
      <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
    </select>
    <select
      :value="modelScene"
      class="select-input"
      @change="emit('update:modelScene', ($event.target as HTMLSelectElement).value)"
    >
      <option v-for="scene in scenes" :key="scene.name" :value="scene.name">
        {{ scene.label }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import type { Scene } from "../../types/models";

defineProps<{
  cities: string[];
  scenes: Scene[];
  modelCity: string;
  modelScene: string;
}>();

const emit = defineEmits<{
  "update:modelCity": [value: string];
  "update:modelScene": [value: string];
}>();
</script>
