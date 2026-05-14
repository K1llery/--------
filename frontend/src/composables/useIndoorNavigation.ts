import { ref } from "vue";

import { api } from "../api/client";
import type { IndoorRouteResult } from "../types/models";

type ApiFailure = {
  response?: {
    data?: {
      detail?: string;
    };
  };
};

export function useIndoorNavigation() {
  const indoorRoute = ref<IndoorRouteResult | null>(null);
  const indoorLoading = ref(false);
  const selectedBuildingCode = ref("");
  const startNodeCode = ref("");
  const endNodeCode = ref("");
  const strategy = ref("time");
  const mobilityMode = ref("normal");

  const planRoute = async () => {
    if (!selectedBuildingCode.value || !startNodeCode.value || !endNodeCode.value) {
      return "当前场景缺少可用的室内导航点位。";
    }

    indoorLoading.value = true;
    try {
      const { data } = await api.post<IndoorRouteResult>("/indoor/route", {
        building_code: selectedBuildingCode.value,
        start_node_code: startNodeCode.value,
        end_node_code: endNodeCode.value,
        strategy: strategy.value,
        mobility_mode: mobilityMode.value,
      });
      indoorRoute.value = data;
      return null;
    } catch (err: unknown) {
      return (err as ApiFailure)?.response?.data?.detail || "室内导航失败，请稍后重试。";
    } finally {
      indoorLoading.value = false;
    }
  };

  const reset = () => {
    indoorRoute.value = null;
  };

  return {
    indoorRoute,
    indoorLoading,
    selectedBuildingCode,
    startNodeCode,
    endNodeCode,
    strategy,
    mobilityMode,
    planRoute,
    reset,
  };
}
