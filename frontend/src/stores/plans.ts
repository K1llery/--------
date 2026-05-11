import { defineStore } from "pinia";

import { api } from "../api/client";
import type { TravelPlan } from "../types/models";
import type { PlanListResponse } from "../types/api";

interface PlanState {
  items: TravelPlan[];
  loading: boolean;
  error: string;
  selected: TravelPlan | null;
}

export const usePlanStore = defineStore("plans", {
  state: (): PlanState => ({
    items: [],
    loading: false,
    error: "",
    selected: null,
  }),
  actions: {
    async loadPlans() {
      if (this.loading) return;
      this.loading = true;
      this.error = "";
      try {
        const { data } = await api.get<PlanListResponse>("/plans");
        this.items = data.items ?? [];
      } catch {
        this.error = "加载旅行计划失败。";
      } finally {
        this.loading = false;
      }
    },
    async getPlan(planId: number): Promise<TravelPlan | null> {
      try {
        const { data } = await api.get<TravelPlan>(`/plans/${planId}`);
        this.selected = data;
        return data;
      } catch {
        this.error = "加载计划详情失败。";
        return null;
      }
    },
    async createPlan(payload: { title: string; days: any[] }): Promise<TravelPlan | null> {
      try {
        const { data } = await api.post<TravelPlan>("/plans", payload);
        this.items.unshift(data);
        return data;
      } catch {
        this.error = "创建计划失败。";
        return null;
      }
    },
    async updatePlan(planId: number, payload: { title?: string; days?: any[] }): Promise<TravelPlan | null> {
      try {
        const { data } = await api.put<TravelPlan>(`/plans/${planId}`, payload);
        const idx = this.items.findIndex((p) => p.id === planId);
        if (idx >= 0) this.items[idx] = data;
        if (this.selected?.id === planId) this.selected = data;
        return data;
      } catch {
        this.error = "更新计划失败。";
        return null;
      }
    },
    async deletePlan(planId: number): Promise<boolean> {
      try {
        await api.delete(`/plans/${planId}`);
        this.items = this.items.filter((p) => p.id !== planId);
        if (this.selected?.id === planId) this.selected = null;
        return true;
      } catch {
        this.error = "删除计划失败。";
        return false;
      }
    },
  },
});
