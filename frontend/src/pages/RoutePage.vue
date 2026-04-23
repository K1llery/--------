<template>
  <section class="panel-card route-page">
    <div class="section-top">
      <div>
        <h2>地图导航</h2>
        <p>按真实出行流程规划：先确定风格，再选起终点，最后查看分段导航与备选线路。</p>
      </div>
    </div>

    <!-- 出行风格 + 出发方式 -->
    <section class="route-experience">
      <TravelProfileSelector v-model="activeProfileKey" @profile-applied="onProfileApplied" />
      <LocationCapture ref="locationCaptureRef" v-model="useCurrentLocation" />
    </section>

    <!-- 城市 / 场景 / 策略 / 交通 过滤栏 -->
    <div class="filter-bar">
      <select v-model="selectedCity" class="select-input" @change="handleCityChange">
        <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
      </select>
      <select v-model="selectedSceneName" class="select-input" @change="handleSceneChange">
        <option v-for="scene in visibleScenes" :key="scene.name" :value="scene.name">
          {{ scene.label }}
        </option>
      </select>
      <select v-model="strategy" class="select-input">
        <option value="distance">最短距离</option>
        <option value="time">最快到达</option>
        <option value="congestion">避开拥堵</option>
        <option value="scenic">轻松逛/打卡优先</option>
      </select>
      <select v-model="transportMode" class="select-input">
        <option value="walk">步行</option>
        <option value="bike">骑行</option>
        <option value="shuttle">摆渡车</option>
        <option value="mixed">综合方式</option>
      </select>
    </div>

    <!-- 地图 -->
    <RouteMap :nodes="mapNodes" :path="displayPathCodes" :current-location="currentLocation" />

    <!-- 信息卡片 -->
    <RouteInfoCards
      :selected-city="selectedCity"
      :current-scene-message="currentSceneMessage"
      :suggested-nodes="suggestedNodes"
      :navigation-summary="activeNavigationSummary"
    />

    <!-- 错误提示 -->
    <div v-if="routeError" class="status-card error-card">{{ routeError }}</div>

    <!-- 支持路由的场景：室外 + 室内面板 -->
    <template v-if="supportsRouting">
      <OutdoorRoutePanel
        ref="outdoorPanelRef"
        :scene-name="selectedSceneName"
        :place-options="placeOptions"
        :strategy="strategy"
        :transport-mode="transportMode"
        :disable-start-select="useCurrentLocation"
        :location-payload-fn="getLocationPayload"
        :ensure-location-ready-fn="ensureLocationReady"
        @route-error="routeError = $event"
        @save-route="handleSaveRoute"
      />

      <IndoorRoutePanel
        ref="indoorPanelRef"
        :buildings="indoorBuildingsForScene"
        @route-error="routeError = $event"
      />
    </template>

    <div v-else class="status-card">
      {{ selectedCity }}当前支持城市地图浏览与精选地点查看，精细导航即将上线。
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import RouteMap from "../components/RouteMap.vue";
import IndoorRoutePanel from "../components/route/IndoorRoutePanel.vue";
import LocationCapture from "../components/route/LocationCapture.vue";
import OutdoorRoutePanel from "../components/route/OutdoorRoutePanel.vue";
import RouteInfoCards from "../components/route/RouteInfoCards.vue";
import TravelProfileSelector from "../components/route/TravelProfileSelector.vue";
import { useSceneLoader } from "../composables/useSceneLoader";
import { useAuthStore } from "../stores/auth";

// ─── Stores & Composables ───────────────────────────────────────────
const auth = useAuthStore();
const loader = useSceneLoader();

// ─── 模板引用 ───────────────────────────────────────────────────────
const locationCaptureRef = ref<InstanceType<typeof LocationCapture> | null>(null);
const outdoorPanelRef = ref<InstanceType<typeof OutdoorRoutePanel> | null>(null);
const indoorPanelRef = ref<InstanceType<typeof IndoorRoutePanel> | null>(null);

// ─── 页面级状态 ─────────────────────────────────────────────────────
const cities = ["北京", "上海", "广州", "深圳"];
const selectedCity = ref("北京");
const selectedSceneName = ref("BUPT_Main_Campus");
const strategy = ref("distance");
const transportMode = ref("walk");
const activeProfileKey = ref("balanced");
const useCurrentLocation = ref(false);
const routeError = ref("");

// ─── 派生状态 ────────────────────────────────────────────────────────
const visibleScenes = computed(() =>
  loader.scenes.value.filter((item) => item.city === selectedCity.value),
);

const supportsRouting = computed(
  () =>
    visibleScenes.value.find((item) => item.name === selectedSceneName.value)?.supports_routing ??
    false,
);

const placeOptions = computed(() => [
  ...(loader.scene.value?.nodes ?? []),
  ...loader.facilities.value,
]);

const indoorBuildingsForScene = computed(() =>
  loader.indoorBuildings.value.filter((item) => item.scene_name === selectedSceneName.value),
);

const mapNodes = computed(() => {
  if (supportsRouting.value) return placeOptions.value;
  return loader.featuredDestinations.value
    .filter((item) => item.city === selectedCity.value)
    .map((item) => ({
      code: item.source_id,
      name: item.name,
      latitude: item.latitude,
      longitude: item.longitude,
    }));
});

const currentSceneMessage = computed(() =>
  supportsRouting.value
    ? `${mapNodes.value.length} 个点位可用于精细规划。`
    : `${mapNodes.value.length} 个精选地点可用于城市浏览。`,
);

const suggestedNodes = computed(() => placeOptions.value.slice(0, 4));

const currentLocation = computed(() => locationCaptureRef.value?.currentLocation ?? null);

const displayPathCodes = computed<string[]>(() => outdoorPanelRef.value?.displayPathCodes ?? []);

const activeNavigationSummary = computed<string>(
  () => outdoorPanelRef.value?.activeNavigationSummary ?? "",
);

// ─── 事件处理 ────────────────────────────────────────────────────────
const onProfileApplied = (profile: { strategy: string; transportMode: string }) => {
  strategy.value = profile.strategy;
  transportMode.value = profile.transportMode;
};

const getLocationPayload = () => {
  return (
    locationCaptureRef.value?.locationPayload() ?? {
      prefer_nearest_start: false,
      start_latitude: null,
      start_longitude: null,
    }
  );
};

const ensureLocationReady = async (): Promise<boolean> => {
  return locationCaptureRef.value?.ensureReady() ?? true;
};

const handleCityChange = async () => {
  routeError.value = "";
  selectedSceneName.value = visibleScenes.value[0]?.name ?? "";
  await handleSceneChange();
};

const handleSceneChange = async () => {
  routeError.value = "";
  outdoorPanelRef.value?.reset();
  indoorPanelRef.value?.reset();

  if (!supportsRouting.value) {
    loader.scene.value = { nodes: [] };
    loader.facilities.value = [];
    return;
  }

  await loader.loadScene(selectedSceneName.value);
};

const handleSaveRoute = async (payload: Record<string, unknown>) => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  await auth.saveRouteFavorite(payload);
};

// ─── 初始化 ──────────────────────────────────────────────────────────
onMounted(async () => {
  await loader.loadMeta();
  selectedSceneName.value = visibleScenes.value[0]?.name ?? "";
  await handleSceneChange();
});
</script>
