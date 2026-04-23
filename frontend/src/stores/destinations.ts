import { defineStore } from "pinia";

import { api } from "../api/client";
import type { Destination } from "../types/models";

interface DestinationState {
  items: Destination[];
  loading: boolean;
  error: string;
  selected: Destination | null;
  lastUpdated: string;
}

export const useDestinationStore = defineStore("destinations", {
  state: (): DestinationState => ({
    items: [],
    loading: false,
    error: "",
    selected: null,
    lastUpdated: "",
  }),
  actions: {
    async loadFeatured(force = false) {
      if (this.loading) return;
      if (!force && this.items.length > 0) return;
      this.loading = true;
      this.error = "";
      try {
        const { data } = await api.get<Destination[]>("/destinations/featured");
        this.items = data;
        this.selected = data[0] ?? null;
        this.lastUpdated = new Date().toLocaleString("zh-CN");
      } catch {
        this.error = "精选目的地加载失败，请确认后端是否已启动。";
      } finally {
        this.loading = false;
      }
    },
    select(item: Destination) {
      this.selected = item;
    },
  },
});
