<template>
  <section class="panel-card route-page route-command">
    <div class="section-top">
      <div>
        <h2>地图导航</h2>
        <p>{{ supportsRouting ? "输入目的地，自动为你规划最优路线" : "选择支持导航的场景以开始规划" }}</p>
      </div>
    </div>

    <SceneSelector
      :cities="cities"
      :scenes="visibleScenes"
      :model-city="selectedCity"
      :model-scene="selectedSceneName"
      @update:model-city="handleCityChange"
      @update:model-scene="handleSceneChange"
    />

    <template v-if="supportsRouting">
      <FacilityChips
        :facilities="loader.facilities.value"
        :active-type="activeFacilityType"
        @update:active-type="setFacilityFilter"
      />

      <div class="map-interaction-wrapper">
        <RouteMap
          :nodes="mapNodes"
          :path="displayPathCodes"
          :current-location="currentLocation"
          :interaction-mode="nav.mapInteractionMode.value"
          :active-segment-path="nav.activeSegmentPath.value"
          :alternative-routes="alternativeMapRoutes"
          :fit-bounds="nav.activeSegmentBounds.value"
          :segments="activeSegments"
          :overlay-facilities="overlayFacilities"
          @map-click="nav.onMapClick"
          @marker-click="handleMarkerClick"
          @facility-click="handleFacilityClick"
          @context-action="handleContextAction"
        />
        <Transition name="page-fade-slide">
          <div
            v-if="nav.mapInteractionMode.value !== 'idle'"
            class="map-mode-indicator"
          >
            {{ nav.mapInteractionMode.value === "set-origin" ? "点击地图选择起点" : "点击地图选择终点" }}
            <button class="secondary-btn" type="button" @click="nav.cancelMapInteraction()">
              取消
            </button>
          </div>
        </Transition>

        <RouteSearchBar
          ref="searchBarRef"
          :nodes="(loader.scene.value?.nodes ?? []) as any"
          :facilities="loader.facilities.value"
          :use-current-location="useCurrentLocation"
          :origin-name="originDisplayName"
          :trip-stop-codes="tripStopCodes"
          @select-destination="handleSelectDestination"
          @add-destination-to-trip="handleAddDestinationToTrip"
          @toggle-current-location="toggleCurrentLocation"
          @open-multi-stop="multiStopOpen = true"
          @open-recommend="recommendOpen = true"
          @open-origin-picker="openOriginPicker"
        />

        <RouteTripBar
          v-if="tripStops.length"
          :stops="tripStops as any"
          :loading="planner.multiLoading.value"
          :origin-label="routeStartLabel"
          @remove-stop="removeTripStop"
          @plan-trip="runPlanTrip"
          @open-multi-stop="multiStopOpen = true"
          @clear="clearTripStops"
        />
      </div>

      <Transition name="page-fade-slide">
        <div v-if="routeError" class="status-card error-card">
          {{ routeError }}
          <button class="secondary-btn" type="button" @click="routeError = ''">关闭</button>
        </div>
      </Transition>

      <RoutePlanningOverlay :visible="isPlanning" />

      <RouteResultPanel
        v-if="activeRoute"
        :route="activeRoute"
        :route-type="resultPanelType"
        :scene-name="selectedSceneName"
        :origin-name="originDisplayName"
        :available-transports="availableTransports"
        :current-transport="activeTransport"
        :current-strategy="activeStrategy"
        :tab-loading="tabLoading"
        :indoor-available="indoorHandoffAvailable"
        @change-transport="handleChangeTransport"
        @change-strategy="handleChangeStrategy"
        @start-navigation="nav.goToSegment(0)"
        @open-indoor="openIndoorHandoff"
      />

      <RouteAlternatives
        v-if="activeAlternatives.length"
        :alternatives="activeAlternatives"
        :selected-strategy="planner.selectedAlternativeStrategy.value"
        @select="planner.selectedAlternativeStrategy.value = $event"
        @hover="nav.highlightedAltIndex.value = $event"
      />

      <SegmentTimeline
        v-if="activeSegments.length"
        :segments="activeSegments"
        :active-index="nav.activeSegmentIndex.value"
        @select-segment="nav.goToSegment"
      />

      <SegmentNavBar
        v-if="activeSegments.length && nav.activeSegmentIndex.value !== null"
        :current-index="nav.activeSegmentIndex.value ?? -1"
        :total-segments="activeSegments.length"
        @prev="nav.prevSegment()"
        @next="nav.nextSegment()"
        @exit-navigation="nav.exitNavigation()"
      />

      <RouteEmptyState
        v-if="!activeRoute && !isPlanning && !routeError"
        context="initial"
      />

      <MultiStopDrawer
        :visible="multiStopOpen"
        :place-options="placeOptions as any"
        :loading="planner.multiLoading.value"
        :initial-start-code="effectiveStartCode"
        :initial-stop-codes="tripStopCodes"
        @close="multiStopOpen = false"
        @submit="handleMultiSubmit"
      />

      <RecommendDrawer
        :visible="recommendOpen"
        :loading="planner.wanderLoading.value"
        @close="recommendOpen = false"
        @submit="handleRecommendSubmit"
      />

      <IndoorRoutePanel
        as-drawer
        :buildings="indoorBuildingsForScene"
        :drawer-open="indoorDrawerOpen"
        :initial-building-code="indoorHandoffBuildingCode"
        :initial-start-node="indoorHandoffStartNode"
        @close="indoorDrawerOpen = false"
        @route-error="(msg) => { routeError = msg }"
      />
    </template>

    <div v-else class="status-card">
      {{ selectedCity }}当前支持城市地图浏览与精选地点查看，精细导航即将上线。
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import RouteMap from "../components/RouteMap.vue";
import FacilityChips from "../components/route/FacilityChips.vue";
import IndoorRoutePanel from "../components/route/IndoorRoutePanel.vue";
import MultiStopDrawer from "../components/route/MultiStopDrawer.vue";
import RecommendDrawer from "../components/route/RecommendDrawer.vue";
import RouteAlternatives from "../components/route/RouteAlternatives.vue";
import RouteEmptyState from "../components/route/RouteEmptyState.vue";
import RoutePlanningOverlay from "../components/route/RoutePlanningOverlay.vue";
import RouteResultPanel from "../components/route/RouteResultPanel.vue";
import RouteSearchBar from "../components/route/RouteSearchBar.vue";
import RouteTripBar from "../components/route/RouteTripBar.vue";
import SceneSelector from "../components/route/SceneSelector.vue";
import SegmentNavBar from "../components/route/SegmentNavBar.vue";
import SegmentTimeline from "../components/route/SegmentTimeline.vue";
import { useGeolocation } from "../composables/useGeolocation";
import { useRouteNavigation } from "../composables/useRouteNavigation";
import { useRoutePlanner } from "../composables/useRoutePlanner";
import { useSceneLoader } from "../composables/useSceneLoader";
import { useToastStore } from "../stores/toast";
import type { MultiRouteResult, RouteSegment, SingleRouteResult } from "../types/models";
import { buildMultiRoutePayload, type RouteBasePayload } from "../utils/routePayload";

type TransportValue = "walk" | "bike" | "taxi" | "shuttle" | "mixed";

const loader = useSceneLoader();
const planner = useRoutePlanner();
const geo = useGeolocation();
const toast = useToastStore();

const cities = ["广州", "上海", "北京", "深圳"];
const selectedCity = ref("北京");
const selectedSceneName = ref("BUPT_Main_Campus");

// Origin / destination state (no more "mode")
const useCurrentLocation = ref(true);
const originCode = ref("");
const destinationCode = ref("");
const activeTransport = ref<TransportValue>("mixed");
const activeStrategy = ref("time");
const tabLoading = ref<TransportValue | "">("");
const tripStopCodes = ref<string[]>([]);

// Drawers / overlays
const multiStopOpen = ref(false);
const recommendOpen = ref(false);
const indoorDrawerOpen = ref(false);
const indoorHandoffBuildingCode = ref("");
const indoorHandoffStartNode = ref("");

// Facility filter overlay
const activeFacilityType = ref("");

const routeError = ref("");
const searchBarRef = ref<InstanceType<typeof RouteSearchBar> | null>(null);

// Track which "shape" of route is currently shown
const lastRouteShape = ref<"single" | "multi" | "wander" | "facility">("single");

const visibleScenes = computed(() =>
  loader.scenes.value.filter((item) => item.city === selectedCity.value),
);

const currentScene = computed(() =>
  visibleScenes.value.find((item) => item.name === selectedSceneName.value),
);

const supportsRouting = computed(() => currentScene.value?.supports_routing ?? false);

// Scene context infers default available transports
const availableTransports = computed<TransportValue[]>(() => {
  const sceneName = selectedSceneName.value.toLowerCase();
  // Heuristic: smart mixed is the realistic default, with explicit mode choices kept one tap away.
  if (sceneName.includes("campus") || sceneName.includes("university") || sceneName.includes("bupt")) {
    return ["mixed", "walk", "bike"];
  }
  if (
    sceneName.includes("scenic") ||
    sceneName.includes("park") ||
    sceneName.includes("museum") ||
    sceneName.includes("gugong") ||
    sceneName.includes("palace")
  ) {
    return ["mixed", "walk", "shuttle"];
  }
  return ["mixed", "walk", "bike", "taxi"];
});

const placeOptions = computed(() => [
  ...(loader.scene.value?.nodes ?? []),
  ...loader.facilities.value,
]);

const tripStops = computed(() => {
  const placesByCode = new Map(placeOptions.value.map((item) => [item.code, item]));
  return tripStopCodes.value
    .map((code) => placesByCode.get(code))
    .filter((item): item is NonNullable<typeof item> => Boolean(item));
});

const overlayFacilities = computed(() => {
  if (!activeFacilityType.value) return [];
  return loader.facilities.value.filter(
    (f) => (f.normalized_type || f.facility_type) === activeFacilityType.value,
  );
});

const indoorBuildingsForScene = computed(() =>
  loader.indoorBuildings.value.filter((b) => b.scene_name === selectedSceneName.value),
);

const mapNodes = computed(() => {
  const visibleNodes = supportsRouting.value
    ? placeOptions.value
    : loader.featuredDestinations.value
        .filter((item) => item.city === selectedCity.value)
        .map((item) => ({
          code: item.source_id,
          name: item.name,
          latitude: item.latitude,
          longitude: item.longitude,
        }));
  const nodeMap = new Map(visibleNodes.map((item) => [item.code, item]));
  activeRoute.value?.route_nodes?.forEach((node) => {
    nodeMap.set(node.code, node);
  });
  return [...nodeMap.values()];
});

const currentLocation = computed(() => geo.currentLocation.value);

const activeRoute = computed<SingleRouteResult | MultiRouteResult | null>(() => {
  if (
    planner.selectedAlternativeStrategy.value &&
    planner.singleRoute.value?.alternatives?.length
  ) {
    return (
      planner.singleRoute.value.alternatives.find(
        (item) => item.strategy === planner.selectedAlternativeStrategy.value,
      ) ?? planner.singleRoute.value
    );
  }
  return (
    planner.facilityRoute.value ||
    planner.wanderRoute.value ||
    planner.multiRoute.value ||
    planner.singleRoute.value
  );
});

const activeSegments = computed<RouteSegment[]>(() => activeRoute.value?.segments ?? []);
const displayPathCodes = computed<string[]>(() => activeRoute.value?.path_codes ?? []);

const activeAlternatives = computed<SingleRouteResult[]>(
  () => planner.singleRoute.value?.alternatives ?? [],
);

const isPlanning = computed(
  () =>
    planner.singleLoading.value ||
    planner.wanderLoading.value ||
    planner.facilityLoading.value ||
    planner.multiLoading.value,
);

const resultPanelType = computed<"single" | "multi" | "wander" | "facility">(
  () => lastRouteShape.value,
);

const originDisplayName = computed(() => {
  if (useCurrentLocation.value) return "我的位置";
  if (!originCode.value) return "";
  const node = placeOptions.value.find((p) => p.code === originCode.value);
  return node?.name || "";
});

const routeStartLabel = computed(
  () => originDisplayName.value || loader.scene.value?.nodes?.[0]?.name || "起点",
);

const effectiveStartCode = computed(
  () => originCode.value || loader.scene.value?.nodes?.[0]?.code || "",
);

const indoorHandoffAvailable = computed(() => {
  if (!activeRoute.value) return false;
  const codes = activeRoute.value.path_codes ?? [];
  const lastCode = codes[codes.length - 1];
  if (!lastCode) return false;
  const lastName = (activeRoute.value.path_names ?? []).slice(-1)[0] ?? "";
  return indoorBuildingsForScene.value.some(
    (b) => b.building_name === lastName || b.building_code === lastCode,
  );
});

const nav = useRouteNavigation({
  segments: activeSegments,
  routeNodes: computed(() => activeRoute.value?.route_nodes ?? []),
  allNodes: computed(() => placeOptions.value.map((n) => ({
    code: n.code,
    name: n.name,
    latitude: n.latitude,
    longitude: n.longitude,
    route_node_type: (n as any).route_node_type,
  }))),
});

const alternativeMapRoutes = computed(() => {
  const altColors = ["#4f8cf7", "#34a853", "#ea4335", "#fbbc04"];
  return activeAlternatives.value.map((alt, i) => ({
    pathCodes: alt.path_codes,
    color: altColors[i % altColors.length],
    label: alt.strategy_label,
  }));
});

// When user picks origin/destination via map clicks, sync to local state
watch(
  () => nav.selectedOriginCode.value,
  (code) => {
    if (code) {
      useCurrentLocation.value = false;
      originCode.value = code;
      // Auto re-plan if there's already a destination
      if (destinationCode.value) {
        runPlanSingle();
      }
    }
  },
);

watch(
  () => nav.selectedDestinationCode.value,
  (code) => {
    if (code) {
      destinationCode.value = code;
      runPlanSingle();
    }
  },
);

const buildBasePayload = (): RouteBasePayload => {
  const payload: RouteBasePayload = {
    scene_name: selectedSceneName.value,
    start_code: originCode.value || (loader.scene.value?.nodes?.[0]?.code ?? ""),
    transport_mode: activeTransport.value,
    prefer_nearest_start: false,
  };
  if (useCurrentLocation.value && geo.currentLocation.value) {
    payload.prefer_nearest_start = true;
    payload.start_latitude = geo.currentLocation.value.latitude;
    payload.start_longitude = geo.currentLocation.value.longitude;
  } else {
    payload.prefer_nearest_start = false;
  }
  return payload;
};

const ensureLocationIfNeeded = async (): Promise<boolean> => {
  if (!useCurrentLocation.value) return true;
  if (geo.currentLocation.value) return true;
  await geo.capture();
  if (!geo.currentLocation.value) {
    routeError.value = "无法获取当前位置，请关闭'我的位置'开关后再试。";
    return false;
  }
  return true;
};

const runPlanSingle = async () => {
  if (!destinationCode.value) return;
  if (!(await ensureLocationIfNeeded())) return;
  routeError.value = "";
  nav.resetNavigation();
  const payload = {
    ...buildBasePayload(),
    end_code: destinationCode.value,
    strategy: activeStrategy.value,
  };
  await planner.planSingle(payload);
  if (planner.error.value) routeError.value = planner.error.value;
  else lastRouteShape.value = "single";
};

const handleSelectDestination = async (code: string) => {
  destinationCode.value = code;
  await runPlanSingle();
};

const handleAddDestinationToTrip = (code: string) => {
  const place = placeOptions.value.find((item) => item.code === code);
  if (!place) return;
  if (!useCurrentLocation.value && code === effectiveStartCode.value) {
    toast.info("这个地点已经是当前起点");
    return;
  }
  if (tripStopCodes.value.includes(code)) {
    toast.info("这个地点已经在行程里");
    return;
  }
  tripStopCodes.value = [...tripStopCodes.value, code];
  toast.success(`已加入行程：${place.name}`);
};

const removeTripStop = (code: string) => {
  tripStopCodes.value = tripStopCodes.value.filter((item) => item !== code);
};

const clearTripStops = () => {
  tripStopCodes.value = [];
};

const runPlanMultiTargets = async (
  targetCodes: string[],
  transportMode: string,
  strategy: string,
) => {
  const basePayload = buildBasePayload();
  const normalizedTargets = targetCodes.filter((code, index, list) => {
    return code !== basePayload.start_code && list.indexOf(code) === index;
  });
  if (normalizedTargets.length < 2) {
    routeError.value = "至少添加 2 个地点后才能优化多点路线。";
    return;
  }
  if (!(await ensureLocationIfNeeded())) return;
  routeError.value = "";
  nav.resetNavigation();
  activeTransport.value = transportMode as TransportValue;
  activeStrategy.value = strategy;
  await planner.planMulti(
    buildMultiRoutePayload(basePayload, {
      stopCodes: normalizedTargets,
      transportMode,
      strategy,
    }),
  );
  if (planner.error.value) {
    routeError.value = planner.error.value;
  } else {
    tripStopCodes.value = [...normalizedTargets];
    lastRouteShape.value = "multi";
    multiStopOpen.value = false;
  }
};

const runPlanTrip = async () => {
  await runPlanMultiTargets(tripStopCodes.value, activeTransport.value, activeStrategy.value);
};

const handleChangeTransport = async (value: TransportValue) => {
  if (value === activeTransport.value) return;
  activeTransport.value = value;
  tabLoading.value = value;
  try {
    if (lastRouteShape.value === "single") {
      await runPlanSingle();
    } else if (lastRouteShape.value === "wander" && planner.wanderRoute.value) {
      await runPlanWander(planner.wanderRoute.value.duration_minutes ?? 45, activeStrategy.value);
    } else if (lastRouteShape.value === "facility" && planner.facilityRoute.value) {
      await runPlanFacility(
        planner.facilityRoute.value.facility?.facility_type ?? "restroom",
        planner.facilityRoute.value.search_radius_m ?? 1500,
      );
    } else if (lastRouteShape.value === "multi" && planner.multiRoute.value) {
      const targets = tripStopCodes.value.length
        ? tripStopCodes.value
        : planner.multiRoute.value.ordered_stop_codes.filter(
            (code) => code !== planner.multiRoute.value?.resolved_start_code,
          );
      await runPlanMultiTargets(targets, value, activeStrategy.value);
    }
  } finally {
    tabLoading.value = "";
  }
};

const handleChangeStrategy = async (value: string) => {
  if (value === activeStrategy.value) return;
  activeStrategy.value = value;
  // Prefer the in-result alternatives; if matches, use that
  const altMatch = activeAlternatives.value.find((a) => a.strategy === value);
  if (altMatch) {
    planner.selectedAlternativeStrategy.value = value;
    return;
  }
  if (lastRouteShape.value === "single") {
    await runPlanSingle();
  } else if (lastRouteShape.value === "multi") {
    await runPlanTrip();
  }
};

const toggleCurrentLocation = async () => {
  useCurrentLocation.value = !useCurrentLocation.value;
  if (useCurrentLocation.value && !geo.currentLocation.value) {
    await geo.capture();
  }
  if (destinationCode.value) await runPlanSingle();
};

const openOriginPicker = () => {
  nav.startSetOrigin();
  toast.success("点击地图任意位置选择起点");
};

const handleMarkerClick = (data: { code: string; action: "origin" | "destination" }) => {
  if (data.action === "origin") {
    useCurrentLocation.value = false;
    originCode.value = data.code;
    if (destinationCode.value) runPlanSingle();
  } else {
    destinationCode.value = data.code;
    runPlanSingle();
  }
};

const handleFacilityClick = (data: { code: string; action: "destination" }) => {
  destinationCode.value = data.code;
  runPlanSingle();
};

const handleContextAction = (data: {
  action: "origin" | "destination";
  lat: number;
  lng: number;
}) => {
  // Find nearest node and treat like marker click
  const nearest = nav.findNearestNode(
    data.lat,
    data.lng,
    placeOptions.value.map((n) => ({
      code: n.code,
      name: n.name,
      latitude: n.latitude,
      longitude: n.longitude,
      route_node_type: (n as any).route_node_type,
    })),
  );
  if (!nearest) return;
  handleMarkerClick({ code: nearest.code, action: data.action });
};

const setFacilityFilter = (type: string) => {
  activeFacilityType.value = type;
};

// Multi-stop submit
const handleMultiSubmit = async (payload: {
  target_codes: string[];
  closed_loop: boolean;
  transport_mode: string;
  strategy: string;
}) => {
  await runPlanMultiTargets(payload.target_codes, payload.transport_mode, payload.strategy);
};

// Recommend / wander submit
const runPlanWander = async (duration: number, strategy: string) => {
  routeError.value = "";
  nav.resetNavigation();
  activeStrategy.value = strategy;
  await planner.planWander({
    ...buildBasePayload(),
    duration_minutes: duration,
    strategy,
  });
  if (planner.error.value) routeError.value = planner.error.value;
  else lastRouteShape.value = "wander";
};

const handleRecommendSubmit = async (payload: {
  duration_minutes: number;
  transport_mode: string;
  strategy: string;
}) => {
  if (!(await ensureLocationIfNeeded())) return;
  activeTransport.value = payload.transport_mode as TransportValue;
  await runPlanWander(payload.duration_minutes, payload.strategy);
  if (!planner.error.value) recommendOpen.value = false;
};

// Facility quick search (facility chip → "show me nearest")
const runPlanFacility = async (facilityType: string, radius: number) => {
  if (!(await ensureLocationIfNeeded())) return;
  routeError.value = "";
  nav.resetNavigation();
  await planner.planNearbyFacility({
    ...buildBasePayload(),
    facility_type: facilityType,
    radius,
    strategy: "time",
  });
  if (planner.error.value) routeError.value = planner.error.value;
  else lastRouteShape.value = "facility";
};

// Indoor handoff
const openIndoorHandoff = (destCode: string) => {
  // Find building matching destination
  const lastName = activeRoute.value?.path_names?.slice(-1)[0] ?? "";
  const match = indoorBuildingsForScene.value.find(
    (b) => b.building_code === destCode || b.building_name === lastName,
  );
  if (match) {
    indoorHandoffBuildingCode.value = match.building_code;
    indoorHandoffStartNode.value = match.nodes[0]?.code ?? "";
  }
  indoorDrawerOpen.value = true;
};

const handleCityChange = async (city: string) => {
  selectedCity.value = city;
  selectedSceneName.value = visibleScenes.value[0]?.name ?? "";
  await doSceneChange();
};

const handleSceneChange = async (sceneName: string) => {
  selectedSceneName.value = sceneName;
  await doSceneChange();
};

const doSceneChange = async () => {
  routeError.value = "";
  planner.reset();
  nav.resetNavigation();
  destinationCode.value = "";
  originCode.value = "";
  tripStopCodes.value = [];
  activeFacilityType.value = "";
  // Reset transport based on scene context
  activeTransport.value = availableTransports.value[0] ?? "walk";

  if (!supportsRouting.value) {
    loader.scene.value = { nodes: [] };
    loader.facilities.value = [];
    return;
  }

  await loader.loadScene(selectedSceneName.value);
};

onMounted(async () => {
  await loader.loadMeta();
  selectedSceneName.value = visibleScenes.value[0]?.name ?? "";
  await doSceneChange();
  // Try to capture location upfront
  if (useCurrentLocation.value && geo.supportsGeolocation) {
    geo.capture();
  }
});
</script>
