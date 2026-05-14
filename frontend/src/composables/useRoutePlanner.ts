import { ref } from "vue";

import { api } from "../api/client";
import type {
  MultiRouteResult,
  NearbyFacilityRouteResult,
  SingleRouteResult,
  WanderRouteResult,
} from "../types/models";

type ApiFailure = {
  response?: {
    data?: {
      detail?: string;
    };
  };
};

export function useRoutePlanner() {
  const singleRoute = ref<SingleRouteResult | null>(null);
  const multiRoute = ref<MultiRouteResult | null>(null);
  const wanderRoute = ref<WanderRouteResult | null>(null);
  const facilityRoute = ref<NearbyFacilityRouteResult | null>(null);
  const singleLoading = ref(false);
  const multiLoading = ref(false);
  const wanderLoading = ref(false);
  const facilityLoading = ref(false);
  const error = ref("");
  const selectedAlternativeStrategy = ref("");

  const planSingle = async (payload: Record<string, unknown>) => {
    error.value = "";
    singleLoading.value = true;
    multiRoute.value = null;
    wanderRoute.value = null;
    facilityRoute.value = null;
    selectedAlternativeStrategy.value = "";

    try {
      const { data } = await api.post<SingleRouteResult>("/routes/single", payload);
      singleRoute.value = data;
    } catch (err: unknown) {
      error.value = (err as ApiFailure)?.response?.data?.detail || "路线规划失败，请稍后重试。";
    } finally {
      singleLoading.value = false;
    }
  };

  const planMulti = async (payload: Record<string, unknown>) => {
    error.value = "";
    multiLoading.value = true;
    singleRoute.value = null;
    wanderRoute.value = null;
    facilityRoute.value = null;
    selectedAlternativeStrategy.value = "";

    try {
      const { data } = await api.post<MultiRouteResult>("/routes/multi", payload);
      multiRoute.value = data;
    } catch (err: unknown) {
      error.value = (err as ApiFailure)?.response?.data?.detail || "多点路线规划失败，请稍后重试。";
    } finally {
      multiLoading.value = false;
    }
  };

  const planWander = async (payload: Record<string, unknown>) => {
    error.value = "";
    wanderLoading.value = true;
    singleRoute.value = null;
    multiRoute.value = null;
    facilityRoute.value = null;
    selectedAlternativeStrategy.value = "";

    try {
      const { data } = await api.post<WanderRouteResult>("/routes/wander", payload);
      wanderRoute.value = data;
    } catch (err: unknown) {
      error.value = (err as ApiFailure)?.response?.data?.detail || "漫游路线生成失败，请稍后重试。";
    } finally {
      wanderLoading.value = false;
    }
  };

  const planNearbyFacility = async (payload: Record<string, unknown>) => {
    error.value = "";
    facilityLoading.value = true;
    singleRoute.value = null;
    multiRoute.value = null;
    wanderRoute.value = null;
    selectedAlternativeStrategy.value = "";

    try {
      const { data } = await api.post<NearbyFacilityRouteResult>("/routes/nearby-facility", payload);
      facilityRoute.value = data;
    } catch (err: unknown) {
      error.value =
        (err as ApiFailure)?.response?.data?.detail || "最近设施路线生成失败，请稍后重试。";
    } finally {
      facilityLoading.value = false;
    }
  };

  const reset = () => {
    singleRoute.value = null;
    multiRoute.value = null;
    wanderRoute.value = null;
    facilityRoute.value = null;
    selectedAlternativeStrategy.value = "";
    error.value = "";
  };

  return {
    singleRoute,
    multiRoute,
    wanderRoute,
    facilityRoute,
    singleLoading,
    multiLoading,
    wanderLoading,
    facilityLoading,
    error,
    selectedAlternativeStrategy,
    planSingle,
    planMulti,
    planWander,
    planNearbyFacility,
    reset,
  };
}
