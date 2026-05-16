<template>
  <aside class="space-y-5">
    <section
      v-if="food"
      class="card-elevated rounded-[24px] p-5 sticky top-18 self-start space-y-4 food-detail-card"
    >
      <div>
        <div>
          <span class="route-panel-kicker">当前选择</span>
          <h3 class="text-xl font-bold text-slate-950 mt-1">{{ food.name }}</h3>
          <p class="text-sm text-slate-500 mt-2">
            {{ food.destination_name || food.city || "推荐美食候选" }}
          </p>
        </div>
      </div>

      <div class="food-detail-media">
        <RealImage
          v-if="food.image_url"
          :src="food.image_url"
          :alt="food.name"
          :name="food.name"
          :search-hint="food.destination_name"
          :city="food.city"
          :latitude="food.latitude"
          :longitude="food.longitude"
          :source-url="food.source_url"
          class="w-full h-full object-cover"
        />
        <div v-else class="food-image-placeholder food-image-placeholder-detail">
          <span class="food-image-icon">餐</span>
          <strong>{{ food.cuisine || "推荐餐饮" }}</strong>
          <small>{{ food.city || food.destination_name || "美食候选" }}</small>
        </div>
      </div>

      <div class="food-detail-section">
        <span class="food-detail-label">为什么推荐</span>
        <div class="food-reason-list mt-2">
          <span
            v-for="reason in foodRankReasons(food)"
            :key="`${foodKey(food)}-detail-${reason}`"
            class="food-reason-pill"
          >
            {{ reason }}
          </span>
        </div>
        <p class="text-sm text-slate-600 leading-7 mt-3">
          {{
            food.description ||
            "这条推荐结合评分、距离和目的地关联度生成，可作为当前行程的餐饮补充。"
          }}
        </p>
      </div>

      <div class="food-detail-section">
        <span class="food-detail-label">距离与路线信息</span>
        <p class="text-sm text-slate-600 mt-2">
          距离 {{ formatDistance(food) }}，{{
            food.latitude != null && food.longitude != null
              ? "可直接打开地图导航。"
              : "暂无可用坐标，建议结合地址人工规划。"
          }}
        </p>
      </div>

      <div class="food-detail-section">
        <span class="food-detail-label">地址</span>
        <p class="text-sm text-slate-600 mt-2">
          {{ food.address || food.destination_name || "地址待补充" }}
        </p>
      </div>

      <div class="food-detail-section text-xs text-slate-400 leading-6">
        <span class="food-detail-label">来源链接</span>
        <p class="m-0">
          <a
            v-if="food.source_url"
            :href="food.source_url"
            target="_blank"
            rel="noreferrer"
            class="text-primary-600 hover:underline"
          >
            {{ food.source_name || "来源页面" }}
          </a>
          <span v-else>{{ food.source_name || "平台数据" }}</span>
        </p>
        <p class="m-0">图片来源：{{ food.image_source_name || "Wikipedia / OpenStreetMap" }}</p>
      </div>

      <div class="food-card-actions">
        <button
          type="button"
          class="food-action-button food-action-primary"
          @click.stop.prevent="null"
        >
          加入行程
        </button>
        <a
          v-if="food.latitude != null && food.longitude != null"
          class="food-action-button"
          :href="`https://www.google.com/maps/search/?api=1&query=${food.latitude},${food.longitude}`"
          target="_blank"
          rel="noreferrer"
        >
          查看路线
        </a>
        <button v-else type="button" class="food-action-button" disabled>查看路线</button>
      </div>
    </section>

    <section v-else class="card-elevated rounded-[24px] p-5 space-y-3">
      <span class="route-panel-kicker">详情面板</span>
      <h3 class="text-lg font-bold text-slate-950">先从左侧选择一家美食</h3>
      <p class="text-sm text-slate-500 leading-7">
        这里会集中展示当前餐饮的图片、位置、关联目的地和评分信息，方便继续决定是否加入行程。
      </p>
    </section>
  </aside>
</template>

<script setup lang="ts">
import RealImage from "../RealImage.vue";
import { buildFoodRankReasons, getFoodDistanceKm } from "../../utils/foodRecommend";
import type { FoodRecommendation } from "./types";

defineProps<{
  food: FoodRecommendation | null;
}>();

const foodKey = (item: FoodRecommendation) => item.source_id || item.id || item.name;

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
</script>
