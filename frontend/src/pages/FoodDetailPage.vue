<template>
  <div class="food-detail-page space-y-6">
    <section class="food-detail-header card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div class="min-w-0">
          <button type="button" class="food-detail-back" @click="backToFoods">返回美食推荐</button>
          <p class="home-section-kicker mt-4">美食详情</p>
          <h1 class="food-detail-title">
            {{ food ? foodDisplayName(food) : "美食详情" }}
          </h1>
          <p v-if="food" class="food-detail-subtitle">
            {{ subtitle }}
          </p>
        </div>

        <div v-if="food" class="food-detail-score-chip">
          <span>综合推荐</span>
          <strong>{{ formatRecommendScore(food) }}</strong>
        </div>
      </div>
    </section>

    <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-[minmax(0,1.1fr)_360px] gap-6">
      <SkeletonCard />
      <SkeletonCard />
    </div>

    <EmptyState v-else-if="loadError && !food" title="美食数据加载失败" :description="loadError">
      <div class="food-detail-actions mt-4">
        <button class="food-detail-action food-detail-action-primary" @click="retryLoad">
          重新加载
        </button>
        <button class="food-detail-action" @click="backToFoods">返回美食推荐</button>
      </div>
    </EmptyState>

    <EmptyState
      v-else-if="!food"
      title="未找到该美食信息"
      description="可能是链接中的餐饮标识已失效，或当前数据还没有加载到这条记录。"
    >
      <button class="food-detail-action mt-4" @click="backToFoods">返回美食推荐</button>
    </EmptyState>

    <div v-else class="space-y-6">
      <section class="food-detail-main-grid">
        <div class="food-detail-image-card">
          <img
            v-if="hasHeroImage"
            :src="imageUrl"
            :alt="food.name"
            class="food-detail-primary-image"
            loading="lazy"
            decoding="async"
            @error="imageLoadFailed = true"
          />
          <div v-else class="food-detail-image-placeholder">
            <span>餐</span>
            <strong>{{ fallbackImageUrl ? "美食推荐" : "暂无餐厅图片" }}</strong>
            <small>{{ food.cuisine || food.city || food.destination_name || "美食候选" }}</small>
          </div>
        </div>

        <aside class="food-detail-side-card card-elevated rounded-[24px] p-5 lg:p-6">
          <span class="food-detail-label">核心指标</span>
          <div class="food-detail-metric-grid mt-4">
            <div class="food-detail-metric">
              <small>评分</small>
              <strong>{{ displayMetric(food.rating) }}</strong>
            </div>
            <div class="food-detail-metric">
              <small>热度</small>
              <strong>{{ displayMetric(food.heat) }}</strong>
            </div>
            <div class="food-detail-metric">
              <small>距离</small>
              <strong>{{ formatDistance(food) }}</strong>
            </div>
            <div class="food-detail-metric food-detail-metric-accent">
              <small>推荐分</small>
              <strong>{{ formatRecommendScore(food) }}</strong>
            </div>
          </div>

          <div class="food-detail-mini-summary">
            <span>{{ food.city || "城市待补充" }}</span>
            <span>{{ food.cuisine || "特色餐饮" }}</span>
            <span>{{ foodTypeLabel(food) }}</span>
          </div>

          <div class="food-detail-actions mt-5">
            <button
              type="button"
              class="food-detail-action food-detail-action-primary"
              @click="addToPlan"
            >
              加入行程
            </button>
            <a
              v-if="mapUrl"
              class="food-detail-action"
              :href="mapUrl"
              target="_blank"
              rel="noreferrer"
            >
              查看路线
            </a>
            <button v-else type="button" class="food-detail-action" disabled>查看路线</button>
          </div>
        </aside>
      </section>

      <section class="food-detail-content-grid">
        <div class="space-y-5">
          <section class="food-detail-block">
            <div class="food-detail-section-head">
              <span class="food-detail-label">为什么推荐</span>
              <strong>{{ formatRecommendScore(food) }} 分</strong>
            </div>
            <div class="food-detail-reason-grid mt-4">
              <span
                v-for="reason in foodRankReasons(food)"
                :key="`${foodKey(food)}-${reason}`"
                class="food-detail-reason-pill"
              >
                {{ reason }}
              </span>
            </div>
            <p class="food-detail-copy mt-4">
              {{ recommendSummary(food) }}
            </p>
          </section>

          <section class="food-detail-block">
            <div class="food-detail-section-head">
              <span class="food-detail-label">位置与路线</span>
              <strong>{{ coordinateStatus }}</strong>
            </div>
            <div class="food-detail-info-list mt-4">
              <div class="food-detail-info-row">
                <span>关联景点/学校</span>
                <strong>{{ anchorLabel }}</strong>
              </div>
              <div class="food-detail-info-row">
                <span>距离</span>
                <strong>{{ formatDistance(food) }}</strong>
              </div>
              <div class="food-detail-info-row">
                <span>地址</span>
                <strong>{{ food.address || "地址待补充" }}</strong>
              </div>
              <div class="food-detail-info-row">
                <span>经纬度</span>
                <strong>{{ coordinateText }}</strong>
              </div>
            </div>
            <div class="food-detail-actions mt-4">
              <a
                v-if="mapUrl"
                class="food-detail-action food-detail-action-primary"
                :href="mapUrl"
                target="_blank"
                rel="noreferrer"
              >
                查看路线
              </a>
              <button v-else type="button" class="food-detail-action" disabled>暂无精确坐标</button>
            </div>
          </section>

          <section v-if="hasVenueDetails" class="food-detail-block">
            <span class="food-detail-label">餐厅 / 食堂 / 窗口信息</span>
            <div class="food-detail-info-list mt-4">
              <div v-for="row in venueRows" :key="row.label" class="food-detail-info-row">
                <span>{{ row.label }}</span>
                <strong>{{ row.value }}</strong>
              </div>
            </div>
            <div v-if="dishTags.length" class="food-detail-dish-list mt-4">
              <span v-for="dish in dishTags" :key="dish">{{ dish }}</span>
            </div>
          </section>

          <section v-if="hasSourceInfo" class="food-detail-block">
            <span class="food-detail-label">来源信息</span>
            <div class="food-detail-info-list mt-4">
              <div v-for="row in sourceRows" :key="row.label" class="food-detail-info-row">
                <span>{{ row.label }}</span>
                <a v-if="row.href" :href="row.href" target="_blank" rel="noreferrer">
                  {{ row.value }}
                </a>
                <strong v-else>{{ row.value }}</strong>
              </div>
            </div>
          </section>
        </div>

        <aside class="food-detail-action-card card-elevated rounded-[24px] p-5">
          <span class="route-panel-kicker">操作区</span>
          <h2>{{ foodDisplayName(food) }}</h2>
          <p>{{ actionHint }}</p>
          <div class="food-detail-actions food-detail-actions-column">
            <button
              type="button"
              class="food-detail-action food-detail-action-primary"
              @click="addToPlan"
            >
              加入行程
            </button>
            <a
              v-if="mapUrl"
              class="food-detail-action"
              :href="mapUrl"
              target="_blank"
              rel="noreferrer"
            >
              查看路线
            </a>
            <button v-else type="button" class="food-detail-action" disabled>查看路线</button>
            <button type="button" class="food-detail-action" @click="backToFoods">
              返回推荐列表
            </button>
          </div>
        </aside>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import EmptyState from "../components/EmptyState.vue";
import SkeletonCard from "../components/SkeletonCard.vue";
import type { FoodRecommendation } from "../components/food/types";
import { useTravelStore } from "../stores/travel";
import { buildFoodRankReasons, getFoodDistanceKm, getRecommendScore } from "../utils/foodRecommend";

type DetailRow = {
  label: string;
  value: string;
  href?: string;
};

const route = useRoute();
const router = useRouter();
const store = useTravelStore();
const imageLoadFailed = ref(false);

const routeParamValue = computed(() => {
  const id = route.params.id;
  return Array.isArray(id) ? id[0] || "" : String(id || "");
});

const routeFoodId = computed(() => {
  try {
    return decodeURIComponent(routeParamValue.value);
  } catch {
    return routeParamValue.value;
  }
});

const loading = computed(() => store.foods.loading);
const loadError = computed(() => store.foods.error);

const foodKey = (item: FoodRecommendation) => item.source_id || item.id || item.name;

const food = computed<FoodRecommendation | null>(() => {
  const targetId = routeFoodId.value;
  if (!targetId) return null;

  return (
    (store.foods.items as FoodRecommendation[]).find((item) => foodKey(item) === targetId) ?? null
  );
});

const imageUrl = computed(() => food.value?.image_url?.trim() || "");

const isDecorativeFallbackImage = computed(() => {
  const src = imageUrl.value.toLowerCase();
  const sourceName = (food.value?.image_source_name || "").toLowerCase();

  return (
    sourceName.includes("占位") ||
    sourceName.includes("fallback") ||
    sourceName.includes("logo") ||
    src.includes("/media/system/")
  );
});

const hasHeroImage = computed(
  () => Boolean(imageUrl.value) && !isDecorativeFallbackImage.value && !imageLoadFailed.value,
);

const fallbackImageUrl = computed(() =>
  imageUrl.value && isDecorativeFallbackImage.value && !imageLoadFailed.value ? imageUrl.value : "",
);

const venueTypeLabels: Record<NonNullable<FoodRecommendation["venue_type"]>, string> = {
  restaurant: "餐厅",
  canteen: "食堂",
  window: "窗口",
  cafe: "咖啡",
  snack: "小吃",
  stall_group: "档口集合",
};

const foodTypeLabel = (item: FoodRecommendation) =>
  item.venue_type ? venueTypeLabels[item.venue_type] : "餐饮";

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

const subtitle = computed(() => {
  if (!food.value) return "";

  return [food.value.city, food.value.cuisine, foodTypeLabel(food.value), foodVenueLine(food.value)]
    .filter(Boolean)
    .join(" · ");
});

const mapUrl = computed(() =>
  food.value?.latitude != null && food.value.longitude != null
    ? `https://www.google.com/maps/search/?api=1&query=${food.value.latitude},${food.value.longitude}`
    : "",
);

const displayMetric = (value: number | null | undefined) => value ?? "待补充";

const formatRecommendScore = (item: FoodRecommendation) => getRecommendScore(item).toFixed(1);

const formatDistance = (item: FoodRecommendation) => {
  const distanceKm = getFoodDistanceKm(item);
  if (distanceKm == null) return "待补充";
  if (distanceKm < 1) return `${Math.round(distanceKm * 1000)} m`;
  return `${distanceKm.toFixed(1)} km`;
};

const foodRankReasons = (item: FoodRecommendation) => {
  const reasons = buildFoodRankReasons(item);
  return reasons.length ? reasons.slice(0, 3) : ["综合推荐"];
};

const recommendSummary = (item: FoodRecommendation) => {
  if (item.description) return item.description;

  const reasons = foodRankReasons(item).join("、");
  return `${foodDisplayName(item)}结合${reasons || "综合指标"}进入当前推荐结果，适合作为行程中的餐饮补充。`;
};

const anchorLabel = computed(() => {
  if (!food.value) return "未关联具体景点/学校";
  return food.value.destination_name || food.value.venue_name || "未关联具体景点/学校";
});

const coordinateStatus = computed(() => (mapUrl.value ? "可导航" : "暂无精确坐标"));

const coordinateText = computed(() => {
  if (food.value?.latitude == null || food.value.longitude == null) return "暂无精确坐标";
  return `${food.value.latitude.toFixed(6)}, ${food.value.longitude.toFixed(6)}`;
});

const dishTags = computed(() =>
  food.value && Array.isArray(food.value.dishes)
    ? food.value.dishes.filter(Boolean).slice(0, 8)
    : [],
);

const venueRows = computed<DetailRow[]>(() => {
  if (!food.value) return [];
  const rows: DetailRow[] = [];

  if (food.value.restaurant_name) {
    rows.push({ label: "餐厅名", value: food.value.restaurant_name });
  }
  if (food.value.canteen_name) {
    rows.push({ label: "食堂名", value: food.value.canteen_name });
  }
  if (food.value.window_name) {
    rows.push({ label: "窗口名", value: food.value.window_name });
  }
  if (food.value.venue_type) {
    rows.push({ label: "类型", value: foodTypeLabel(food.value) });
  }

  return rows;
});

const hasVenueDetails = computed(() => venueRows.value.length > 0 || dishTags.value.length > 0);

const sourceRows = computed<DetailRow[]>(() => {
  if (!food.value) return [];
  const rows: DetailRow[] = [];

  if (food.value.source_name) {
    rows.push({ label: "数据来源", value: food.value.source_name });
  }
  if (food.value.source_url) {
    rows.push({
      label: "来源链接",
      value: food.value.source_name || "打开来源页面",
      href: food.value.source_url,
    });
  }
  if (food.value.image_source_name) {
    rows.push({ label: "图片来源", value: food.value.image_source_name });
  }

  return rows;
});

const hasSourceInfo = computed(() => sourceRows.value.length > 0);

const actionHint = computed(() => {
  if (!food.value) return "";
  const distance = formatDistance(food.value);
  return mapUrl.value
    ? `可直接打开地图导航，当前距离为 ${distance}。`
    : "暂无精确坐标，可先返回列表或根据地址人工规划。";
});

const isSafeFoodsPath = (value: string) => {
  const trimmed = value.trim();
  if (!trimmed) return false;
  if (!trimmed.startsWith("/foods")) return false;
  if (trimmed.startsWith("//")) return false;
  if (/^[a-z][a-z\d+\-.]*:/i.test(trimmed)) return false;
  return (
    trimmed === "/foods" ||
    trimmed.startsWith("/foods?") ||
    trimmed.startsWith("/foods#") ||
    trimmed.startsWith("/foods/")
  );
};

const safeReturnTo = () => {
  const returnTo = Array.isArray(route.query.returnTo)
    ? route.query.returnTo[0]
    : route.query.returnTo;
  return typeof returnTo === "string" && isSafeFoodsPath(returnTo) ? returnTo : "/foods";
};

const backToFoods = () => {
  void router.push(safeReturnTo());
};

const addToPlan = () => {
  if (food.value) console.info("加入行程待接入", food.value);
};

const retryLoad = () => {
  void store.loadFoods(true);
};

watch(imageUrl, () => {
  imageLoadFailed.value = false;
});

onMounted(async () => {
  if (store.foods.items.length === 0) {
    await store.loadFoods(false);
  }
});
</script>

<style>
.food-detail-header {
  background:
    radial-gradient(circle at top right, rgba(43, 142, 240, 0.1), transparent 26%),
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}

.food-detail-back {
  display: inline-flex;
  min-height: 2.25rem;
  align-items: center;
  justify-content: center;
  padding: 0 0.9rem;
  color: #2563eb;
  background: rgba(233, 245, 255, 0.95);
  border: 1px solid rgba(191, 219, 254, 0.88);
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 800;
}

.food-detail-title {
  margin-top: 0.25rem;
  color: #0f172a;
  font-size: clamp(1.75rem, 3vw, 2.5rem);
  font-weight: 900;
  line-height: 1.12;
}

.food-detail-subtitle {
  max-width: 48rem;
  margin-top: 0.75rem;
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.9;
}

.food-detail-score-chip {
  display: grid;
  min-width: 8rem;
  gap: 0.2rem;
  padding: 0.9rem 1.1rem;
  color: #0f172a;
  background: #ffffff;
  border: 1px solid rgba(191, 219, 254, 0.86);
  border-radius: 1.25rem;
  box-shadow: 0 14px 30px rgba(28, 57, 87, 0.1);
}

.food-detail-score-chip span {
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 800;
}

.food-detail-score-chip strong {
  font-size: 1.55rem;
  font-weight: 900;
}

.food-detail-main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(18rem, 0.65fr);
  gap: 1.5rem;
  align-items: start;
}

.food-detail-image-card {
  position: relative;
  width: 100%;
  height: clamp(18rem, 28vw, 24rem);
  overflow: hidden;
  background:
    radial-gradient(circle at 20% 12%, rgba(249, 115, 22, 0.16), transparent 28%),
    linear-gradient(135deg, #f8fafc 0%, #eef6ff 100%);
  border: 1px solid rgba(214, 228, 241, 0.96);
  border-radius: 1.5rem;
  box-shadow: 0 14px 34px rgba(28, 57, 87, 0.1);
}

.food-detail-primary-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.food-detail-image-placeholder {
  display: flex;
  width: 100%;
  height: 100%;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  padding: 1.5rem;
  color: #64748b;
  background: transparent;
  text-align: center;
}

.food-detail-image-placeholder span {
  display: inline-flex;
  width: 5.5rem;
  height: 5.5rem;
  align-items: center;
  justify-content: center;
  color: #0f172a;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 999px;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
  font-weight: 900;
}

.food-detail-image-placeholder strong {
  color: #334155;
  font-size: 1rem;
}

.food-detail-image-placeholder small {
  color: #94a3b8;
  font-size: 0.78rem;
}

.food-detail-side-card {
  align-self: start;
}

.food-detail-label {
  color: #94a3b8;
  font-size: 0.74rem;
  font-weight: 900;
  letter-spacing: 0;
}

.food-detail-metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.food-detail-metric {
  display: flex;
  min-height: 5rem;
  flex-direction: column;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.85rem;
  background: #ffffff;
  border: 1px solid rgba(214, 228, 241, 0.88);
  border-radius: 1rem;
}

.food-detail-metric-accent {
  background: linear-gradient(135deg, #eff6ff, #f0fdfa);
  border-color: rgba(147, 197, 253, 0.72);
}

.food-detail-metric small {
  color: #94a3b8;
  font-size: 0.72rem;
  font-weight: 800;
}

.food-detail-metric strong {
  color: #0f172a;
  font-size: 1.15rem;
  font-weight: 900;
}

.food-detail-mini-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.food-detail-mini-summary span {
  display: inline-flex;
  min-height: 1.75rem;
  align-items: center;
  padding: 0 0.65rem;
  color: #2563eb;
  background: rgba(233, 245, 255, 0.95);
  border: 1px solid rgba(191, 219, 254, 0.82);
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 800;
}

.food-detail-content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(17rem, 0.34fr);
  gap: 1.5rem;
  align-items: start;
}

.food-detail-block {
  padding: 1.15rem;
  background:
    radial-gradient(circle at top right, rgba(43, 142, 240, 0.06), transparent 25%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 251, 255, 0.96));
  border: 1px solid rgba(214, 228, 241, 0.9);
  border-radius: 1.25rem;
  box-shadow: 0 10px 24px rgba(28, 57, 87, 0.06);
}

.food-detail-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.food-detail-section-head strong {
  color: #2563eb;
  font-size: 0.82rem;
  font-weight: 900;
}

.food-detail-reason-grid,
.food-detail-dish-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.food-detail-reason-pill,
.food-detail-dish-list span {
  display: inline-flex;
  align-items: center;
  min-height: 1.85rem;
  padding: 0 0.72rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 850;
}

.food-detail-reason-pill {
  color: #0f766e;
  background: rgba(240, 253, 250, 0.96);
  border: 1px solid rgba(94, 234, 212, 0.46);
}

.food-detail-dish-list span {
  color: #7c2d12;
  background: rgba(255, 247, 237, 0.96);
  border: 1px solid rgba(253, 186, 116, 0.52);
}

.food-detail-copy {
  color: #475569;
  font-size: 0.92rem;
  line-height: 1.9;
}

.food-detail-info-list {
  display: grid;
  gap: 0.75rem;
}

.food-detail-info-row {
  display: grid;
  grid-template-columns: 7rem minmax(0, 1fr);
  gap: 1rem;
  padding: 0.8rem 0.9rem;
  background: rgba(248, 250, 252, 0.84);
  border: 1px solid rgba(226, 232, 240, 0.82);
  border-radius: 1rem;
}

.food-detail-info-row span {
  color: #94a3b8;
  font-size: 0.76rem;
  font-weight: 850;
}

.food-detail-info-row strong,
.food-detail-info-row a {
  min-width: 0;
  color: #0f172a;
  font-size: 0.88rem;
  font-weight: 800;
  overflow-wrap: anywhere;
}

.food-detail-info-row a {
  color: #2563eb;
  text-decoration: none;
}

.food-detail-info-row a:hover {
  text-decoration: underline;
}

.food-detail-action-card {
  position: sticky;
  top: 4.5rem;
}

.food-detail-action-card h2 {
  margin-top: 0.55rem;
  color: #0f172a;
  font-size: 1.1rem;
  font-weight: 900;
}

.food-detail-action-card p {
  margin-top: 0.45rem;
  color: #64748b;
  font-size: 0.84rem;
  line-height: 1.75;
}

.food-detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.food-detail-actions-column {
  flex-direction: column;
  margin-top: 1rem;
}

.food-detail-action {
  display: inline-flex;
  min-height: 2.45rem;
  align-items: center;
  justify-content: center;
  padding: 0 0.95rem;
  color: #334155;
  background: #f8fafc;
  border: 1px solid rgba(203, 213, 225, 0.88);
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 850;
  text-decoration: none;
  transition:
    transform 0.18s ease,
    border-color 0.18s ease,
    background 0.18s ease;
}

.food-detail-action:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #ffffff;
  border-color: rgba(59, 130, 246, 0.42);
}

.food-detail-action:disabled {
  cursor: not-allowed;
  color: #94a3b8;
  background: #f1f5f9;
}

.food-detail-action-primary {
  color: #ffffff;
  background: linear-gradient(135deg, #2563eb, #0f766e);
  border-color: transparent;
}

@media (max-width: 1024px) {
  .food-detail-main-grid,
  .food-detail-content-grid {
    grid-template-columns: 1fr;
  }

  .food-detail-action-card {
    position: static;
  }
}

@media (max-width: 640px) {
  .food-detail-info-row {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }

  .food-detail-score-chip {
    width: 100%;
  }
}
</style>
