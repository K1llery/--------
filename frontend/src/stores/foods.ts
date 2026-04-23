import { defineStore } from "pinia";

import { api } from "../api/client";
import type { Food } from "../types/models";
import type { FoodListResponse } from "../types/api";

interface FoodState {
  items: Food[];
  loading: boolean;
  error: string;
  selected: Food | null;
  lastUpdated: string;
}

export const useFoodStore = defineStore("foods", {
  state: (): FoodState => ({
    items: [],
    loading: false,
    error: "",
    selected: null,
    lastUpdated: "",
  }),
  actions: {
    async load(force = false) {
      if (this.loading) return;
      if (!force && this.items.length > 0) return;
      this.loading = true;
      this.error = "";
      try {
        const { data } = await api.get<FoodListResponse>("/foods");
        this.items = data.items ?? [];
        this.selected = this.items[0] ?? null;
        this.lastUpdated = new Date().toLocaleString("zh-CN");
      } catch {
        this.error = "美食数据加载失败，请稍后重试。";
      } finally {
        this.loading = false;
      }
    },
    select(item: Food) {
      this.selected = item;
    },
  },
});
