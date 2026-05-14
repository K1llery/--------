import { defineStore } from "pinia";

import { api } from "../api/client";
import type { PlanListResponse } from "../types/api";
import type { TravelPlan } from "../types/models";

interface PlanState {
  items: TravelPlan[];
  loading: boolean;
  error: string;
  selected: TravelPlan | null;
}

type PlanPayload = {
  title: string;
  days: TravelPlan["days"];
};

type PlanUpdatePayload = {
  title?: string;
  days?: TravelPlan["days"];
};

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
    async createPlan(payload: PlanPayload): Promise<TravelPlan | null> {
      try {
        const { data } = await api.post<TravelPlan>("/plans", payload);
        this.items.unshift(data);
        return data;
      } catch {
        this.error = "创建计划失败。";
        return null;
      }
    },
    async updatePlan(planId: number, payload: PlanUpdatePayload): Promise<TravelPlan | null> {
      try {
        const { data } = await api.put<TravelPlan>(`/plans/${planId}`, payload);
        const index = this.items.findIndex((plan) => plan.id === planId);
        if (index >= 0) this.items[index] = data;
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
        this.items = this.items.filter((plan) => plan.id !== planId);
        if (this.selected?.id === planId) this.selected = null;
        return true;
      } catch {
        this.error = "删除计划失败。";
        return false;
      }
    },
  },
});
