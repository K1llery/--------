<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-chip">Urban Explorer</span>
        <h1>北上广深高校与景区</h1>
        <p>城市漫游 · 校园打卡 · 景点精选</p>
      </div>
      <nav>
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to">{{ item.label }}</RouterLink>
      </nav>

      <section class="sidebar-account">
        <template v-if="auth.isLoggedIn">
          <div class="account-avatar">{{ (auth.user?.display_name || "旅").slice(0, 1) }}</div>
          <div>
            <h3>{{ auth.user?.display_name }}</h3>
            <p>{{ auth.favoriteDestinationCount }} 个目的地收藏 · {{ auth.favoriteRouteCount }} 条路线收藏</p>
          </div>
          <button class="ghost-btn wide-btn" @click="auth.logout()">退出登录</button>
        </template>
        <template v-else>
          <h3>登录后可同步收藏</h3>
          <p>收藏目的地、保存路线、发布日记都会跟账号联动。</p>
          <div class="hero-actions">
            <button class="primary-btn" @click="auth.openAuthModal('login')">登录</button>
            <button class="secondary-btn" @click="auth.openAuthModal('register')">注册</button>
          </div>
        </template>
      </section>
    </aside>

    <main class="content">
      <div class="app-topbar">
        <div class="topbar-copy">
          <span class="eyebrow">Trip Board</span>
          <p>行程收藏、日记发布与路线记录都支持本地账号保存。</p>
        </div>
        <div class="topbar-actions">
          <template v-if="auth.isLoggedIn">
            <div class="topbar-user">
              <strong>{{ auth.user?.display_name }}</strong>
              <span>我的收藏 {{ auth.favoriteDestinationCount + auth.favoriteRouteCount }}</span>
            </div>
            <button class="ghost-btn" @click="auth.logout()">退出</button>
          </template>
          <template v-else>
            <button class="ghost-btn" @click="auth.openAuthModal('login')">登录</button>
            <button class="primary-btn" @click="auth.openAuthModal('register')">注册</button>
          </template>
        </div>
      </div>
      <RouterView v-slot="{ Component, route }">
        <Transition name="page-fade-slide" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </Transition>
      </RouterView>
    </main>
    <AuthModal />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import AuthModal from "./components/AuthModal.vue";
import { useAuthStore } from "./stores/auth";

const auth = useAuthStore();

const navItems = [
  { label: "首页", to: "/" },
  { label: "目的地推荐", to: "/destinations" },
  { label: "搜索", to: "/search" },
  { label: "地图导航", to: "/routes" },
  { label: "附近设施", to: "/facilities" },
  { label: "美食推荐", to: "/foods" },
  { label: "旅游日记", to: "/diaries" }
];

onMounted(() => {
  auth.bindUnauthorizedListener();
  auth.restoreSession();
});
</script>
