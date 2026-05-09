<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="auth.modalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-indigo-50/80 backdrop-blur-sm"
        @click.self="auth.closeAuthModal()"
      >
        <div class="w-full max-w-md animate-[card-enter_0.3s_ease]">
          <!-- Tab switcher -->
          <div class="flex gap-1 p-1.5 bg-gray-100/80 rounded-2xl mb-4">
            <button
              v-for="tab in ['login', 'register'] as const"
              :key="tab"
              type="button"
              class="flex-1 py-2.5 text-sm font-medium rounded-2xl transition-all duration-300"
              :class="
                auth.modalMode === tab
                  ? 'bg-white text-gray-900 shadow-lg shadow-gray-200/50'
                  : 'text-gray-500 hover:text-gray-700'
              "
              @click="switchTo(tab)"
            >
              {{ tab === "login" ? "登录" : "注册" }}
            </button>
          </div>
          <!-- Card -->
          <div class="relative bg-white rounded-3xl card-elevated p-6 md:p-8">
            <!-- Header -->
            <div class="mb-6">
              <h2 class="text-2xl font-bold text-gray-900">
                {{ auth.modalMode === "login" ? "欢迎回来" : "创建账号" }}
              </h2>
              <p class="text-sm text-gray-500 mt-1">
                {{
                  auth.modalMode === "login"
                    ? "登录后可收藏路线、目的地和发布日记"
                    : "注册本地账号，保存你的浏览偏好"
                }}
              </p>
            </div>
            <form class="space-y-4" @submit.prevent="submit">
              <!-- Display name (register only) -->
              <div v-if="auth.modalMode === 'register'" class="space-y-1.5">
                <label class="block text-sm font-medium text-gray-700">昵称</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg
                      class="w-4 h-4 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      stroke-width="1.5"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
                      />
                    </svg>
                  </div>
                  <input
                    v-model="displayName"
                    placeholder="你的昵称"
                    class="input-soft has-leading-icon text-sm"
                  />
                </div>
              </div>
              <!-- Username -->
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-gray-700">用户名</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg
                      class="w-4 h-4 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      stroke-width="1.5"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75"
                      />
                    </svg>
                  </div>
                  <input
                    v-model="username"
                    placeholder="你的用户名"
                    class="input-soft has-leading-icon text-sm"
                  />
                </div>
              </div>
              <!-- Password -->
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-gray-700">密码</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg
                      class="w-4 h-4 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      stroke-width="1.5"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"
                      />
                    </svg>
                  </div>
                  <input
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="输入密码"
                    class="input-soft has-leading-icon has-trailing-icon text-sm"
                  />
                  <button
                    type="button"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                    @click="showPassword = !showPassword"
                  >
                    <svg
                      v-if="!showPassword"
                      class="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      stroke-width="1.5"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
                      />
                    </svg>
                    <svg
                      v-else
                      class="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      stroke-width="1.5"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"
                      />
                    </svg>
                  </button>
                </div>
              </div>
              <!-- Error -->
              <div v-if="auth.error" class="alert-soft-error flex items-center gap-2">
                <svg
                  class="w-4 h-4 flex-shrink-0"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z"
                  />
                </svg>
                {{ auth.error }}
              </div>
              <!-- Submit -->
              <button
                type="submit"
                :disabled="auth.loading"
                v-ripple
                class="btn-soft-primary w-full flex items-center justify-center gap-2 text-sm"
              >
                <svg
                  v-if="auth.loading"
                  class="w-4 h-4 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                {{ auth.loading ? "处理中..." : auth.modalMode === "login" ? "登录" : "创建账号" }}
              </button>
            </form>
            <!-- Switch mode -->
            <p class="text-center text-sm text-gray-500 mt-5">
              {{ auth.modalMode === "login" ? "还没有账号？" : "已有账号？" }}
              <button
                type="button"
                class="text-primary-600 hover:text-primary-700 font-medium transition-colors"
                @click="switchMode"
              >
                {{ auth.modalMode === "login" ? "免费注册" : "去登录" }}
              </button>
            </p>
            <!-- Close -->
            <button
              type="button"
              class="absolute top-4 right-4 p-1.5 rounded-2xl text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all"
              @click="auth.closeAuthModal()"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <!-- Footer -->
          <p class="mt-4 text-center text-xs text-gray-400">数据仅保存在本地服务器，安全可控</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
<script setup lang="ts">
import { ref, watch } from "vue";
import { useAuthStore } from "../stores/auth";
const auth = useAuthStore();
const username = ref("");
const displayName = ref("");
const password = ref("");
const showPassword = ref(false);
const resetFields = () => {
  username.value = "";
  displayName.value = "";
  password.value = "";
  showPassword.value = false;
};
const switchTo = (mode: "login" | "register") => {
  auth.modalMode = mode;
  auth.error = "";
  resetFields();
};
const switchMode = () => {
  switchTo(auth.modalMode === "login" ? "register" : "login");
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
<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
