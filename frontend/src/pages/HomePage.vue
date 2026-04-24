<template>
  <div class="space-y-6">
    <!-- Hero -->
    <section
      class="relative bg-white rounded-3xl card-elevated overflow-hidden"
    >
      <!-- Floating blobs -->
      <div class="gradient-blob w-72 h-72 bg-primary-400 -top-20 -left-20" />
      <div
        class="gradient-blob w-56 h-56 bg-accent-400 -bottom-16 right-10"
        style="animation-delay: -3s"
      />
      <div class="relative grid lg:grid-cols-2 gap-0">
        <!-- Copy -->
        <div class="p-8 lg:p-10 flex flex-col justify-center">
          <span
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary-50 text-primary-700 text-xs font-semibold w-fit mb-4"
          >
            <svg
              class="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z"
              />
            </svg>
            City Picks
          </span>
          <h2
            class="text-3xl lg:text-4xl font-bold text-gray-900 leading-tight"
          >
            北上广深高校与景区，<br class="hidden sm:block" />一站式安排行程
          </h2>
          <p class="mt-3 text-gray-500 text-base leading-relaxed">
            从热门地标、城市商圈到经典校园，先挑城市，再看精选目的地、美食与路线。
          </p>
          <!-- City tabs -->
          <div class="flex flex-wrap gap-2 mt-6">
            <button
              v-for="city in cities"
              :key="city"
              class="btn-press px-4 py-2 rounded-2xl text-sm font-medium transition-all duration-200"
              :class="
                selectedCity === city
                  ? 'bg-gradient-to-r from-primary-600 to-accent-500 text-white shadow-lg shadow-primary-500/30'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              "
              @click="selectedCity = city"
            >
              {{ city }}
            </button>
          </div>
          <!-- Actions -->
          <div class="flex flex-wrap gap-3 mt-6">
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
                stroke-width="2"
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
              >查看地图</RouterLink
            >
            <button
              v-if="!auth.isLoggedIn"
              class="text-sm text-primary-600 font-medium hover:text-primary-700 transition-colors"
              @click="auth.openAuthModal('login')"
            >
              登录保存行程 →
            </button>
          </div>
        </div>
        <!-- Hero image -->
        <div
          class="relative min-h-[300px] lg:min-h-[400px] bg-gray-100 hero-shimmer"
        >
          <RealImage
            v-if="heroDestination"
            :src="heroDestination.image_url"
            :alt="heroDestination.name"
            :name="heroDestination.name"
            :city="heroDestination.city"
            :latitude="heroDestination.latitude"
            :longitude="heroDestination.longitude"
            :source-url="heroDestination.source_url"
            class="absolute inset-0 w-full h-full object-cover"
          />
          <div
            v-if="heroDestination"
            class="absolute left-4 right-4 bottom-4 p-4 rounded-2xl bg-white/80 backdrop-blur-lg border-0 shadow-md shadow-gray-200/50 shadow-lg"
          >
            <p class="text-xs text-primary-600 font-semibold">
              {{ heroDestination.city }} ·
              {{ categoryLabel(heroDestination.category) }}
            </p>
            <h3 class="text-lg font-bold text-gray-900 mt-0.5">
              {{ heroDestination.name }}
            </h3>
            <p class="text-sm text-gray-500 mt-1 line-clamp-2">
              {{ heroDestination.description }}
            </p>
          </div>
        </div>
      </div>
    </section>
    <!-- My Favorites -->
    <section
      v-if="auth.isLoggedIn"
      v-reveal
      class="bg-white rounded-3xl card-elevated p-6"
    >
      <div class="flex items-start gap-3">
        <span class="section-accent h-6 mt-1" />
        <div>
          <h2 class="text-lg font-bold text-gray-900">我的收藏</h2>
          <p class="text-sm text-gray-500 mt-1">
            当前账号的收藏和最近一次登录信息会保留在本地。
          </p>
        </div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5 stagger-children">
        <div
          class="group relative overflow-hidden p-5 rounded-2xl bg-gradient-to-br from-primary-50 via-white to-primary-50/30 border-0 shadow-md shadow-gray-200/50 hover:shadow-lg hover:shadow-primary-500/10 transition-all"
        >
          <div
            class="absolute -top-4 -right-4 w-20 h-20 rounded-full bg-primary-200/30 blur-xl group-hover:bg-primary-300/40 transition-colors"
          />
          <div class="relative flex items-start gap-3">
            <div
              class="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 text-white flex items-center justify-center shadow-lg shadow-primary-500/25 flex-shrink-0"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z"
                />
              </svg>
            </div>
            <div class="min-w-0">
              <p class="text-2xl font-bold text-primary-700 leading-none">
                {{ auth.favoriteDestinationCount }}
              </p>
              <p class="text-xs text-gray-500 mt-2">已收藏目的地</p>
            </div>
          </div>
        </div>
        <div
          class="group relative overflow-hidden p-5 rounded-2xl bg-gradient-to-br from-accent-50 via-white to-accent-50/30 border-0 shadow-md shadow-gray-200/50 hover:shadow-lg hover:shadow-accent-500/10 transition-all"
        >
          <div
            class="absolute -top-4 -right-4 w-20 h-20 rounded-full bg-accent-200/30 blur-xl group-hover:bg-accent-300/40 transition-colors"
          />
          <div class="relative flex items-start gap-3">
            <div
              class="w-10 h-10 rounded-2xl bg-gradient-to-br from-accent-500 to-accent-600 text-white flex items-center justify-center shadow-lg shadow-accent-500/25 flex-shrink-0"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M9 6.75V15m6-6v8.25m.503 3.498 4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934a1.12 1.12 0 0 1-1.006 0L9.503 3.252a1.125 1.125 0 0 0-1.006 0L3.622 5.689A1.125 1.125 0 0 0 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934a1.12 1.12 0 0 1 1.006 0l4.994 2.497c.317.158.69.158 1.006 0Z"
                />
              </svg>
            </div>
            <div class="min-w-0">
              <p class="text-2xl font-bold text-accent-600 leading-none">
                {{ auth.favoriteRouteCount }}
              </p>
              <p class="text-xs text-gray-500 mt-2">已收藏路线</p>
            </div>
          </div>
        </div>
        <div
          class="relative overflow-hidden p-5 rounded-2xl bg-gradient-to-br from-gray-50 via-white to-gray-50/30 border-0 shadow-md shadow-gray-200/50 hover:shadow-md hover:shadow-slate-500/10 transition-all"
        >
          <div class="flex items-start gap-3">
            <div
              class="w-10 h-10 rounded-2xl bg-gradient-to-br from-slate-500 to-slate-700 text-white flex items-center justify-center shadow-lg shadow-slate-500/25 text-sm font-bold flex-shrink-0"
            >
              {{ (auth.user?.display_name || "U").slice(0, 1).toUpperCase() }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-gray-900 truncate">
                {{ auth.user?.display_name }}
              </p>
              <p class="text-[11px] text-gray-500 mt-1 truncate">
                最近登录 · {{ auth.user?.last_login_at || "首次进入" }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
    <!-- Cities -->
    <section v-reveal="100" class="bg-white rounded-3xl card-elevated p-6">
      <div class="flex items-start gap-3">
        <span class="section-accent h-6 mt-1" />
        <div>
          <h2 class="text-lg font-bold text-gray-900">热门城市</h2>
          <p class="text-sm text-gray-500 mt-1">
            切换城市后，首页推荐和地图浏览都会联动更新。
          </p>
        </div>
      </div>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-5 stagger-children">
        <button
          v-for="city in cityCards"
          :key="city.name"
          v-tilt
          class="text-left p-4 rounded-2xl border-0 shadow-md shadow-gray-200/50 transition-all duration-200"
          :class="
            selectedCity === city.name
              ? 'bg-primary-50 shadow-md shadow-primary-500/10'
              : 'bg-white hover:shadow-sm'
          "
          @click="selectedCity = city.name"
        >
          <h3 class="font-semibold text-gray-900">{{ city.name }}</h3>
          <p class="text-sm text-gray-500 mt-1">{{ city.tagline }}</p>
          <p class="text-xs text-primary-600 font-medium mt-2">
            {{ city.count }} 个精选地点
          </p>
        </button>
      </div>
    </section>
    <!-- Featured preview -->
    <section v-reveal="200" class="bg-white rounded-3xl card-elevated p-6">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-3">
          <span class="section-accent h-6 mt-1" />
          <div>
            <h2 class="text-lg font-bold text-gray-900">
              {{ selectedCity }}精选预览
            </h2>
            <p class="text-sm text-gray-500 mt-1">
              先看最值得逛的景点、商圈和校园
            </p>
          </div>
        </div>
        <RouterLink
          to="/destinations"
          class="group inline-flex items-center gap-1 text-sm text-primary-600 font-medium hover:text-primary-700 transition-colors whitespace-nowrap"
        >
          查看全部
          <svg
            class="w-4 h-4 group-hover:translate-x-0.5 transition-transform"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
            />
          </svg>
        </RouterLink>
      </div>
      <div
        v-if="loading"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-5"
      >
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
          class="group rounded-2xl bg-white overflow-hidden cursor-pointer glow-border shadow-md shadow-gray-200/50 transition-all duration-300"
          @click="store.selectDestination(item)"
        >
          <div class="relative h-40 bg-gray-100 overflow-hidden">
            <RealImage
              :src="item.image_url"
              :alt="item.name"
              :name="item.name"
              :city="item.city"
              :latitude="item.latitude"
              :longitude="item.longitude"
              :source-url="item.source_url"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          </div>
          <div class="p-4">
            <h3 class="font-semibold text-gray-900 text-sm">{{ item.name }}</h3>
            <p class="text-xs text-gray-500 mt-1">
              {{ categoryLabel(item.category) }} · {{ item.city }}
            </p>
            <div class="flex gap-2 mt-2">
              <span
                class="text-xs px-2 py-0.5 rounded-full bg-primary-50 text-primary-600 font-medium"
                >评分 {{ item.rating ?? "—" }}</span
              >
              <span
                class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600"
                >热度 {{ item.heat ?? "—" }}</span
              >
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
import EmptyState from "../components/EmptyState.vue";
import RealImage from "../components/RealImage.vue";
import SkeletonCard from "../components/SkeletonCard.vue";
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
const heroDestination = computed(
  () => featuredPreview.value[0] ?? featured.value[0] ?? null,
);
const categoryLabel = (value: string) => {
  if (value === "shopping") return "商场/商圈";
  if (value === "campus") return "校园";
  return "景点";
};
onMounted(() => {
  store.loadFeaturedDestinations(false);
});
</script>
