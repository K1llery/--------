import { ref } from "vue";

import { api } from "../api/client";
import type { SingleRouteResult, MultiRouteResult } from "../types/models";

export function useRoutePlanner() {
  const singleRoute = ref<SingleRouteResult | null>(null);
  const multiRoute = ref<MultiRouteResult | null>(null);
  const singleLoading = ref(false);
  const multiLoading = ref(false);
  const error = ref("");
  const selectedAlternativeStrategy = ref("");

  const planSingle = async (payload: Record<string, unknown>) => {
    error.value = "";
    singleLoading.value = true;
    multiRoute.value = null;
    selectedAlternativeStrategy.value = "";
    try {
      const { data } = await api.post<SingleRouteResult>("/routes/single", payload);
      singleRoute.value = data;
    } catch (err: any) {
      error.value = err?.response?.data?.detail || "路线规划失败，请稍后重试。";
    } finally {
      singleLoading.value = false;
    }
  };

  const planMulti = async (payload: Record<string, unknown>) => {
    error.value = "";
    multiLoading.value = true;
    singleRoute.value = null;
    selectedAlternativeStrategy.value = "";
    try {
      const { data } = await api.post<MultiRouteResult>("/routes/multi", payload);
      multiRoute.value = data;
    } catch (err: any) {
      error.value = err?.response?.data?.detail || "多点路线规划失败，请稍后重试。";
    } finally {
      multiLoading.value = false;
    }
  };

  const reset = () => {
    singleRoute.value = null;
    multiRoute.value = null;
    selectedAlternativeStrategy.value = "";
    error.value = "";
  };

  return {
    singleRoute,
    multiRoute,
    singleLoading,
    multiLoading,
    error,
    selectedAlternativeStrategy,
    planSingle,
    planMulti,
    reset,
  };
}
