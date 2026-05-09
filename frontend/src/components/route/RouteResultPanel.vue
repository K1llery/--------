<template>
  <Transition name="page-fade-slide">
    <aside v-if="route" class="route-result-card">
      <header class="result-header">
        <div class="result-od">
          <span class="od-from">{{ originLabel }}</span>
          <span class="od-arrow">→</span>
          <span class="od-to">{{ destinationLabel }}</span>
        </div>
        <button
          class="icon-btn"
          type="button"
          :class="{ 'btn-success-flash': justSaved }"
          :aria-label="justSaved ? '已收藏' : '收藏路线'"
          @click="handleSave"
        >
          {{ justSaved ? "★" : "☆" }}
        </button>
      </header>

      <div v-if="transportTabs.length > 1" class="transport-tabs">
        <button
          v-for="tab in transportTabs"
          :key="tab.value"
          type="button"
          class="transport-tab"
          :class="{ active: currentTransport === tab.value }"
          @click="changeTransport(tab.value)"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
          <span v-if="tabLoading === tab.value" class="tab-loading">规划中…</span>
        </button>
      </div>

      <div class="result-summary">
        <span class="summary-distance">{{ distanceLabel }}</span>
        <span class="summary-divider">·</span>
        <span class="summary-time">{{ timeLabel }}</span>
        <span class="summary-divider">·</span>
        <span class="congestion-indicator" :class="congestionClass">
          <span class="congestion-dots">{{ congestionDots }}</span>
          <span class="congestion-label">{{ congestionLabel }}</span>
        </span>
      </div>

      <p class="result-explanation">{{ route.explanation }}</p>

      <div v-if="facilityNote" class="result-note">📍 {{ facilityNote }}</div>
      <div v-if="wanderStops" class="result-note">🚶 {{ wanderStops }}</div>

      <div class="strategy-chips" v-if="strategyChips.length > 1">
        <span class="chips-label">策略</span>
        <button
          v-for="chip in strategyChips"
          :key="chip.value"
          type="button"
          class="strategy-chip"
          :class="{ active: currentStrategy === chip.value }"
          @click="changeStrategy(chip.value)"
        >
          {{ chip.icon }} {{ chip.label }}
        </button>
      </div>

      <div class="result-actions">
        <button class="primary-btn" type="button" @click="emit('start-navigation')">
          开始分段导航
        </button>
        <button
          v-if="indoorAvailable"
          class="secondary-btn"
          type="button"
          @click="emit('open-indoor', destinationCode)"
        >
          继续到楼内房间
        </button>
      </div>
    </aside>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

import { useAuthStore } from "../../stores/auth";
import { useToastStore } from "../../stores/toast";
import type { MultiRouteResult, SingleRouteResult } from "../../types/models";

type TransportValue = "walk" | "bike" | "taxi" | "shuttle" | "mixed";

const props = defineProps<{
  route: SingleRouteResult | MultiRouteResult | null;
  routeType: "single" | "multi" | "wander" | "facility";
  sceneName: string;
  originName?: string;
  /** Available transport modes for current scene context */
  availableTransports?: TransportValue[];
  /** Currently active transport (for tab highlight) */
  currentTransport?: TransportValue;
  /** Currently active strategy (chip highlight) */
  currentStrategy?: string;
  /** Loading indicator for tab being switched */
  tabLoading?: TransportValue | "";
  /** Indoor handoff available */
  indoorAvailable?: boolean;
}>();

const emit = defineEmits<{
  "change-transport": [value: TransportValue];
  "change-strategy": [value: string];
  "start-navigation": [];
  "open-indoor": [destinationCode: string];
}>();

const auth = useAuthStore();
const toast = useToastStore();
const justSaved = ref(false);

const TRANSPORT_META: Record<TransportValue, { icon: string; label: string }> = {
  walk: { icon: "🚶", label: "步行" },
  bike: { icon: "🚲", label: "自行车" },
  taxi: { icon: "🚖", label: "打车" },
  shuttle: { icon: "🚐", label: "电瓶车" },
  mixed: { icon: "🔀", label: "智能混合" },
};

const STRATEGY_META: Record<string, { icon: string; label: string }> = {
  time: { icon: "⚡", label: "最快到达" },
  distance: { icon: "📏", label: "距离最短" },
  scenic: { icon: "🌳", label: "边走边逛" },
  congestion: { icon: "🚦", label: "避开拥挤" },
  astar: { icon: "🎯", label: "A*" },
};

const transportTabs = computed(() => {
  const list = props.availableTransports ?? ["walk", "bike", "taxi"];
  return list.map((v) => ({ value: v, ...TRANSPORT_META[v] }));
});

const strategyChips = computed(() => {
  const allowed = ["time", "distance", "scenic", "congestion"];
  return allowed.map((v) => ({ value: v, ...STRATEGY_META[v] }));
});

const originLabel = computed(() => {
  if (!props.route) return "";
  return props.route.resolved_start_name || props.originName || "起点";
});

const destinationLabel = computed(() => {
  if (!props.route) return "";
  if (props.routeType === "multi") {
    const mr = props.route as MultiRouteResult;
    const stopCount = Math.max(0, (mr.ordered_stop_names?.length ?? 2) - 2);
    return `多点闭环${stopCount ? `（${stopCount}站）` : ""}`;
  }
  if (props.routeType === "wander") return "推荐漫游闭环";
  const names = props.route.path_names ?? [];
  if (props.routeType === "facility" && "facility" in props.route) {
    const sr = props.route as SingleRouteResult;
    if (sr.facility?.name) return sr.facility.name;
  }
  return names[names.length - 1] || "终点";
});

const destinationCode = computed(() => {
  if (!props.route) return "";
  const codes = props.route.path_codes ?? [];
  return codes[codes.length - 1] || "";
});

const distanceLabel = computed(() => {
  if (!props.route) return "";
  const m = props.route.total_distance_m;
  if (m >= 1000) return `${(m / 1000).toFixed(2)} 公里`;
  return `${Math.round(m)} 米`;
});

const timeLabel = computed(() => {
  if (!props.route) return "";
  const min = props.route.estimated_minutes;
  return `${Math.round(min)} 分钟`;
});

const avgCongestion = computed(() => {
  if (!props.route) return 0;
  if ("average_congestion" in props.route && typeof props.route.average_congestion === "number") {
    return props.route.average_congestion;
  }
  // Fallback: average from segments
  const segs = props.route.segments ?? [];
  if (!segs.length) return 0;
  return segs.reduce((s, seg) => s + (seg.congestion ?? 0), 0) / segs.length;
});

const congestionDots = computed(() => {
  const c = avgCongestion.value;
  if (c < 0.3) return "●○○";
  if (c < 0.6) return "●●○";
  return "●●●";
});

const congestionLabel = computed(() => {
  const c = avgCongestion.value;
  if (c < 0.3) return "通畅";
  if (c < 0.6) return "稍拥挤";
  return "拥堵";
});

const congestionClass = computed(() => {
  const c = avgCongestion.value;
  if (c < 0.3) return "congestion-low";
  if (c < 0.6) return "congestion-mid";
  return "congestion-high";
});

const facilityNote = computed(() => {
  if (props.routeType !== "facility" || !props.route) return "";
  const sr = props.route as SingleRouteResult;
  if (!sr.facility) return "";
  return `${sr.facility.name}（${sr.facility.facility_label}）`;
});

const wanderStops = computed(() => {
  if (!props.route || !["wander", "multi"].includes(props.routeType)) return "";
  const mr = props.route as MultiRouteResult;
  return mr.ordered_stop_names?.join(" → ") ?? "";
});

const changeTransport = (value: TransportValue) => {
  if (value === props.currentTransport) return;
  emit("change-transport", value);
};

const changeStrategy = (value: string) => {
  if (value === props.currentStrategy) return;
  emit("change-strategy", value);
};

const handleSave = async () => {
  if (!props.route) return;
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  try {
    await auth.saveRouteFavorite({
      scene_name: props.sceneName,
      strategy: props.route.strategy,
      transport_mode: props.route.transport_mode,
      path_codes: props.route.path_codes,
      path_names: props.route.path_names,
      total_distance_m: props.route.total_distance_m,
      estimated_minutes: props.route.estimated_minutes,
      explanation: props.route.explanation,
    });
    justSaved.value = true;
    toast.success("路线已收藏");
    setTimeout(() => {
      justSaved.value = false;
    }, 2000);
  } catch {
    toast.error("收藏失败，请稍后重试。");
  }
};

watch(
  () => props.route,
  () => {
    justSaved.value = false;
  },
);
</script>
