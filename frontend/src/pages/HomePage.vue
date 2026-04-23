<template>
  <div class="page-grid">
    <section class="panel-card hero-card">
      <div class="hero-copy">
        <span class="eyebrow">City Picks</span>
        <h2>北上广深高校与景区，一站式安排行程</h2>
        <p>从热门地标、城市商圈到经典校园，先挑城市，再看精选目的地、美食与路线。</p>
        <div class="segment-tabs">
          <button
            v-for="city in cities"
            :key="city"
            class="filter-chip"
            :class="{ active: selectedCity === city }"
            @click="selectedCity = city"
          >
            {{ city }}
          </button>
        </div>
        <div class="hero-actions">
          <RouterLink class="primary-btn" to="/destinations">浏览目的地</RouterLink>
          <RouterLink class="secondary-btn" to="/routes">查看地图</RouterLink>
          <button v-if="!auth.isLoggedIn" class="ghost-btn" @click="auth.openAuthModal('login')">
            登录保存行程
          </button>
          <button v-if="!auth.isLoggedIn" class="ghost-btn" @click="auth.openAuthModal('register')">
            快速注册
          </button>
        </div>
      </div>
      <div class="hero-preview">
        <RealImage
          v-if="heroDestination"
          :src="heroDestination.image_url"
          :alt="heroDestination.name"
          :name="heroDestination.name"
          :city="heroDestination.city"
          :latitude="heroDestination.latitude"
          :longitude="heroDestination.longitude"
          :source-url="heroDestination.source_url"
          class="detail-image hero-image"
        />
        <div v-if="heroDestination" class="hero-overlay">
          <p class="hero-kicker">
            {{ heroDestination.city }} · {{ categoryLabel(heroDestination.category) }}
          </p>
          <h3>{{ heroDestination.name }}</h3>
          <p>{{ heroDestination.description }}</p>
        </div>
      </div>
    </section>

    <section v-if="auth.isLoggedIn" class="panel-card">
      <div class="section-top">
        <div>
          <h2>我的收藏</h2>
          <p>当前账号的收藏和最近一次登录信息会保留在本地。</p>
        </div>
      </div>
      <div class="city-grid">
        <div class="city-card selected">
          <h3>{{ auth.favoriteDestinationCount }}</h3>
          <p>已收藏目的地</p>
          <span>下次打开还能继续看</span>
        </div>
        <div class="city-card selected">
          <h3>{{ auth.favoriteRouteCount }}</h3>
          <p>已收藏路线</p>
          <span>适合答辩时直接展示历史路线</span>
        </div>
        <div class="city-card">
          <h3>{{ auth.user?.display_name }}</h3>
          <p>最近登录用户</p>
          <span>{{ auth.user?.last_login_at || "首次进入" }}</span>
        </div>
      </div>
    </section>

    <section class="panel-card">
      <div class="section-top">
        <div>
          <h2>热门城市</h2>
          <p>切换城市后，首页推荐和地图浏览都会联动更新。</p>
        </div>
      </div>
      <div class="city-grid">
        <button
          v-for="city in cityCards"
          :key="city.name"
          class="city-card"
          :class="{ selected: selectedCity === city.name }"
          @click="selectedCity = city.name"
        >
          <h3>{{ city.name }}</h3>
          <p>{{ city.tagline }}</p>
          <span>{{ city.count }} 个精选地点</span>
        </button>
      </div>
    </section>

    <section class="panel-card">
      <div class="section-top">
        <div>
          <h2>{{ selectedCity }}精选预览</h2>
          <p>先看最值得逛的景点、商圈和校园，再进入详情页做筛选。</p>
        </div>
        <RouterLink class="text-link" to="/destinations">查看全部</RouterLink>
      </div>

      <div v-if="loading" class="status-card">正在加载城市精选...</div>
      <div v-else-if="error" class="status-card error-card">{{ error }}</div>
      <div v-else class="card-grid">
        <article
          v-for="item in featuredPreview"
          :key="item.source_id"
          class="item-card media-card"
          @click="store.selectDestination(item)"
        >
          <RealImage
            :src="item.image_url"
            :alt="item.name"
            :name="item.name"
            :city="item.city"
            :latitude="item.latitude"
            :longitude="item.longitude"
            :source-url="item.source_url"
            class="media-thumb"
          />
          <div class="media-body">
            <h3>{{ item.name }}</h3>
            <p>{{ categoryLabel(item.category) }} · {{ item.city }}</p>
            <p>评分 {{ item.rating ?? "待补充" }} · 热度 {{ item.heat ?? "待补充" }}</p>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import RealImage from "../components/RealImage.vue";
import { useAuthStore } from "../stores/auth";
import { useTravelStore } from "../stores/travel";

const store = useTravelStore();
const auth = useAuthStore();
const selectedCity = ref("北京");
const cities = ["北京", "上海", "广州", "深圳"];

const featured = computed(() => store.destinations.items);
const loading = computed(() => store.destinations.loading);
const error = computed(() => store.destinations.error);

const cityCards = computed(() =>
  cities.map((city) => ({
    name: city,
    count: featured.value.filter((item) => item.city === city).length,
    tagline:
      city === "北京"
        ? "皇家古迹与高校密集"
        : city === "上海"
          ? "江景地标与都市校园"
          : city === "广州"
            ? "岭南风貌与商圈漫游"
            : "海滨创意与城市新景",
  })),
);

const featuredPreview = computed(() =>
  featured.value.filter((item) => item.city === selectedCity.value).slice(0, 4),
);

const heroDestination = computed(() => featuredPreview.value[0] ?? featured.value[0] ?? null);

const categoryLabel = (value: string) => {
  if (value === "shopping") return "商场/商圈";
  if (value === "campus") return "校园";
  return "景点";
};

onMounted(() => {
  store.loadFeaturedDestinations(false);
});
</script>
