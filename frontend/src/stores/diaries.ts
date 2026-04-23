import { defineStore } from "pinia";

import { api } from "../api/client";
import type { Diary } from "../types/models";
import type { DiaryListResponse, DiaryRateResponse, DiarySearchResponse } from "../types/api";

interface DiaryState {
  items: Diary[];
  loading: boolean;
  error: string;
  selected: Diary | null;
  lastUpdated: string;
  searchResults: Diary[];
  searchLoading: boolean;
  searchError: string;
  searchLastUpdated: string;
}

export const useDiaryStore = defineStore("diaries", {
  state: (): DiaryState => ({
    items: [],
    loading: false,
    error: "",
    selected: null,
    lastUpdated: "",
    searchResults: [],
    searchLoading: false,
    searchError: "",
    searchLastUpdated: "",
  }),
  actions: {
    async load(force = false) {
      if (this.loading) return;
      if (!force && this.items.length > 0) return;
      this.loading = true;
      this.error = "";
      try {
        const { data } = await api.get<DiaryListResponse>("/diaries");
        this.items = data.items ?? [];
        this.selected = this.items[0] ?? null;
        this.lastUpdated = new Date().toLocaleString("zh-CN");
      } catch {
        this.error = "日记列表加载失败。";
      } finally {
        this.loading = false;
      }
    },
    async search(query: string) {
      this.searchLoading = true;
      this.searchError = "";
      try {
        const { data } = await api.post<DiarySearchResponse>("/diaries/search", { query });
        this.searchResults = data.items ?? [];
        this.searchLastUpdated = new Date().toLocaleString("zh-CN");
      } catch {
        this.searchError = "日记搜索失败。";
      } finally {
        this.searchLoading = false;
      }
    },
    _syncInCollections(diary: Diary) {
      const listIndex = this.items.findIndex((entry) => entry.id === diary.id);
      if (listIndex >= 0) this.items[listIndex] = diary;
      const searchIndex = this.searchResults.findIndex((entry) => entry.id === diary.id);
      if (searchIndex >= 0) this.searchResults[searchIndex] = diary;
    },
    async select(item: Diary, countView = true) {
      try {
        const { data } = await api.get<Diary>(`/diaries/${item.id}`);
        this.selected = data;
        if (countView) {
          const viewResponse = await api.post<{ diary: Diary }>(`/diaries/${item.id}/view`);
          this.selected = viewResponse.data.diary;
          this._syncInCollections(viewResponse.data.diary);
        }
      } catch {
        this.error = "加载日记详情失败。";
      }
    },
    async rate(diaryId: number, score: number): Promise<DiaryRateResponse | null> {
      const { data } = await api.post<DiaryRateResponse>(`/diaries/${diaryId}/rate`, { score });
      this.selected = data.diary;
      this._syncInCollections(data.diary);
      this.lastUpdated = new Date().toLocaleString("zh-CN");
      return data;
    },
  },
});
