<template>
  <div class="app-shell">
    <aside class="app-sidebar">
      <div class="app-brand">
        <RouterLink to="/" class="app-brand-mark">
          <span class="app-brand-logo-shell">
            <img :src="brandLogoUrl" alt="优途" class="app-brand-logo" />
          </span>
          <span class="app-brand-copy">
            <strong>优途</strong>
            <small>城市探索与路线规划</small>
          </span>
        </RouterLink>
      </div>

      <nav class="app-nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="app-nav-link"
          :class="[isNavActive(item.to) ? 'app-nav-link-active' : 'app-nav-link-idle']"
        >
          <component :is="item.icon" class="app-nav-icon" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="app-sidebar-account">
        <template v-if="auth.isLoggedIn">
          <div class="app-user-card">
            <div class="app-user-avatar">
              {{ (auth.user?.display_name || "旅").slice(0, 1) }}
            </div>
            <div class="app-user-meta">
              <p>{{ auth.user?.display_name }}</p>
              <span>
                {{ auth.favoriteDestinationCount }} 个收藏地点 · {{ auth.favoriteRouteCount }} 条路线
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
        <template v-else>
          <div class="app-sidebar-guest">
            <p>登录后可同步收藏、路线和计划。</p>
            <div class="app-sidebar-guest-actions">
              <button class="app-shell-button" type="button" @click="auth.openAuthModal('login')">
                登录
              </button>
              <button
                class="app-shell-button app-shell-button-ghost"
                type="button"
                @click="auth.openAuthModal('register')"
              >
                注册
              </button>
            </div>
          </div>
        </template>
      </div>
    </aside>

    <div class="app-mobile-shell">
      <div class="app-mobile-header">
        <RouterLink to="/" class="app-mobile-brand" @click="mobileMenuOpen = false">
          <span class="app-brand-logo-shell app-brand-logo-shell-mobile">
            <img :src="brandLogoUrl" alt="优途" class="app-brand-logo" />
          </span>
          <span class="app-brand-copy">
            <strong>优途</strong>
            <small>城市探索与路线规划</small>
          </span>
        </RouterLink>
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
            <path v-else stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <Transition name="page-fade-slide">
        <nav v-if="mobileMenuOpen" class="app-mobile-nav">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="app-mobile-nav-link"
            :class="[isNavActive(item.to) ? 'app-nav-link-active' : 'app-nav-link-idle']"
            @click="mobileMenuOpen = false"
          >
            <component :is="item.icon" class="app-nav-icon" />
            {{ item.label }}
          </RouterLink>
        </nav>
      </Transition>
    </div>

    <main class="app-main">
      <header class="app-topbar">
        <div class="app-topbar-context">
          <p>优途</p>
          <strong>{{ currentNavLabel }}</strong>
        </div>

        <div ref="topbarToolsRef" class="app-topbar-tools" @click.stop>
          <button
            class="app-topbar-link"
            :class="{ 'app-topbar-link-active': activeTopbarPanel === 'favorites' }"
            type="button"
            @click="handleFavoritesClick"
          >
            <IconBookmark class="app-topbar-icon" />
            收藏
            <strong>{{ auth.favoriteDestinationCount + auth.favoriteRouteCount }}</strong>
          </button>
          <button
            class="app-topbar-link"
            :class="{ 'app-topbar-link-active': activeTopbarPanel === 'notifications' }"
            type="button"
            @click="toggleTopbarPanel('notifications')"
          >
            <IconBell class="app-topbar-icon" />
            通知
          </button>
          <button
            class="app-topbar-link"
            :class="{ 'app-topbar-link-active': activeTopbarPanel === 'messages' }"
            type="button"
            @click="handleMessagesClick"
          >
            <IconChat class="app-topbar-icon" />
            消息
          </button>

          <template v-if="auth.isLoggedIn">
            <span class="app-topbar-tool app-topbar-user">
              <IconUser class="app-topbar-icon" />
              {{ auth.user?.display_name }}
            </span>
            <button class="app-topbar-link" type="button" @click="auth.logout()">
              <IconLogout class="app-topbar-icon" />
              退出
            </button>
          </template>
          <template v-else>
            <button class="app-topbar-link" type="button" @click="auth.openAuthModal('login')">
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

          <Transition name="app-popover">
            <div
              v-if="activeTopbarPanel"
              class="app-topbar-popover"
              :class="{ 'app-topbar-popover-wide': activeTopbarPanel === 'messages' }"
            >
              <template v-if="activeTopbarPanel === 'favorites'">
                <div class="app-popover-header">
                  <div>
                    <p>收藏中心</p>
                    <span>你的地点收藏和路线快照会汇总在这里，方便答辩时快速切换。</span>
                  </div>
                  <strong>{{ auth.favoriteDestinationCount + auth.favoriteRouteCount }}</strong>
                </div>
                <div class="app-favorite-grid">
                  <div>
                    <strong>{{ auth.favoriteDestinationCount }}</strong>
                    <span>收藏地点</span>
                  </div>
                  <div>
                    <strong>{{ auth.favoriteRouteCount }}</strong>
                    <span>收藏路线</span>
                  </div>
                </div>
                <p
                  v-if="auth.favoriteDestinationCount + auth.favoriteRouteCount === 0"
                  class="app-popover-empty"
                >
                  还没有收藏内容。你可以先收藏一个目的地或路线，这里会实时更新。
                </p>
                <div class="app-popover-actions">
                  <RouterLink to="/destinations" @click="closeTopbarPanel">去看目的地</RouterLink>
                  <RouterLink to="/routes" @click="closeTopbarPanel">打开地图导航</RouterLink>
                  <RouterLink to="/" @click="closeTopbarPanel">返回首页</RouterLink>
                </div>
              </template>

              <template v-else-if="activeTopbarPanel === 'notifications'">
                <div class="app-popover-header">
                  <div>
                    <p>通知中心</p>
                    <span>这里保留收藏同步、演示提醒和互动反馈等产品通知入口。</span>
                  </div>
                  <strong>{{ demoNotifications.length }}</strong>
                </div>
                <div class="app-notice-list">
                  <div
                    v-for="notice in demoNotifications"
                    :key="notice.title"
                    class="app-notice-item"
                  >
                    <span class="app-notice-dot" />
                    <div>
                      <p>{{ notice.title }}</p>
                      <span>{{ notice.detail }}</span>
                    </div>
                  </div>
                </div>
              </template>

              <template v-else>
                <div class="app-popover-header">
                  <div>
                    <p>好友消息</p>
                    <span>保留社交模块的演示入口，后续可以接真实接口。</span>
                  </div>
                  <strong>{{ currentFriendMessages.length }}</strong>
                </div>
                <div class="app-message-layout">
                  <div class="app-friend-list">
                    <button
                      v-for="friend in demoFriends"
                      :key="friend.id"
                      class="app-friend-item"
                      :class="{ 'app-friend-item-active': friend.id === selectedFriendId }"
                      type="button"
                      @click="selectedFriendId = friend.id"
                    >
                      <span>{{ friend.avatar }}</span>
                      <div>
                        <p>{{ friend.name }}</p>
                        <small>{{ friend.status }}</small>
                      </div>
                    </button>
                  </div>
                  <div class="app-chat-panel">
                    <div class="app-chat-history">
                      <div
                        v-for="message in currentFriendMessages"
                        :key="message.id"
                        class="app-chat-bubble"
                        :class="{ 'app-chat-bubble-self': message.from === 'me' }"
                      >
                        {{ message.text }}
                      </div>
                    </div>
                    <form class="app-chat-form" @submit.prevent="sendDemoMessage">
                      <input
                        v-model="messageDraft"
                        type="text"
                        maxlength="80"
                        placeholder="输入演示消息"
                      />
                      <button type="submit" aria-label="发送消息">
                        <IconSend class="app-topbar-icon" />
                      </button>
                    </form>
                  </div>
                </div>
              </template>
            </div>
          </Transition>
        </div>
      </header>

      <div class="app-content">
        <RouterView v-slot="{ Component, route: currentRoute }">
          <Transition name="page-fade-slide" mode="out-in">
            <component :is="Component" :key="currentRoute.fullPath" />
          </Transition>
        </RouterView>
      </div>
    </main>

    <AuthModal />
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { computed, h, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import AuthModal from "./components/AuthModal.vue";
import ToastContainer from "./components/ToastContainer.vue";
import { useAuthStore } from "./stores/auth";
import { useToastStore } from "./stores/toast";

const brandLogoUrl = "/brands/youtu_logo.png";
const auth = useAuthStore();
const toast = useToastStore();
const route = useRoute();
const mobileMenuOpen = ref(false);

type TopbarPanel = "favorites" | "notifications" | "messages";
type DemoMessage = {
  id: number;
  from: "friend" | "me";
  text: string;
};

const topbarToolsRef = ref<HTMLElement | null>(null);
const activeTopbarPanel = ref<TopbarPanel | null>(null);
const selectedFriendId = ref("chen");
const messageDraft = ref("");
const messageStorageKey = "travel_demo_friend_messages";

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
const IconChat = () =>
  createTopbarIcon(
    "M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm3.75 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm3.75 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM21 12c0 4.142-4.03 7.5-9 7.5a10.3 10.3 0 0 1-3.293-.526L3 21l1.45-3.626C3.536 15.995 3 14.411 3 12c0-4.142 4.03-7.5 9-7.5s9 3.358 9 7.5Z",
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
const IconSend = () =>
  createTopbarIcon("M6 12 3.269 3.125A59.768 59.768 0 0 1 21.485 12 59.77 59.77 0 0 1 3.27 20.875L6 12Zm0 0h7.5");

const IconHome = () =>
  h(
    "svg",
    { class: "w-[18px] h-[18px]", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "1.5" },
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
    { class: "w-[18px] h-[18px]", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "1.5" },
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
    { class: "w-[18px] h-[18px]", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "1.5" },
    [
      h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" }),
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
    { class: "w-[18px] h-[18px]", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "1.5" },
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
    { class: "w-[18px] h-[18px]", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "1.5" },
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
    { class: "w-[18px] h-[18px]", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "1.5" },
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
    { class: "w-[18px] h-[18px]", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "1.5" },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25",
      }),
    ],
  );
const IconCalendar = () =>
  h(
    "svg",
    { class: "w-[18px] h-[18px]", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "1.5" },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5",
      }),
    ],
  );

const IconStats = () =>
  h(
    "svg",
    { class: "w-[18px] h-[18px]", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "1.5" },
    [
      h("path", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        d: "M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75Zm6.75-6C9.75 6.504 10.254 6 10.875 6h2.25c.621 0 1.125.504 1.125 1.125v12.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V7.125Zm6.75-3C16.5 3.504 17.004 3 17.625 3h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z",
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
  { label: "旅游规划", to: "/plan", icon: IconCalendar },
  { label: "数据洞察", to: "/stats", icon: IconStats },
];

const isNavActive = (to: string) => (to === "/" ? route.path === "/" : route.path === to || route.path.startsWith(`${to}/`));

const currentNavLabel = computed(
  () =>
    navItems
      .filter((item) => item.to === "/" || route.path === item.to || route.path.startsWith(`${item.to}/`))
      .sort((left, right) => right.to.length - left.to.length)[0]?.label ?? "个性化旅游平台",
);

const demoFriends = [
  { id: "chen", name: "陈同学", avatar: "陈", status: "想看故宫路线" },
  { id: "lin", name: "林同学", avatar: "林", status: "刚收藏了一个美食点" },
  { id: "zhou", name: "周同学", avatar: "周", status: "约周末校园漫游" },
];

const demoNotifications = [
  {
    title: "收藏同步提醒",
    detail: "登录后，地点收藏和路线快照会同步到当前账号。",
  },
  {
    title: "路线讲解准备",
    detail: "地图导航里的收藏路线可以直接作为课程演示素材。",
  },
  {
    title: "好友互动入口",
    detail: "消息模块保留了社交入口，后续可以接真实接口。",
  },
];

const defaultMessages: Record<string, DemoMessage[]> = {
  chen: [
    { id: 1, from: "friend", text: "下午讲解时可以先演示收藏，再切到路线。" },
    { id: 2, from: "me", text: "好，我把入口做成了更清晰的产品工具栏。" },
  ],
  lin: [{ id: 1, from: "friend", text: "我想看北京周边美食推荐，能一起发路线吗？" }],
  zhou: [{ id: 1, from: "friend", text: "如果周末去北邮校园，我可以直接跟着路线走吗？" }],
};

const loadDemoMessages = () => {
  if (typeof window === "undefined") return defaultMessages;
  try {
    const cached = window.localStorage.getItem(messageStorageKey);
    return cached ? { ...defaultMessages, ...JSON.parse(cached) } : defaultMessages;
  } catch {
    return defaultMessages;
  }
};

const friendMessages = ref<Record<string, DemoMessage[]>>(loadDemoMessages());
const currentFriendMessages = computed(() => friendMessages.value[selectedFriendId.value] || []);

const persistDemoMessages = () => {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(messageStorageKey, JSON.stringify(friendMessages.value));
};

const closeTopbarPanel = () => {
  activeTopbarPanel.value = null;
};

const toggleTopbarPanel = (panel: TopbarPanel) => {
  activeTopbarPanel.value = activeTopbarPanel.value === panel ? null : panel;
};

const handleFavoritesClick = () => {
  if (!auth.isLoggedIn) {
    closeTopbarPanel();
    toast.info("登录后查看收藏中心");
    auth.openAuthModal("login");
    return;
  }
  toggleTopbarPanel("favorites");
};

const handleMessagesClick = () => {
  if (!auth.isLoggedIn) {
    closeTopbarPanel();
    toast.info("登录后查看好友消息");
    auth.openAuthModal("login");
    return;
  }
  toggleTopbarPanel("messages");
};

const sendDemoMessage = () => {
  const text = messageDraft.value.trim();
  if (!text) return;

  const nextMessage = {
    id: Date.now(),
    from: "me" as const,
    text,
  };

  friendMessages.value = {
    ...friendMessages.value,
    [selectedFriendId.value]: [...currentFriendMessages.value, nextMessage],
  };
  messageDraft.value = "";
  persistDemoMessages();
};

const handleDocumentClick = (event: MouseEvent) => {
  if (!topbarToolsRef.value?.contains(event.target as Node)) {
    closeTopbarPanel();
  }
};

onMounted(() => {
  auth.bindUnauthorizedListener();
  auth.restoreSession();
  document.addEventListener("click", handleDocumentClick);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleDocumentClick);
});
</script>
