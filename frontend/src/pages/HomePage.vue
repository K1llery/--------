<template>
  <div class="space-y-6">
    <section class="relative overflow-hidden rounded-[28px] card-elevated home-hero-shell">
      <div class="home-hero-grid">
        <div class="p-7 lg:p-10 flex flex-col justify-center gap-6">
          <div class="flex items-center gap-3">
            <span class="home-brand-badge">
              <img :src="brandLogoUrl" alt="优途" class="home-brand-badge-logo" />
            </span>
            <div>
              <p class="text-xs font-semibold tracking-[0.18em] text-sky-700 uppercase m-0">
                优途
              </p>
              <p class="text-sm text-slate-500 mt-1 mb-0">城市探索与路线规划</p>
            </div>
          </div>

          <div class="space-y-3">
            <h1 class="text-3xl lg:text-[3.1rem] font-bold text-slate-950 leading-tight">
              用更清晰的路线和场景入口，安排你的城市探索
            </h1>
            <p class="max-w-2xl text-base lg:text-lg text-slate-600 leading-8">
              在北京、上海、广州、深圳之间切换，统一浏览目的地、美食、设施和路线规划，把校园与城市旅行都放进一套顺手的工具里。
            </p>
          </div>

          <div class="flex flex-wrap gap-3">
            <RouterLink
              to="/destinations"
              v-ripple
              class="btn-soft-primary inline-flex items-center gap-2 text-sm"
            >
              浏览目的地
              <svg
                class="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
                />
              </svg>
            </RouterLink>
            <RouterLink
              to="/routes"
              v-ripple
              class="btn-soft-secondary inline-flex items-center gap-2 text-sm"
            >
              开始导航
            </RouterLink>
            <button
              v-if="!auth.isLoggedIn"
              class="home-text-action"
              type="button"
              @click="auth.openAuthModal('login')"
            >
              登录后同步你的收藏与路线
            </button>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <article class="home-metric-card">
              <span>覆盖城市</span>
              <strong>{{ cities.length }}</strong>
              <small>北京、上海、广州、深圳</small>
            </article>
            <article class="home-metric-card">
              <span>精选地点</span>
              <strong>{{ featured.length }}</strong>
              <small>持续用于推荐、搜索与路线规划</small>
            </article>
            <article class="home-metric-card">
              <span>{{ auth.isLoggedIn ? "我的收藏" : "核心能力" }}</span>
              <strong>{{ auth.isLoggedIn ? auth.favoriteDestinationCount + auth.favoriteRouteCount : 5 }}</strong>
              <small>
                {{ auth.isLoggedIn ? "地点收藏与路线快照已接入" : "推荐、导航、设施、规划、日记" }}
              </small>
            </article>
          </div>
        </div>

        <div class="relative min-h-[340px] lg:min-h-[480px]">
          <div class="home-hero-visual">
            <RealImage
              v-if="heroDestination"
              :src="heroDestination.image_url"
              :alt="heroDestination.name"
              :name="heroDestination.name"
              :city="heroDestination.city"
              :latitude="heroDestination.latitude"
              :longitude="heroDestination.longitude"
              :source-url="heroDestination.source_url"
              class="absolute inset-0 h-full w-full object-cover"
            />
            <div v-if="heroDestination" class="home-hero-overlay">
              <div class="home-hero-overlay-top">
                <span class="home-hero-chip">{{ heroDestination.city }}</span>
                <span class="home-hero-chip home-hero-chip-accent">
                  {{ categoryLabel(heroDestination.category) }}
                </span>
              </div>
              <div>
                <h2 class="text-xl font-bold text-white">{{ heroDestination.name }}</h2>
                <p class="mt-2 text-sm leading-6 text-white/82 line-clamp-3">
                  {{ heroDestination.description }}
                </p>
              </div>
            </div>
          </div>

          <aside class="home-hero-sidecard">
            <p class="text-xs font-semibold tracking-[0.16em] uppercase text-sky-700 m-0">
              今日推荐城市
            </p>
            <h3 class="text-lg font-bold text-slate-900 mt-2 mb-1">{{ selectedCity }}</h3>
            <p class="text-sm text-slate-500 leading-6 m-0">
              先看精选地点，再切进地图导航和附近设施，整条体验会更连贯。
            </p>
            <div class="mt-4 flex flex-wrap gap-2">
              <button
                v-for="city in cities"
                :key="city"
                class="home-city-chip"
                :class="{ 'home-city-chip-active': selectedCity === city }"
                @click="selectedCity = city"
              >
                {{ city }}
              </button>
            </div>
          </aside>
        </div>
      </div>
    </section>

    <section v-reveal class="card-elevated rounded-[24px] p-6">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">城市入口</p>
          <h2 class="text-xl font-bold text-slate-950 mt-1">从场景开始组织路线与地点</h2>
          <p class="text-sm text-slate-500 mt-2">
            每个城市都可以直接进入目的地浏览、地图导航和设施查询，不需要重复找入口。
          </p>
        </div>
        <RouterLink to="/search" class="home-inline-link">去搜索地点</RouterLink>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mt-5">
        <button
          v-for="city in cityCards"
          :key="city.name"
          v-tilt
          class="home-city-card"
          :class="{ 'home-city-card-active': selectedCity === city.name }"
          @click="selectedCity = city.name"
        >
          <div class="home-city-card-top">
            <strong>{{ city.name }}</strong>
            <span>{{ city.count }} 个精选地点</span>
          </div>
          <p>{{ city.tagline }}</p>
          <div class="home-city-card-footer">
            <span>浏览推荐</span>
            <span>查看路线</span>
          </div>
        </button>
      </div>
    </section>

    <section v-reveal="120" class="card-elevated rounded-[24px] p-6">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">核心能力</p>
          <h2 class="text-xl font-bold text-slate-950 mt-1">把推荐、导航和规划收成一套工具</h2>
          <p class="text-sm text-slate-500 mt-2">
            首页直接说明平台能做什么，避免看起来像一组松散页面。
          </p>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 mt-5">
        <RouterLink
          v-for="item in capabilityCards"
          :key="item.title"
          :to="item.to"
          class="home-capability-card"
        >
          <span class="home-capability-index">{{ item.index }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
          <span class="home-capability-link">{{ item.action }}</span>
        </RouterLink>
      </div>
    </section>

    <section
      v-if="auth.isLoggedIn"
      v-reveal="180"
      class="card-elevated rounded-[24px] p-6 home-personal-shell"
    >
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">我的优途</p>
          <h2 class="text-xl font-bold text-slate-950 mt-1">把收藏、路线和计划接回到你的账号</h2>
          <p class="text-sm text-slate-500 mt-2">
            已登录状态优先展示个人信息，让首页有真正的个性化感，而不是统一静态内容。
          </p>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
        <article class="home-personal-card">
          <span>收藏地点</span>
          <strong>{{ auth.favoriteDestinationCount }}</strong>
          <p>已保存到账号，讲解时可以随时打开。</p>
        </article>
        <article class="home-personal-card">
          <span>收藏路线</span>
          <strong>{{ auth.favoriteRouteCount }}</strong>
          <p>路线规划结果可以直接沉淀为可复用快照。</p>
        </article>
        <article class="home-personal-card">
          <span>推荐动作</span>
          <strong>继续规划</strong>
          <p>优先从地图导航页继续完成校园或城市路线演示。</p>
        </article>
      </div>
    </section>

    <section v-reveal="220" class="card-elevated rounded-[24px] p-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="home-section-kicker">{{ selectedCity }}精选预览</p>
          <h2 class="text-xl font-bold text-slate-950 mt-1">先看值得去的地点，再决定路线</h2>
          <p class="text-sm text-slate-500 mt-2">
            当前城市的精选地点会优先展示，方便从推荐直接切到路线与收藏。
          </p>
        </div>
        <RouterLink to="/destinations" class="home-inline-link">查看全部</RouterLink>
      </div>

      <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-5">
        <SkeletonCard v-for="n in 4" :key="n" />
      </div>
      <div v-else-if="error" class="mt-5 alert-soft-error">{{ error }}</div>
      <div
        v-else
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-5 stagger-children"
      >
        <article
          v-for="item in featuredPreview"
          :key="item.source_id"
          v-tilt
          class="home-preview-card group"
          @click="store.selectDestination(item)"
        >
          <div class="relative h-44 overflow-hidden bg-slate-100">
            <RealImage
              :src="item.image_url"
              :alt="item.name"
              :name="item.name"
              :city="item.city"
              :latitude="item.latitude"
              :longitude="item.longitude"
              :source-url="item.source_url"
              class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          </div>
          <div class="p-4">
            <h3 class="text-base font-bold text-slate-900">{{ item.name }}</h3>
            <p class="text-sm text-slate-500 mt-1">
              {{ categoryLabel(item.category) }} · {{ item.city }}
            </p>
            <div class="flex flex-wrap gap-2 mt-3">
              <span class="home-score-pill">评分 {{ item.rating ?? "—" }}</span>
              <span class="home-heat-pill">热度 {{ item.heat ?? "—" }}</span>
            </div>
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
import SkeletonCard from "../components/SkeletonCard.vue";
import { useAuthStore } from "../stores/auth";
import { useTravelStore } from "../stores/travel";

const brandLogoUrl = "/brands/youtu.png";
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
        ? "皇家古迹、城市地标与高校校园集中分布。"
        : city === "上海"
          ? "江景地标、商圈与都市校园切换自然。"
          : city === "广州"
            ? "岭南风貌、商圈漫游与生活服务更完整。"
            : "滨海城市、创意街区与现代园区结合明显。",
  })),
);

const capabilityCards = [
  {
    index: "01",
    title: "目的地推荐",
    description: "按城市浏览景点、商圈和校园，快速形成候选列表。",
    action: "查看推荐",
    to: "/destinations",
  },
  {
    index: "02",
    title: "地图导航",
    description: "基于本地图结构完成路线规划、设施查询和讲解演示。",
    action: "进入导航",
    to: "/routes",
  },
  {
    index: "03",
    title: "设施查询",
    description: "按场景查看周边设施，支持从当前路线继续衔接使用。",
    action: "查附近设施",
    to: "/facilities",
  },
  {
    index: "04",
    title: "旅游规划",
    description: "把地点和路线组织成可复用的个性化行程计划。",
    action: "开始规划",
    to: "/plan",
  },
  {
    index: "05",
    title: "旅游日记",
    description: "保留内容分享入口，形成从推荐到记录的完整闭环。",
    action: "查看日记",
    to: "/diaries",
  },
];

const featuredPreview = computed(() =>
  featured.value.filter((item) => item.city === selectedCity.value).slice(0, 4),
);

const heroDestination = computed(() => featuredPreview.value[0] ?? featured.value[0] ?? null);

const categoryLabel = (value: string) => {
  if (value === "shopping") return "商场 / 商圈";
  if (value === "campus") return "校园";
  return "景点";
};

onMounted(() => {
  store.loadFeaturedDestinations(false);
});
</script>
