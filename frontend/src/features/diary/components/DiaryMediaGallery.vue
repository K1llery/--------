<template>
  <div v-if="media.length" class="diary-media-gallery">
    <figure
      v-for="(item, idx) in media"
      :key="`${item.url}-${idx}`"
      class="diary-media-cell"
    >
      <video
        v-if="item.type === 'video'"
        :src="item.url"
        :poster="item.thumbnail_url"
        controls
        playsinline
        preload="metadata"
        class="diary-media-video"
      />
      <RealImage
        v-else
        :src="item.url"
        :alt="item.caption || subject"
        :name="subject"
        :search-hint="subject"
        class="diary-media-image"
      />
      <figcaption v-if="item.caption" class="diary-media-caption">
        {{ item.caption }}
      </figcaption>
    </figure>
  </div>
</template>

<script setup lang="ts">
import RealImage from "../../../components/RealImage.vue";
import type { DiaryMedia } from "../types/diary";

withDefaults(
  defineProps<{
    media: DiaryMedia[];
    subject?: string;
  }>(),
  {
    subject: "旅行日记",
  },
);
</script>

<style scoped>
.diary-media-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.diary-media-cell {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.diary-media-image,
.diary-media-video {
  width: 100%;
  height: 224px;
  object-fit: cover;
  border-radius: 20px;
  background: rgb(241 245 249);
}

.diary-media-video {
  background: black;
}

.diary-media-caption {
  font-size: 12px;
  color: rgb(100 116 139);
  padding: 0 4px;
}
</style>
