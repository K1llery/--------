<template>
  <div class="diary-filter-bar">
    <div class="diary-filter-group">
      <span class="diary-filter-label">搜索方式</span>
      <div class="diary-filter-tabs">
        <button
          v-for="opt in searchTypes"
          :key="opt.value"
          type="button"
          class="diary-filter-chip"
          :class="{ 'diary-filter-chip-active': searchType === opt.value }"
          @click="$emit('update:searchType', opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>
    <div class="diary-filter-group">
      <span class="diary-filter-label">排序</span>
      <div class="diary-filter-tabs">
        <button
          v-for="opt in sortKeys"
          :key="opt.value"
          type="button"
          class="diary-filter-chip"
          :class="{ 'diary-filter-chip-active': sort === opt.value }"
          @click="$emit('update:sort', opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DiarySearchType, DiarySortKey } from "../types/diary";

defineProps<{
  searchType: DiarySearchType;
  sort: DiarySortKey;
}>();

defineEmits<{
  (e: "update:searchType", value: DiarySearchType): void;
  (e: "update:sort", value: DiarySortKey): void;
}>();

const searchTypes: { value: DiarySearchType; label: string }[] = [
  { value: "destination", label: "目的地" },
  { value: "title_exact", label: "标题精确" },
  { value: "fulltext", label: "正文全文" },
];

const sortKeys: { value: DiarySortKey; label: string }[] = [
  { value: "recommend", label: "综合推荐" },
  { value: "views", label: "热度最高" },
  { value: "rating", label: "评分最高" },
  { value: "latest", label: "最新发布" },
];
</script>

<style scoped>
.diary-filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 18px 28px;
}

.diary-filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.diary-filter-label {
  font-size: 11px;
  font-weight: 600;
  color: rgb(100 116 139);
  letter-spacing: 0.04em;
}

.diary-filter-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.diary-filter-chip {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid rgb(226 232 240);
  background: white;
  font-size: 13px;
  color: rgb(71 85 105);
  cursor: pointer;
  transition: all 120ms ease;
}

.diary-filter-chip:hover {
  border-color: rgb(148 163 184);
}

.diary-filter-chip-active {
  background: rgb(15 23 42);
  border-color: rgb(15 23 42);
  color: white;
  font-weight: 600;
}
</style>
