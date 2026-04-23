<template>
  <img
    v-bind="attrs"
    :src="resolvedSrc"
    :alt="alt"
    loading="lazy"
    decoding="async"
    @error="handleImageError"
  />
</template>

<script setup lang="ts">
import { onMounted, ref, useAttrs, watch } from "vue";

import { buildEmergencyFallback, resolveRealMedia } from "../utils/realMedia";

defineOptions({
  inheritAttrs: false,
});

const props = defineProps<{
  src?: string | null;
  alt: string;
  name?: string | null;
  city?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  sourceUrl?: string | null;
  searchHint?: string | null;
}>();

const attrs = useAttrs();
const resolvedSrc = ref(props.src || "");
let requestId = 0;

const resolveImage = async () => {
  const currentRequestId = ++requestId;
  const next = await resolveRealMedia({
    src: props.src,
    name: props.name,
    city: props.city,
    latitude: props.latitude,
    longitude: props.longitude,
    sourceUrl: props.sourceUrl,
    searchHint: props.searchHint,
  });
  if (currentRequestId !== requestId) return;
  resolvedSrc.value = next;
};

const handleImageError = () => {
  resolvedSrc.value = buildEmergencyFallback({
    src: props.src,
    name: props.name,
    city: props.city,
    latitude: props.latitude,
    longitude: props.longitude,
    sourceUrl: props.sourceUrl,
    searchHint: props.searchHint,
  });
};

watch(
  () => [
    props.src,
    props.name,
    props.city,
    props.latitude,
    props.longitude,
    props.sourceUrl,
    props.searchHint,
  ],
  () => {
    resolveImage();
  },
);

onMounted(() => {
  resolveImage();
});
</script>
