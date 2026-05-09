<template>
  <Teleport to="body">
    <div class="fixed top-5 right-5 z-[9999] flex flex-col gap-2.5 pointer-events-none">
      <TransitionGroup name="toast-slide">
        <div
          v-for="item in toast.items"
          :key="item.id"
          class="pointer-events-auto max-w-sm px-5 py-3.5 rounded-2xl text-sm font-medium backdrop-blur-xl transition-all"
          :class="typeClasses[item.type]"
        >
          <div class="flex items-center gap-2.5">
            <svg
              v-if="item.type === 'success'"
              class="w-4 h-4 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
              />
            </svg>
            <svg
              v-else-if="item.type === 'error'"
              class="w-4 h-4 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z"
              />
            </svg>
            <svg
              v-else
              class="w-4 h-4 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"
              />
            </svg>
            <span>{{ item.message }}</span>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
<script setup lang="ts">
import { useToastStore } from "../stores/toast";
const toast = useToastStore();
const typeClasses: Record<string, string> = {
  success: "bg-emerald-50/95 text-emerald-700 shadow-lg shadow-gray-200/50",
  error: "bg-red-50/95 text-red-700 shadow-lg shadow-gray-200/50",
  info: "bg-primary-50/95 text-primary-700 shadow-lg shadow-gray-200/50",
};
</script>
<style scoped>
.toast-slide-enter-active {
  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}
.toast-slide-leave-active {
  transition: all 0.25s ease;
}
.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(40px) scale(0.95);
}
.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(40px) scale(0.95);
}
.toast-slide-move {
  transition: transform 0.3s ease;
}
</style>
