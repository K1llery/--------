<template>
  <div class="app-shell">
    <!-- Sidebar -->
    <aside class="app-sidebar">
      <!-- Brand -->
      <div class="app-brand">
        <div class="app-brand-mark">
          <div class="app-brand-icon">
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
                d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418"
              />
            </svg>
          </div>
          <span>城市漫游</span>
        </div>
      </div>
      <!-- Nav -->
      <nav class="app-nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="app-nav-link"
          :class="[
            $route.path === item.to
              ? 'app-nav-link-active'
              : 'app-nav-link-idle',
          ]"
        >
          <component :is="item.icon" class="app-nav-icon" />
          {{ item.label }}
        </RouterLink>
      </nav>
      <!-- Account -->
      <div class="app-sidebar-account">
        <template v-if="auth.isLoggedIn">
          <div class="app-user-card">
            <div class="app-user-avatar">
              {{ (auth.user?.display_name || "旅").slice(0, 1) }}
            </div>
            <div class="app-user-meta">
              <p>{{ auth.user?.display_name }}</p>
              <span>
                {{ auth.favoriteDestinationCount }} 收藏 ·
                {{ auth.favoriteRouteCount }} 路线
              </span>
            </div>
          </div>
          <button
            class="app-shell-button app-shell-button-ghost"
            type="button"
            v-ripple
            @click="auth.logout()"
          >
            退出登录
          </button>
        </template>
      </div>
    </aside>
    <!-- Mobile header -->
    <div class="app-mobile-shell">
      <div class="app-mobile-header">
        <div class="app-mobile-brand">
          <div class="app-brand-icon app-brand-icon-mobile">
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
                d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418"
              />
            </svg>
          </div>
          <span>城市漫游</span>
        </div>
        <button
          class="app-icon-button"
          type="button"
          aria-label="切换导航菜单"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <svg
            class="w-5 h-5"
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
          class="app-mobile-nav"
        >
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="app-mobile-nav-link"
            :class="[
              $route.path === item.to
                ? 'app-nav-link-active'
                : 'app-nav-link-idle',
            ]"
            @click="mobileMenuOpen = false"
          >
            <component :is="item.icon" class="app-nav-icon" />
            {{ item.label }}
          </RouterLink>
        </nav>
      </Transition>
    </div>
    <!-- Main content -->
    <main class="app-main">
      <!-- Top bar -->
      <header class="app-topbar">
        <div class="app-topbar-tools">
          <span class="app-topbar-tool">
            <IconBookmark class="app-topbar-icon" />
            收藏
            <strong>{{
              auth.favoriteDestinationCount + auth.favoriteRouteCount
            }}</strong>
          </span>
          <span class="app-topbar-tool">
            <IconBell class="app-topbar-icon" />
            通知
          </span>
          <template v-if="auth.isLoggedIn">
            <span class="app-topbar-tool app-topbar-user">
              <IconUser class="app-topbar-icon" />
              {{ auth.user?.display_name }}
            </span>
            <button
              class="app-topbar-link"
              type="button"
              @click="auth.logout()"
            >
              <IconLogout class="app-topbar-icon" />
              退出
            </button>
          </template>
          <template v-else>
            <button
              class="app-topbar-link"
              type="button"
              @click="auth.openAuthModal('login')"
            >
              <IconUser class="app-topbar-icon" />
              登录
            </button>
            <button
              class="app-topbar-link app-topbar-register"
              type="button"
              @click="auth.openAuthModal('register')"
            >
              <IconUserPlus class="app-topbar-icon" />
              免费注册
            </button>
          </template>
        </div>
      </header>
      <div class="app-content">
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
const createTopbarIcon = (pathData: string) =>
  h(
    "svg",
    {
      class: "app-topbar-icon",
      fill: "none",
      viewBox: "0 0 24 24",
      stroke: "currentColor",
      "stroke-width": "1.8",
    },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: pathData,
      }),
    ],
  );
const IconBookmark = () =>
  createTopbarIcon(
    "M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z",
  );
const IconBell = () =>
  createTopbarIcon(
    "M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0",
  );
const IconUser = () =>
  createTopbarIcon(
    "M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z",
  );
const IconUserPlus = () =>
  createTopbarIcon(
    "M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0ZM4.269 19.533a6.375 6.375 0 0 1 11.462 0 17.902 17.902 0 0 1-5.731.967 17.902 17.902 0 0 1-5.731-.967Z",
  );
const IconLogout = () =>
  createTopbarIcon(
    "M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9",
  );
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
];
onMounted(() => {
  auth.bindUnauthorizedListener();
  auth.restoreSession();
});
</script>
