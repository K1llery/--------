<template>
  <div class="destination-detail-page space-y-6">
    <div v-if="error" class="alert-soft-error">{{ error }}</div>
    <div v-else-if="loading" class="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_360px] gap-6">
      <SkeletonCard />
      <SkeletonCard />
    </div>

    <template v-else-if="detail">
      <section class="destination-workbench-hero">
        <RealImage
          :src="detail.image_url"
          :alt="detail.name"
          :name="detail.name"
          :city="detail.city"
          :latitude="detail.latitude"
          :longitude="detail.longitude"
          :source-url="detail.source_url"
          class="destination-workbench-image"
        />
        <div class="destination-workbench-copy">
          <div class="destination-workbench-badges">
            <span>{{ categoryLabel(detail.category) }}</span>
            <span>{{ detail.city || "城市目的地" }}</span>
          </div>
          <h1>{{ detail.name }}</h1>
          <p>{{ detail.description || "暂无详细介绍，仍可进入路线、美食和日记联动查看。" }}</p>
          <div class="destination-workbench-actions">
            <RouterLink class="btn-soft-primary text-sm" :to="routeLink">规划路线</RouterLink>
            <RouterLink class="btn-soft-secondary text-sm" :to="foodLink">查周边美食</RouterLink>
            <button
              class="text-sm"
              :class="isFavorite ? 'btn-soft-secondary text-primary-700 bg-primary-50' : 'btn-soft-secondary'"
              type="button"
              @click="toggleFavorite"
            >
              {{ isFavorite ? "已收藏" : "收藏" }}
            </button>
          </div>
        </div>
      </section>

      <section class="destination-detail-grid">
        <main class="space-y-5">
          <section class="destination-metric-strip">
            <article>
              <span>资料评分</span>
              <strong>{{ metric(detail.rating) }}</strong>
            </article>
            <article>
              <span>平台热度</span>
              <strong>{{ metric(detail.heat) }}</strong>
            </article>
            <article>
              <span>浏览量</span>
              <strong>{{ detail.interaction_stats.total_views }}</strong>
            </article>
            <article>
              <span>用户评分</span>
              <strong>{{ metric(detail.interaction_stats.rating_avg) }}</strong>
              <small>{{ detail.interaction_stats.rating_count }} 人</small>
            </article>
          </section>

          <section class="card-elevated rounded-[24px] p-5 lg:p-6">
            <div class="destination-section-head">
              <div>
                <span class="route-panel-kicker">路线联动</span>
                <h2>地点信息与算法说明</h2>
              </div>
              <span class="route-summary-chip">{{ detail.source_name || "项目数据" }}</span>
            </div>
            <p class="destination-long-copy">{{ detail.address || detail.district || "暂无地址信息" }}</p>
            <p class="destination-long-copy">{{ detail.algorithm_explanation }}</p>
            <div class="destination-tag-row">
              <span v-for="tag in detail.tags ?? []" :key="tag">{{ tag }}</span>
            </div>
          </section>

          <section class="destination-panel-grid">
            <article class="destination-linked-panel">
              <div class="destination-section-head">
                <div>
                  <span class="route-panel-kicker">附近设施</span>
                  <h2>距离最近的服务点</h2>
                </div>
              </div>
              <div class="destination-mini-list">
                <div v-for="facility in detail.nearby_facilities.slice(0, 5)" :key="facility.code">
                  <strong>{{ facility.name }}</strong>
                  <span>{{ facility.facility_label || facility.facility_type }} · {{ facility.distance_km ?? "-" }} km</span>
                </div>
              </div>
            </article>

            <article class="destination-linked-panel">
              <div class="destination-section-head">
                <div>
                  <span class="route-panel-kicker">周边美食</span>
                  <h2>可衔接的餐饮</h2>
                </div>
              </div>
              <div class="destination-mini-list">
                <RouterLink
                  v-for="food in detail.nearby_foods.slice(0, 5)"
                  :key="food.source_id || food.name"
                  :to="`/foods/${food.source_id}`"
                >
                  <strong>{{ food.name }}</strong>
                  <span>{{ food.cuisine || "美食" }} · 评分 {{ metric(food.rating) }}</span>
                </RouterLink>
              </div>
            </article>
          </section>

          <section class="destination-linked-panel">
            <div class="destination-section-head">
              <div>
                <span class="route-panel-kicker">相关日记</span>
                <h2>从他人的路线经验继续看</h2>
              </div>
              <RouterLink class="home-inline-link" :to="`/diaries?destination=${encodeURIComponent(detail.name)}`">
                查看更多
              </RouterLink>
            </div>
            <div class="destination-diary-list">
              <RouterLink v-for="diary in detail.related_diaries" :key="diary.id" :to="`/diaries/${diary.id}`">
                <strong>{{ diary.title }}</strong>
                <span>{{ diary.views }} 浏览 · 评分 {{ metric(diary.rating_avg ?? diary.rating) }}</span>
                <p>{{ diary.content }}</p>
              </RouterLink>
            </div>
          </section>
        </main>

        <aside class="space-y-5">
          <section class="destination-rate-card">
            <span class="route-panel-kicker">我的评分</span>
            <h2>给这个目的地打分</h2>
            <div class="destination-rating-buttons" role="radiogroup" aria-label="目的地评分">
              <button
                v-for="score in scores"
                :key="score"
                type="button"
                :class="{ 'destination-rating-active': currentScore === score }"
                :disabled="ratingLoading"
                @click="rate(score)"
              >
                {{ score }}
              </button>
            </div>
            <p>
              {{ detail.interaction_stats.user_score ? `你已评分 ${detail.interaction_stats.user_score}` : "登录后可保存个人评分。" }}
            </p>
          </section>

          <section class="destination-source-card">
            <span class="route-panel-kicker">来源与坐标</span>
            <h2>{{ detail.city }} · {{ detail.district || "坐标定位" }}</h2>
            <dl>
              <div>
                <dt>纬度</dt>
                <dd>{{ detail.latitude.toFixed(6) }}</dd>
              </div>
              <div>
                <dt>经度</dt>
                <dd>{{ detail.longitude.toFixed(6) }}</dd>
              </div>
              <div>
                <dt>热度指标</dt>
                <dd>{{ detail.heat_metric || "平台热度" }}</dd>
              </div>
            </dl>
            <a v-if="detail.source_url" :href="detail.source_url" target="_blank" rel="noreferrer">
              查看原始来源
            </a>
          </section>
        </aside>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";

import { api } from "../api/client";
import RealImage from "../components/RealImage.vue";
import SkeletonCard from "../components/SkeletonCard.vue";
import { useAuthStore } from "../stores/auth";
import { useToastStore } from "../stores/toast";
import type { DestinationDetailResponse } from "../types/api";

const route = useRoute();
const auth = useAuthStore();
const toast = useToastStore();
const detail = ref<DestinationDetailResponse | null>(null);
const loading = ref(false);
const ratingLoading = ref(false);
const error = ref("");
const scores = [1, 2, 3, 4, 5];

const currentScore = computed(() => Math.round(detail.value?.interaction_stats.user_score ?? 0));
const isFavorite = computed(() =>
  detail.value ? Boolean(auth.user?.favorite_destination_ids?.includes(detail.value.source_id)) : false,
);

const routeLink = computed(() => "/routes");
const foodLink = computed(() => {
  if (!detail.value) return "/foods";
  const params = new URLSearchParams({
    anchorType: "destination",
    anchorName: detail.value.name,
    anchorId: `destination:${detail.value.name}`,
    lat: String(detail.value.latitude),
    lng: String(detail.value.longitude),
  });
  return `/foods?${params.toString()}`;
});

const metric = (value: number | null | undefined) => (value === null || value === undefined ? "-" : value);
const categoryLabel = (value: string) => {
  if (value === "campus") return "高校 / 校园";
  if (value === "shopping") return "商场 / 商圈";
  return "景点";
};

const sourceId = () => {
  const raw = route.params.sourceId;
  return Array.isArray(raw) ? raw[0] : raw;
};

const load = async () => {
  const id = sourceId();
  if (!id) return;
  loading.value = true;
  error.value = "";
  try {
    const { data } = await api.get<DestinationDetailResponse>(`/destinations/${encodeURIComponent(id)}`);
    detail.value = data;
    const viewResponse = await api.post<DestinationDetailResponse>(`/destinations/${encodeURIComponent(id)}/view`);
    detail.value = viewResponse.data;
  } catch {
    error.value = "目的地详情加载失败。";
  } finally {
    loading.value = false;
  }
};

const toggleFavorite = async () => {
  if (!detail.value) return;
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  const wasFavorite = isFavorite.value;
  await auth.toggleDestinationFavorite(detail.value.source_id);
  toast.success(wasFavorite ? "已取消收藏" : "已收藏目的地");
};

const rate = async (score: number) => {
  if (!detail.value) return;
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  ratingLoading.value = true;
  try {
    const { data } = await api.post<DestinationDetailResponse>(
      `/destinations/${encodeURIComponent(detail.value.source_id)}/rate`,
      { score },
    );
    detail.value = data;
    toast.success("评分已保存");
  } catch {
    toast.error("评分失败，请稍后重试");
  } finally {
    ratingLoading.value = false;
  }
};

onMounted(load);
watch(() => route.params.sourceId, load);
</script>

<style scoped>
.destination-workbench-hero {
  position: relative;
  display: grid;
  min-height: 420px;
  overflow: hidden;
  border-radius: 28px;
  background: #142738;
  box-shadow: 0 28px 78px rgba(20, 39, 56, 0.2);
}

.destination-workbench-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.82;
}

.destination-workbench-hero::after {
  position: absolute;
  inset: 0;
  content: "";
  background: linear-gradient(90deg, rgba(16, 33, 49, 0.9), rgba(16, 33, 49, 0.28));
}

.destination-workbench-copy {
  position: relative;
  z-index: 1;
  display: flex;
  max-width: 760px;
  flex-direction: column;
  justify-content: flex-end;
  padding: clamp(1.4rem, 4vw, 3rem);
  color: #ffffff;
}

.destination-workbench-badges,
.destination-workbench-actions,
.destination-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.destination-workbench-badges span,
.destination-tag-row span {
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  padding: 0.45rem 0.75rem;
  font-size: 0.78rem;
  font-weight: 700;
}

.destination-workbench-copy h1 {
  margin: 1rem 0 0;
  font-size: clamp(2.1rem, 5vw, 4.6rem);
  font-weight: 850;
  letter-spacing: 0;
  line-height: 1.05;
}

.destination-workbench-copy p {
  max-width: 46rem;
  margin: 1rem 0 1.4rem;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.8;
}

.destination-detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 1.5rem;
  align-items: start;
}

.destination-metric-strip,
.destination-panel-grid {
  display: grid;
  gap: 1rem;
}

.destination-metric-strip {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.destination-metric-strip article,
.destination-linked-panel,
.destination-rate-card,
.destination-source-card {
  border: 1px solid rgba(176, 202, 222, 0.76);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 20px 56px rgba(45, 74, 104, 0.08);
}

.destination-metric-strip article {
  min-height: 112px;
  padding: 1rem;
}

.destination-metric-strip span,
.destination-metric-strip small {
  display: block;
  color: #6b7d91;
  font-size: 0.78rem;
}

.destination-metric-strip strong {
  display: block;
  margin-top: 0.45rem;
  color: #172331;
  font-size: 1.8rem;
  font-weight: 850;
}

.destination-section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.destination-section-head h2 {
  margin: 0.2rem 0 0;
  color: #172331;
  font-size: 1.08rem;
  font-weight: 800;
}

.destination-long-copy {
  color: #637589;
  line-height: 1.8;
}

.destination-tag-row {
  margin-top: 1rem;
}

.destination-tag-row span {
  color: #1475c4;
  background: #e8f4ff;
}

.destination-panel-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.destination-linked-panel,
.destination-rate-card,
.destination-source-card {
  padding: 1.25rem;
}

.destination-mini-list,
.destination-diary-list {
  display: grid;
  gap: 0.8rem;
}

.destination-mini-list > div,
.destination-mini-list > a,
.destination-diary-list > a {
  display: block;
  border-radius: 16px;
  background: #f7fbff;
  padding: 0.9rem 1rem;
}

.destination-mini-list strong,
.destination-mini-list span,
.destination-diary-list strong,
.destination-diary-list span,
.destination-diary-list p {
  display: block;
}

.destination-mini-list strong,
.destination-diary-list strong {
  overflow: hidden;
  color: #263647;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.destination-mini-list span,
.destination-diary-list span,
.destination-diary-list p,
.destination-rate-card p {
  margin-top: 0.25rem;
  color: #6b7d91;
  font-size: 0.84rem;
}

.destination-diary-list p {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.destination-rate-card {
  position: sticky;
  top: 5rem;
}

.destination-rate-card h2,
.destination-source-card h2 {
  margin: 0.25rem 0 1rem;
  color: #172331;
  font-size: 1.05rem;
  font-weight: 800;
}

.destination-rating-buttons {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.45rem;
}

.destination-rating-buttons button {
  min-height: 42px;
  border: 1px solid #c7d9e8;
  border-radius: 14px;
  color: #1475c4;
  background: #f4f9ff;
  font-weight: 800;
}

.destination-rating-buttons button:hover,
.destination-rating-active {
  color: #ffffff !important;
  background: #1475c4 !important;
}

.destination-source-card dl {
  display: grid;
  gap: 0.75rem;
  margin: 0;
}

.destination-source-card div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 1px solid #eef3f8;
  padding-bottom: 0.65rem;
}

.destination-source-card dt {
  color: #6b7d91;
}

.destination-source-card dd {
  margin: 0;
  color: #263647;
  font-weight: 800;
}

.destination-source-card a {
  display: inline-flex;
  margin-top: 1rem;
  color: #1475c4;
  font-weight: 800;
}

@media (max-width: 1100px) {
  .destination-detail-grid {
    grid-template-columns: 1fr;
  }

  .destination-rate-card {
    position: static;
  }
}

@media (max-width: 720px) {
  .destination-workbench-hero {
    min-height: 520px;
  }

  .destination-workbench-hero::after {
    background: linear-gradient(180deg, rgba(16, 33, 49, 0.28), rgba(16, 33, 49, 0.92));
  }

  .destination-metric-strip,
  .destination-panel-grid {
    grid-template-columns: 1fr;
  }
}
</style>
