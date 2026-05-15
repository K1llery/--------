import { defineStore } from "pinia";

import { api } from "../api/client";
import type { FoodListResponse } from "../types/api";
import type { Destination, Food } from "../types/models";

type ResourceState<T> = {
  items: T[];
  loading: boolean;
  error: string;
  selected: T | null;
  lastUpdated: string;
};

function createResourceState<T>(): ResourceState<T> {
  return {
    items: [],
    loading: false,
    error: "",
    selected: null,
    lastUpdated: "",
  };
}

// NOTE: Diary state and actions used to live here but have been removed —
// every diary page now talks to ``features/diary/api/diaryApi`` directly and
// keeps its own local state. There is no cross-page diary state to share, so
// no diary store currently exists. If a future flow needs one, add it under
// ``features/diary/stores/`` rather than reviving this central store.
export const useTravelStore = defineStore("travel", {
  state: () => ({
    destinations: createResourceState<Destination>(),
    foods: createResourceState<Food>(),
  }),
  actions: {
    async loadFeaturedDestinations(force = false) {
      if (this.destinations.loading) return;
      if (!force && this.destinations.items.length > 0) return;

      this.destinations.loading = true;
      this.destinations.error = "";
      try {
        const { data } = await api.get<Destination[]>("/destinations/featured");
        this.destinations.items = data;
        this.destinations.selected = data[0] ?? null;
        this.destinations.lastUpdated = new Date().toLocaleString("zh-CN");
      } catch {
        this.destinations.error = "精选目的地加载失败，请确认后端是否已启动。";
      } finally {
        this.destinations.loading = false;
      }
    },
    selectDestination(item: Destination | null) {
      this.destinations.selected = item;
    },
    async loadFoods(force = false) {
      if (this.foods.loading) return;
      if (!force && this.foods.items.length > 0) return;

      this.foods.loading = true;
      this.foods.error = "";
      try {
        const { data } = await api.get<FoodListResponse>("/foods");
        this.foods.items = data.items ?? [];
        this.foods.selected = this.foods.items[0] ?? null;
        this.foods.lastUpdated = new Date().toLocaleString("zh-CN");
      } catch {
        this.foods.error = "美食数据加载失败，请稍后重试。";
      } finally {
        this.foods.loading = false;
      }
    },
    selectFood(item: Food | null) {
      this.foods.selected = item;
    },
  },
});
