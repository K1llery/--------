import { defineStore } from "pinia";
import { ref } from "vue";

export type ToastType = "success" | "error" | "info";

export interface ToastItem {
  id: number;
  message: string;
  type: ToastType;
}

let nextId = 0;

export const useToastStore = defineStore("toast", () => {
  const items = ref<ToastItem[]>([]);

  const show = (message: string, type: ToastType = "info", duration = 3000) => {
    const id = ++nextId;
    items.value.push({ id, message, type });
    setTimeout(() => {
      items.value = items.value.filter((t) => t.id !== id);
    }, duration);
  };

  const success = (message: string) => show(message, "success");
  const error = (message: string) => show(message, "error");
  const info = (message: string) => show(message, "info");

  return { items, show, success, error, info };
});
