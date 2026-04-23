<template>
  <div v-if="auth.modalOpen" class="modal-backdrop" @click.self="auth.closeAuthModal()">
    <section class="modal-card">
      <div class="section-top compact">
        <div>
          <h3>{{ auth.modalMode === "login" ? "登录你的城市行程夹" : "注册新账号" }}</h3>
          <p>
            {{
              auth.modalMode === "login"
                ? "登录后可收藏路线、收藏目的地和发布日记。"
                : "创建本地账号后可直接保存你的浏览偏好。"
            }}
          </p>
        </div>
        <button class="ghost-btn" @click="auth.closeAuthModal()">关闭</button>
      </div>

      <form class="modal-form" @submit.prevent="submit">
        <input v-if="auth.modalMode === 'register'" v-model="displayName" placeholder="昵称" />
        <input v-model="username" placeholder="用户名" />
        <input v-model="password" type="password" placeholder="密码" />
        <button class="primary-btn" type="submit">
          {{ auth.loading ? "提交中..." : auth.modalMode === "login" ? "登录" : "注册" }}
        </button>
      </form>

      <div v-if="auth.error" class="status-card error-card">{{ auth.error }}</div>

      <div class="toolbar-row">
        <span class="toolbar-hint">{{
          auth.modalMode === "login" ? "还没有账号？" : "已经有账号？"
        }}</span>
        <button class="ghost-btn" @click="switchMode">
          {{ auth.modalMode === "login" ? "去注册" : "去登录" }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const username = ref("");
const displayName = ref("");
const password = ref("");

const resetFields = () => {
  username.value = "";
  displayName.value = "";
  password.value = "";
};

const switchMode = () => {
  auth.modalMode = auth.modalMode === "login" ? "register" : "login";
  auth.error = "";
  resetFields();
};

const submit = async () => {
  if (auth.modalMode === "login") {
    await auth.login({ username: username.value, password: password.value });
    return;
  }
  await auth.register({
    username: username.value,
    display_name: displayName.value || username.value,
    password: password.value,
  });
};

watch(
  () => auth.modalOpen,
  (open) => {
    if (!open) resetFields();
  },
);
</script>
