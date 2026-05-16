<template>
  <article v-tilt class="food-card">
    <div class="food-card-media">
      <RealImage
        v-if="item.image_url"
        :src="item.image_url"
        :alt="item.name"
        :name="item.name"
        :search-hint="item.destination_name"
        :city="item.city"
        :latitude="item.latitude"
        :longitude="item.longitude"
        :source-url="item.source_url"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
      />
      <div v-else class="food-image-placeholder">
        <span class="food-image-icon">餐</span>
        <strong>{{ item.cuisine || "推荐餐饮" }}</strong>
        <small>{{ item.city || item.destination_name || "美食候选" }}</small>
      </div>
      <span class="food-rank-badge" :class="{ 'food-rank-badge-premium': index < 3 }">
        TOP {{ index + 1 }}
      </span>
    </div>
    <div class="p-4 space-y-4">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <h3 class="text-base font-bold text-slate-900 truncate">
            {{ foodDisplayName(item) }}
          </h3>
          <p v-if="foodVenueLine(item)" class="text-xs text-slate-400 mt-1 truncate">
            {{ foodVenueLine(item) }}
          </p>
          <p class="text-sm text-slate-500 mt-1">
            {{ item.city || "待补充城市" }} · {{ item.cuisine || "特色餐饮" }}
          </p>
        </div>
        <span class="food-card-badge">{{ item.cuisine || "推荐" }}</span>
      </div>

      <div class="food-card-metrics">
        <span>
          <small>{{ activeAnchorName ? "距离锚点" : "距离" }}</small>
          <strong>{{ formatDistance(item) }}</strong>
        </span>
        <span>
          <small>评分</small>
          <strong>{{ displayMetric(item.rating) }}</strong>
        </span>
      </div>

      <div v-if="foodDishTags(item).length" class="food-dish-list">
        <span
          v-for="dish in foodDishTags(item)"
          :key="`${foodKey(item)}-${dish}`"
          class="food-dish-pill"
        >
          {{ dish }}
        </span>
      </div>

      <div class="food-reason-list">
        <span
          v-for="reason in foodRankReasons(item)"
          :key="`${foodKey(item)}-${reason}`"
          class="food-reason-pill"
        >
          {{ reason }}
        </span>
      </div>

      <div class="food-card-actions">
        <button
          type="button"
          class="food-action-button food-action-primary"
          :disabled="!item.id"
          :title="item.id ? '查看详情' : '缺少详情标识'"
          @click.stop="openDetail"
        >
          详情
        </button>
        <button type="button" class="food-action-button" @click.stop.prevent="null">
          加入行程
        </button>
        <a
          v-if="item.latitude != null && item.longitude != null"
          class="food-action-button"
          :href="mapUrl"
          target="_blank"
          rel="noreferrer"
          @click.stop="null"
        >
          地图导航
        </a>
        <button v-else type="button" class="food-action-button" disabled>地图导航</button>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";

import RealImage from "../RealImage.vue";
import { buildFoodRankReasons, getFoodDistanceKm } from "../../utils/foodRecommend";
import type { FoodRecommendation } from "./types";

const props = defineProps<{
  item: FoodRecommendation;
  index: number;
  activeAnchorName: string;
}>();

const emit = defineEmits<{
  viewDetail: [item: FoodRecommendation];
}>();

const displayMetric = (value: number | null | undefined) => value ?? "待补充";

const foodKey = (item: FoodRecommendation) => item.source_id || item.id || item.name;

const foodDisplayName = (item: FoodRecommendation) =>
  item.window_name || item.restaurant_name || item.canteen_name || item.venue_name || item.name;

const foodVenueLine = (item: FoodRecommendation) => {
  const displayName = foodDisplayName(item);

  if (item.venue_type === "window" && item.canteen_name) {
    return item.restaurant_name
      ? `${item.canteen_name} · ${item.restaurant_name}`
      : item.canteen_name;
  }

  if (item.venue_type === "canteen" && item.window_name) {
    return item.canteen_name || item.venue_name || "";
  }

  if (item.name && item.name !== displayName) return item.name;
  return "";
};

const foodDishTags = (item: FoodRecommendation) => {
  if (Array.isArray(item.dishes) && item.dishes.length > 0) {
    return item.dishes.filter(Boolean).slice(0, 4);
  }

  if ((item.venue_type === "canteen" || item.venue_type === "window") && item.cuisine) {
    return [item.cuisine];
  }

  return [];
};

const formatDistance = (item: FoodRecommendation) => {
  const distanceKm = getFoodDistanceKm(item);
  if (distanceKm == null) return "待补充";
  if (distanceKm < 1) return `${Math.round(distanceKm * 1000)} m`;
  return `${distanceKm.toFixed(1)} km`;
};

const foodRankReasons = (item: FoodRecommendation) => {
  const reasons = buildFoodRankReasons(item).filter((reason) => reason !== "热度高");
  return reasons.length ? reasons.slice(0, 3) : ["综合推荐"];
};

const openDetail = () => {
  if (!props.item.id) {
    console.warn("无法打开美食详情：缺少 food.id", props.item);
    return;
  }
  emit("viewDetail", props.item);
};

const mapUrl = computed(() =>
  props.item.latitude != null && props.item.longitude != null
    ? `https://www.google.com/maps/search/?api=1&query=${props.item.latitude},${props.item.longitude}`
    : "",
);
</script>
