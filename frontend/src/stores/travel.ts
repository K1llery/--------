import { defineStore } from "pinia";

import { api } from "../api/client";

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

export const useTravelStore = defineStore("travel", {
  state: () => ({
    destinations: createResourceState<any>(),
    foods: createResourceState<any>(),
    diaries: createResourceState<any>(),
    diarySearchResults: createResourceState<any>(),
  }),
  actions: {
    async loadFeaturedDestinations(force = false) {
      if (this.destinations.loading) return;
      if (!force && this.destinations.items.length > 0) return;
      this.destinations.loading = true;
      this.destinations.error = "";
      try {
        const { data } = await api.get("/destinations/featured");
        this.destinations.items = data;
        this.destinations.selected = data[0] ?? null;
        this.destinations.lastUpdated = new Date().toLocaleString("zh-CN");
      } catch (error) {
        this.destinations.error = "精选目的地加载失败，请确认后端是否已启动。";
      } finally {
        this.destinations.loading = false;
      }
    },
    selectDestination(item: any) {
      this.destinations.selected = item;
    },
    async loadFoods(force = false) {
      if (this.foods.loading) return;
      if (!force && this.foods.items.length > 0) return;
      this.foods.loading = true;
      this.foods.error = "";
      try {
        const { data } = await api.get("/foods");
        this.foods.items = data.items ?? [];
        this.foods.selected = this.foods.items[0] ?? null;
        this.foods.lastUpdated = new Date().toLocaleString("zh-CN");
      } catch (error) {
        this.foods.error = "美食数据加载失败，请稍后重试。";
      } finally {
        this.foods.loading = false;
      }
    },
    selectFood(item: any) {
      this.foods.selected = item;
    },
    async loadDiaries(force = false) {
      if (this.diaries.loading) return;
      if (!force && this.diaries.items.length > 0) return;
      this.diaries.loading = true;
      this.diaries.error = "";
      try {
        const { data } = await api.get("/diaries");
        this.diaries.items = data.items ?? [];
        this.diaries.selected = this.diaries.items[0] ?? null;
        this.diaries.lastUpdated = new Date().toLocaleString("zh-CN");
      } catch (error) {
        this.diaries.error = "日记列表加载失败。";
      } finally {
        this.diaries.loading = false;
      }
    },
    async searchDiaries(query: string) {
      this.diarySearchResults.loading = true;
      this.diarySearchResults.error = "";
      try {
        const { data } = await api.post("/diaries/search", { query });
        this.diarySearchResults.items = data.items ?? [];
        this.diarySearchResults.lastUpdated = new Date().toLocaleString("zh-CN");
      } catch (error) {
        this.diarySearchResults.error = "日记搜索失败。";
      } finally {
        this.diarySearchResults.loading = false;
      }
    },
    _syncDiaryInCollections(diary: any) {
      const listIndex = this.diaries.items.findIndex((entry) => entry.id === diary.id);
      if (listIndex >= 0) {
        this.diaries.items[listIndex] = diary;
      }
      const searchIndex = this.diarySearchResults.items.findIndex((entry) => entry.id === diary.id);
      if (searchIndex >= 0) {
        this.diarySearchResults.items[searchIndex] = diary;
      }
    },
    async selectDiary(item: any, countView = true) {
      try {
        const { data } = await api.get(`/diaries/${item.id}`);
        this.diaries.selected = data;
        if (countView) {
          const viewResponse = await api.post(`/diaries/${item.id}/view`);
          this.diaries.selected = viewResponse.data.diary;
          this._syncDiaryInCollections(viewResponse.data.diary);
        }
      } catch (error) {
        this.diaries.error = "加载日记详情失败。";
      }
    },
    async rateDiary(diaryId: number, score: number) {
      const { data } = await api.post(`/diaries/${diaryId}/rate`, { score });
      this.diaries.selected = data.diary;
      this._syncDiaryInCollections(data.diary);
      this.diaries.lastUpdated = new Date().toLocaleString("zh-CN");
      return data;
    },
  },
});
