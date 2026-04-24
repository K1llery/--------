<template>
  <div class="flex min-h-screen bg-slate-50">
    <!-- Sidebar -->
    <aside
      class="hidden lg:flex w-[280px] flex-col glass-panel border-0 shadow-md shadow-gray-200/50 sticky top-0 h-screen overflow-y-auto"
    >
      <!-- Brand -->
      <div class="p-6 pb-4">
        <div class="flex items-center gap-2.5 mb-1">
          <div
            class="w-9 h-9 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-500/25"
          >
            <svg
              class="w-5 h-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418"
              />
            </svg>
          </div>
          <span class="text-lg font-bold text-gray-900 tracking-tight"
            >城市漫游</span
          >
        </div>
        <p class="text-xs text-gray-400 mt-1">
          北上广深 · 高校景区 · 个性化旅游
        </p>
      </div>
      <div class="divider-gradient mx-3" />
      <!-- Nav -->
      <nav class="flex-1 px-3 space-y-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-glow flex items-center gap-3 px-3 py-2.5 rounded-2xl text-sm font-medium transition-all duration-200"
          :class="[
            $route.path === item.to
              ? 'bg-primary-50 text-primary-700 shadow-sm shadow-primary-500/5'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
          ]"
          @mousemove="handleNavGlow"
        >
          <component
            :is="item.icon"
            class="w-[18px] h-[18px] flex-shrink-0 transition-transform duration-200 group-hover:scale-110"
          />
          {{ item.label }}
          <span
            v-if="$route.path === item.to"
            class="ml-auto w-1.5 h-1.5 rounded-full bg-primary-500 animate-pulse"
          />
        </RouterLink>
      </nav>
      <!-- Account -->
      <div class="divider-gradient mx-3" />
      <div class="p-4">
        <template v-if="auth.isLoggedIn">
          <div class="flex items-center gap-3 mb-3">
            <div
              class="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md shadow-primary-500/20"
            >
              {{ (auth.user?.display_name || "旅").slice(0, 1) }}
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-gray-900 truncate">
                {{ auth.user?.display_name }}
              </p>
              <p class="text-xs text-gray-400">
                {{ auth.favoriteDestinationCount }} 收藏 ·
                {{ auth.favoriteRouteCount }} 路线
              </p>
            </div>
          </div>
          <button
            class="btn-soft-ghost w-full text-sm"
            v-ripple
            @click="auth.logout()"
          >
            退出登录
          </button>
        </template>
        <template v-else>
          <p class="text-xs text-gray-500 mb-3">
            登录后可同步收藏、保存路线、发布日记
          </p>
          <div class="flex gap-2">
            <button
              class="btn-soft-primary flex-1 text-sm"
              v-ripple
              @click="auth.openAuthModal('login')"
            >
              登录
            </button>
            <button
              class="btn-soft-secondary flex-1 text-sm"
              v-ripple
              @click="auth.openAuthModal('register')"
            >
              注册
            </button>
          </div>
        </template>
      </div>
    </aside>
    <!-- Mobile header -->
    <div
      class="lg:hidden fixed top-0 left-0 right-0 z-30 bg-white/80 backdrop-blur-lg border-0 shadow-md shadow-gray-200/50"
    >
      <div class="flex items-center justify-between px-4 py-3">
        <div class="flex items-center gap-2">
          <div
            class="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center"
          >
            <svg
              class="w-4 h-4 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418"
              />
            </svg>
          </div>
          <span class="text-base font-bold text-gray-900">城市漫游</span>
        </div>
        <button
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="p-2 rounded-2xl hover:bg-gray-100"
        >
          <svg
            class="w-5 h-5 text-gray-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              v-if="!mobileMenuOpen"
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
            />
            <path
              v-else
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
      <!-- Mobile nav dropdown -->
      <Transition name="page-fade-slide">
        <nav
          v-if="mobileMenuOpen"
          class="px-3 pb-3 space-y-1 bg-white border-0 shadow-md shadow-gray-200/50"
        >
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-sm font-medium transition-all"
            :class="[
              $route.path === item.to
                ? 'bg-primary-50 text-primary-700'
                : 'text-gray-600 hover:bg-gray-50',
            ]"
            @click="mobileMenuOpen = false"
          >
            <component :is="item.icon" class="w-[18px] h-[18px]" />
            {{ item.label }}
          </RouterLink>
        </nav>
      </Transition>
    </div>
    <!-- Main content -->
    <main class="flex-1 min-w-0 lg:pt-0 pt-14">
      <!-- Top bar -->
      <header
        class="sticky top-0 z-20 glass-panel border-0 shadow-md shadow-gray-200/50 px-6 py-3 hidden lg:flex items-center justify-between"
      >
        <div>
          <p class="text-sm text-gray-500">
            行程收藏、日记发布与路线记录都支持本地账号保存
          </p>
        </div>
        <div class="flex items-center gap-3">
          <template v-if="auth.isLoggedIn">
            <div
              class="flex items-center gap-2 py-1.5 px-3 rounded-2xl bg-gray-50 border-0 shadow-md shadow-gray-200/50"
            >
              <span class="text-sm font-medium text-gray-700">{{
                auth.user?.display_name
              }}</span>
              <span class="text-xs text-gray-400"
                >{{
                  auth.favoriteDestinationCount + auth.favoriteRouteCount
                }}
                收藏</span
              >
            </div>
            <button
              class="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              @click="auth.logout()"
            >
              退出
            </button>
          </template>
          <template v-else>
            <button
              class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              @click="auth.openAuthModal('login')"
            >
              登录
            </button>
            <button
              class="btn-soft-primary text-sm"
              v-ripple
              @click="auth.openAuthModal('register')"
            >
              免费注册
            </button>
          </template>
        </div>
      </header>
      <div class="p-4 lg:p-6">
        <RouterView v-slot="{ Component, route }">
          <Transition name="page-fade-slide" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </Transition>
        </RouterView>
      </div>
    </main>
    <AuthModal /> <ToastContainer />
  </div>
</template>
<script setup lang="ts">
import { h, onMounted, ref } from "vue";
import AuthModal from "./components/AuthModal.vue";
import ToastContainer from "./components/ToastContainer.vue";
import { useAuthStore } from "./stores/auth";
const auth = useAuthStore();
const mobileMenuOpen = ref(false);
const handleNavGlow = (e: MouseEvent) => {
  const el = e.currentTarget as HTMLElement;
  const rect = el.getBoundingClientRect();
  el.style.setProperty(
    "--glow-x",
    `${((e.clientX - rect.left) / rect.width) * 100}%`,
  );
  el.style.setProperty(
    "--glow-y",
    `${((e.clientY - rect.top) / rect.height) * 100}%`,
  );
};
const IconHome = () =>
  h(
    "svg",
    {
      class: "w-[18px] h-[18px]",
      fill: "none",
      viewBox: "0 0 24 24",
      stroke: "currentColor",
      "stroke-width": "1.5",
    },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "m2.25 12 8.954-8.955a1.126 1.126 0 0 1 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25",
      }),
    ],
  );
const IconMap = () =>
  h(
    "svg",
    {
      class: "w-[18px] h-[18px]",
      fill: "none",
      viewBox: "0 0 24 24",
      stroke: "currentColor",
      "stroke-width": "1.5",
    },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "M9 6.75V15m6-6v8.25m.503 3.498 4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934a1.12 1.12 0 0 1-1.006 0L9.503 3.252a1.125 1.125 0 0 0-1.006 0L3.622 5.689A1.125 1.125 0 0 0 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934a1.12 1.12 0 0 1 1.006 0l4.994 2.497c.317.158.69.158 1.006 0Z",
      }),
    ],
  );
const IconPin = () =>
  h(
    "svg",
    {
      class: "w-[18px] h-[18px]",
      fill: "none",
      viewBox: "0 0 24 24",
      stroke: "currentColor",
      "stroke-width": "1.5",
    },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z",
      }),
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z",
      }),
    ],
  );
const IconSearch = () =>
  h(
    "svg",
    {
      class: "w-[18px] h-[18px]",
      fill: "none",
      viewBox: "0 0 24 24",
      stroke: "currentColor",
      "stroke-width": "1.5",
    },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z",
      }),
    ],
  );
const IconBuilding = () =>
  h(
    "svg",
    {
      class: "w-[18px] h-[18px]",
      fill: "none",
      viewBox: "0 0 24 24",
      stroke: "currentColor",
      "stroke-width": "1.5",
    },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21",
      }),
    ],
  );
const IconUtensils = () =>
  h(
    "svg",
    {
      class: "w-[18px] h-[18px]",
      fill: "none",
      viewBox: "0 0 24 24",
      stroke: "currentColor",
      "stroke-width": "1.5",
    },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "M12 8.25v-1.5m0 1.5c-1.355 0-2.697.056-4.024.166C6.845 8.51 6 9.473 6 10.608v2.513m6-4.871c1.355 0 2.697.056 4.024.166C17.155 8.51 18 9.473 18 10.608v2.513M15 8.25v-1.5m-6 1.5v-1.5m12 9.75-1.5.75a3.354 3.354 0 0 1-3 0 3.354 3.354 0 0 0-3 0 3.354 3.354 0 0 1-3 0 3.354 3.354 0 0 0-3 0 3.354 3.354 0 0 1-3 0L3 16.5m15-3.379a48.474 48.474 0 0 0-6-.371c-2.032 0-4.034.126-6 .371m12 0c.39.049.777.102 1.163.16 1.07.16 1.837 1.094 1.837 2.175v5.17c0 .62-.504 1.124-1.125 1.124H4.125A1.125 1.125 0 0 1 3 20.496v-5.17c0-1.08.768-2.014 1.837-2.174A47.78 47.78 0 0 1 6 12.871",
      }),
    ],
  );
const IconBook = () =>
  h(
    "svg",
    {
      class: "w-[18px] h-[18px]",
      fill: "none",
      viewBox: "0 0 24 24",
      stroke: "currentColor",
      "stroke-width": "1.5",
    },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25",
      }),
    ],
  );
const navItems = [
  { label: "首页", to: "/", icon: IconHome },
  { label: "目的地推荐", to: "/destinations", icon: IconPin },
  { label: "搜索", to: "/search", icon: IconSearch },
  { label: "地图导航", to: "/routes", icon: IconMap },
  { label: "附近设施", to: "/facilities", icon: IconBuilding },
  { label: "美食推荐", to: "/foods", icon: IconUtensils },
  { label: "旅游日记", to: "/diaries", icon: IconBook },
  { label: "智能助手", to: "/agents", icon: IconSearch },
  { label: "管理后台", to: "/admin", icon: IconBuilding },
];
onMounted(() => {
  auth.bindUnauthorizedListener();
  auth.restoreSession();
});
</script>
