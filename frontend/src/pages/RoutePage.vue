<template>
  <div class="route-page space-y-6">
    <section class="card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">导航工作台</p>
          <h2 class="text-2xl font-bold text-slate-950 mt-1">地图导航</h2>
          <p class="text-sm text-slate-500 mt-2 leading-7 max-w-3xl">
            围绕当前城市和场景完成路线规划、设施查询与算法讲解，地图优先展示，操作区集中在下方和右侧。
          </p>
        </div>
        <button
          v-if="activeRoute"
          class="btn-soft-secondary text-sm inline-flex items-center gap-2"
          type="button"
          @click="handleSaveRoute"
        >
          收藏当前路线
        </button>
      </div>

      <div class="route-toolbar mt-5">
        <select v-model="selectedCity" class="soft-control text-sm" @change="handleCityChange">
          <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
        </select>
        <select v-model="selectedSceneName" class="soft-control text-sm" @change="handleSceneChange">
          <option v-for="scene in visibleScenes" :key="scene.name" :value="scene.name">
            {{ scene.label }}
          </option>
        </select>
        <label v-if="supportsRouting" class="route-toggle route-toggle-pro cursor-pointer">
          <input v-model="showGraphEvidence" type="checkbox" />
          <span>{{ showGraphEvidence ? "隐藏路网证据" : "显示路网证据" }}</span>
        </label>
      </div>

      <div class="grid lg:grid-cols-[minmax(0,1.35fr)_320px] gap-5 mt-5 items-start">
        <div class="route-map-stage">
          <div class="flex items-start justify-between gap-4 flex-wrap mb-4">
            <div>
              <h3 class="text-base font-bold text-slate-950">{{ currentSceneLabel }}</h3>
              <p class="text-sm text-slate-500 mt-1">{{ currentSceneMessage }}</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <span class="route-summary-chip">
                {{ supportsRouting ? "支持精细导航" : "当前仅支持地图浏览" }}
              </span>
              <span class="route-summary-chip route-summary-chip-accent">
                {{ activeRoute?.route_source_label || "本地算法" }}
              </span>
            </div>
          </div>
          <RouteMap
            :nodes="mapNodes"
            :path="displayPathCodes"
            :polyline="displayRoutePolyline"
            :show-graph-evidence="showGraphEvidence"
            :edges="loader.edges.value"
            :current-location="currentLocation"
          />
        </div>

        <aside class="space-y-4">
          <article class="route-insight-card">
            <span class="route-panel-kicker">当前场景</span>
            <h3>{{ currentSceneLabel }}</h3>
            <p>{{ currentSceneMessage }}</p>
          </article>
          <article class="route-insight-card">
            <span class="route-panel-kicker">导航状态</span>
            <h3>{{ activeNavigationSummary || "等待规划" }}</h3>
            <p>
              {{
                activeRoute
                  ? resultSubtitle
                  : "先选择一种规划模式，再生成路线。地图会始终保留为首屏工作区域。"
              }}
            </p>
          </article>
          <article class="route-insight-card" v-if="activeRoute">
            <span class="route-panel-kicker">关键指标</span>
            <div class="grid grid-cols-2 gap-3 mt-3">
              <div class="route-metric-tile">
                <strong>{{ activeRoute.total_distance_m }}</strong>
                <span>总距离 / 米</span>
              </div>
              <div class="route-metric-tile">
                <strong>{{ activeRoute.estimated_minutes }}</strong>
                <span>预计时间 / 分钟</span>
              </div>
              <div class="route-metric-tile">
                <strong>{{ activeRoute.algorithm_path_codes?.length ?? activeRoute.path_codes.length }}</strong>
                <span>算法路径点数</span>
              </div>
              <div class="route-metric-tile">
                <strong>{{ loader.edges.value.length }}</strong>
                <span>路网边数</span>
              </div>
            </div>
          </article>
        </aside>
      </div>
    </section>

    <div v-if="routeError" class="alert-soft-error">{{ routeError }}</div>

    <template v-if="supportsRouting">
      <section class="grid xl:grid-cols-[minmax(0,1.08fr)_360px] gap-5 items-start">
        <div class="space-y-5">
          <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4" aria-label="路线规划模式">
            <button
              v-for="item in modeOptions"
              :key="item.key"
              type="button"
              class="route-mode-card"
              :class="{ 'route-mode-card-active': routeMode === item.key }"
              @click="selectMode(item.key)"
            >
              <span class="route-mode-card-tag">{{ item.label }}</span>
              <strong>{{ item.title }}</strong>
              <small>{{ item.caption }}</small>
            </button>
          </div>

          <section v-if="routeMode" class="card-elevated rounded-[24px] p-5 lg:p-6 space-y-4">
            <div class="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <span class="route-panel-kicker">规划设置</span>
                <h3 class="text-lg font-bold text-slate-950 mt-1">{{ activeModeTitle }}</h3>
              </div>
              <span class="route-summary-chip">{{ activeTransportLabel }}</span>
            </div>

            <LocationCapture ref="locationCaptureRef" v-model="useCurrentLocation" />

            <form class="grid grid-cols-1 md:grid-cols-2 gap-4" @submit.prevent="handleGenerateRoute">
              <label class="space-y-1">
                <span class="field-label">当前位置</span>
                <select
                  v-model="startCode"
                  class="soft-control text-sm"
                  :disabled="useCurrentLocation"
                >
                  <option v-for="node in placeOptions" :key="node.code" :value="node.code">
                    {{ node.name }}
                  </option>
                </select>
              </label>

              <label v-if="routeMode === 'destination'" class="space-y-1">
                <span class="field-label">目的地</span>
                <select v-model="endCode" class="soft-control text-sm">
                  <option v-for="node in placeOptions" :key="node.code" :value="node.code">
                    {{ node.name }}
                  </option>
                </select>
              </label>

              <label v-if="routeMode === 'multi'" class="space-y-1 md:col-span-2">
                <span class="field-label">途经地点</span>
                <select
                  v-model="multiTargetCodes"
                  class="soft-control text-sm min-h-32"
                  multiple
                  size="5"
                >
                  <option v-for="node in placeOptions" :key="node.code" :value="node.code">
                    {{ node.name }}
                  </option>
                </select>
              </label>

              <label v-if="routeMode === 'facility'" class="space-y-1">
                <span class="field-label">设施类型</span>
                <select v-model="facilityType" class="soft-control text-sm">
                  <option
                    v-for="facility in facilityTypeOptions"
                    :key="facility.value"
                    :value="facility.value"
                  >
                    {{ facility.label }}
                  </option>
                </select>
              </label>

              <label class="space-y-1">
                <span class="field-label">交通方式</span>
                <select v-model="transportMode" class="soft-control text-sm">
                  <option v-for="item in transportOptions" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </option>
                </select>
              </label>

              <label v-if="routeMode === 'destination' || routeMode === 'multi'" class="space-y-1">
                <span class="field-label">路线策略</span>
                <select v-model="strategy" class="soft-control text-sm">
                  <option v-for="item in strategyOptions" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </option>
                </select>
              </label>

              <label v-if="routeMode === 'wander'" class="space-y-1">
                <span class="field-label">可用时长</span>
                <select v-model.number="durationMinutes" class="soft-control text-sm">
                  <option :value="25">25 分钟</option>
                  <option :value="35">35 分钟</option>
                  <option :value="50">50 分钟</option>
                  <option :value="75">75 分钟</option>
                </select>
              </label>

              <label v-if="routeMode === 'facility'" class="space-y-1">
                <span class="field-label">查找半径</span>
                <select v-model.number="radius" class="soft-control text-sm">
                  <option :value="600">600 米</option>
                  <option :value="1000">1000 米</option>
                  <option :value="1500">1500 米</option>
                  <option :value="2500">2500 米</option>
                </select>
              </label>

              <button class="btn-soft-primary w-full md:col-span-2" type="submit" :disabled="isPlanning">
                {{ isPlanning ? "正在生成路线..." : submitLabel }}
              </button>
            </form>
          </section>

          <section v-if="activeAlternatives.length" class="card-elevated rounded-[24px] p-5 space-y-4">
            <div class="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <span class="route-panel-kicker">备选路线</span>
                <h3 class="text-lg font-bold text-slate-950 mt-1">切换不同策略结果</h3>
              </div>
              <span class="text-xs text-slate-400">点击卡片即可高亮地图中的路线</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
              <article
                v-for="item in activeAlternatives"
                :key="item.strategy"
                class="route-alt-card"
                :class="{
                  'route-alt-card-active':
                    planner.selectedAlternativeStrategy.value === item.strategy,
                }"
                @click="planner.selectedAlternativeStrategy.value = item.strategy"
              >
                <h4>{{ item.strategy_label }}</h4>
                <p>{{ item.total_distance_m }} 米 · {{ item.estimated_minutes }} 分钟</p>
              </article>
            </div>
          </section>

          <section v-if="activeSegments.length" class="card-elevated rounded-[24px] p-5 space-y-4">
            <div class="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <span class="route-panel-kicker">分段导航</span>
                <h3 class="text-lg font-bold text-slate-950 mt-1">按顺序执行即可完成整段行程</h3>
              </div>
            </div>
            <ol class="timeline-list">
              <li
                v-for="segment in activeSegments"
                :key="`segment-${segment.index}-${segment.from_code}-${segment.to_code}`"
                class="timeline-item !bg-slate-50"
              >
                <span class="timeline-index">{{ segment.index }}</span>
                <div class="timeline-content">
                  <strong class="text-sm font-bold text-slate-900">
                    {{ segment.from_name }} → {{ segment.to_name }}
                  </strong>
                  <p class="text-xs text-slate-500 mt-0.5">{{ segment.instruction }}</p>
                  <p class="text-xs text-slate-400 mt-0.5">
                    {{ segment.distance_m }} 米 · {{ segment.estimated_minutes }} 分钟 · 累计
                    {{ segment.cumulative_distance_m }} 米
                  </p>
                </div>
              </li>
            </ol>
          </section>
        </div>

        <aside class="space-y-5">
          <section
            v-if="activeRoute"
            class="card-elevated rounded-[24px] p-5 sticky top-18 space-y-4 route-result-card"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <span class="route-panel-kicker">{{ resultKicker }}</span>
                <h3 class="text-xl font-bold text-slate-950 mt-1">{{ resultTitle }}</h3>
              </div>
              <span class="route-summary-chip route-summary-chip-accent">
                {{ activeRoute.route_source_label || "本地算法" }}
              </span>
            </div>

            <p class="text-sm text-slate-600 leading-7">{{ activeRoute.explanation }}</p>

            <div class="flex flex-wrap gap-2">
              <span class="route-summary-chip">{{ activeRoute.total_distance_m }} 米</span>
              <span class="route-summary-chip">{{ activeRoute.estimated_minutes }} 分钟</span>
              <span class="route-summary-chip">{{ activeRoute.transport_mode_label }}</span>
              <span class="route-summary-chip">
                算法路径 {{ activeRoute.algorithm_path_codes?.length ?? activeRoute.path_codes.length }} 点
              </span>
              <span class="route-summary-chip">路网边 {{ loader.edges.value.length }} 条</span>
            </div>

            <div class="space-y-2 text-sm text-slate-500">
              <p v-if="activeRoute.resolved_start_name">
                实际起点：{{ activeRoute.resolved_start_name }}
              </p>
              <p v-if="planner.facilityRoute.value?.facility">
                最近设施：{{ planner.facilityRoute.value.facility.name }} ·
                {{ planner.facilityRoute.value.facility.facility_label }}
              </p>
              <p v-if="planner.wanderRoute.value?.ordered_stop_names?.length">
                停靠：{{ planner.wanderRoute.value.ordered_stop_names.join(" → ") }}
              </p>
              <p
                v-if="planner.multiRoute.value?.ordered_stop_names?.length && routeMode === 'multi'"
              >
                停靠：{{ planner.multiRoute.value.ordered_stop_names.join(" → ") }}
              </p>
            </div>
          </section>

          <section v-else class="card-elevated rounded-[24px] p-5 space-y-3">
            <span class="route-panel-kicker">结果面板</span>
            <h3 class="text-lg font-bold text-slate-950">等待生成路线</h3>
            <p class="text-sm text-slate-500 leading-7">
              先选择一种模式并填写起点、终点或设施条件，系统会在同一张地图上给出结果。
            </p>
          </section>

          <IndoorRoutePanel
            v-if="currentIndoorBuildings.length"
            :buildings="currentIndoorBuildings"
            @route-error="routeError = $event"
          />
        </aside>
      </section>
    </template>

    <div v-else class="alert-soft-info">
      {{ selectedCity }} 当前支持城市地图浏览与精选地点查看，精细导航暂未覆盖到该场景。
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import RouteMap from "../components/RouteMap.vue";
import LocationCapture from "../components/route/LocationCapture.vue";
import IndoorRoutePanel from "../components/route/IndoorRoutePanel.vue";
import { useRoutePlanner } from "../composables/useRoutePlanner";
import { useSceneLoader } from "../composables/useSceneLoader";
import { useAuthStore } from "../stores/auth";
import type {
  IndoorBuilding,
  MultiRouteResult,
  RouteSegment,
  SingleRouteResult,
} from "../types/models";

type RouteMode = "" | "wander" | "destination" | "multi" | "facility";
type RouteModeOption = {
  key: Exclude<RouteMode, "">;
  label: string;
  title: string;
  caption: string;
};

const auth = useAuthStore();
const loader = useSceneLoader();
const planner = useRoutePlanner();

const locationCaptureRef = ref<InstanceType<typeof LocationCapture> | null>(null);
const cities = ["北京", "上海", "广州", "深圳"];
const selectedCity = ref("北京");
const selectedSceneName = ref("BUPT_Main_Campus");
const routeMode = ref<RouteMode>("");
const startCode = ref("");
const endCode = ref("");
const multiTargetCodes = ref<string[]>([]);
const transportMode = ref("walk");
const strategy = ref("time");
const durationMinutes = ref(35);
const facilityType = ref("restroom");
const radius = ref(1500);
const useCurrentLocation = ref(false);
const routeError = ref("");
const showGraphEvidence = ref(false);

const modeOptions: RouteModeOption[] = [
  {
    key: "wander",
    label: "随便逛逛",
    title: "自动安排一圈",
    caption: "按照可用时长挑选附近点位，并回到起点。",
  },
  {
    key: "destination",
    label: "去指定地点",
    title: "生成到达路线",
    caption: "输入起点和目的地，生成适合当前策略的路线。",
  },
  {
    key: "multi",
    label: "多点游览",
    title: "规划闭环路线",
    caption: "选择多个点位后自动排序，并回到起点。",
  },
  {
    key: "facility",
    label: "找最近设施",
    title: "设施到达查询",
    caption: "按图距离查找最近的厕所、餐厅和服务点。",
  },
];

const transportOptions = [
  { value: "walk", label: "步行" },
  { value: "bike", label: "骑行" },
  { value: "shuttle", label: "电瓶车" },
  { value: "taxi", label: "打车" },
  { value: "mixed", label: "混合" },
];

const strategyOptions = [
  { value: "distance", label: "最短距离" },
  { value: "time", label: "最快到达" },
  { value: "congestion", label: "避开拥堵" },
  { value: "scenic", label: "打卡优先" },
];

const facilityTypeOptions = [
  { value: "restroom", label: "公共厕所" },
  { value: "restaurant", label: "餐厅" },
  { value: "supermarket", label: "超市" },
  { value: "service", label: "服务点" },
  { value: "shop", label: "商店" },
  { value: "sports", label: "运动场馆" },
];

const visibleScenes = computed(() =>
  loader.scenes.value.filter((item) => item.city === selectedCity.value),
);

const currentScene = computed(() =>
  visibleScenes.value.find((item) => item.name === selectedSceneName.value),
);

const currentSceneLabel = computed(() => currentScene.value?.label ?? "当前场景");
const supportsRouting = computed(() => currentScene.value?.supports_routing ?? false);

const currentIndoorBuildings = computed<IndoorBuilding[]>(() =>
  loader.indoorBuildings.value.filter((item) => item.scene_name === selectedSceneName.value),
);

const placeOptions = computed(() => [
  ...(loader.scene.value?.nodes ?? []),
  ...loader.facilities.value,
]);

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

const currentSceneMessage = computed(() =>
  supportsRouting.value
    ? `当前共有 ${mapNodes.value.length} 个可规划点位。`
    : `当前共有 ${mapNodes.value.length} 个精选地点可浏览。`,
);

const currentLocation = computed(() => locationCaptureRef.value?.currentLocation ?? null);
const activeSegments = computed<RouteSegment[]>(() => activeRoute.value?.segments ?? []);
const displayPathCodes = computed<string[]>(() => activeRoute.value?.path_codes ?? []);
const displayRoutePolyline = computed(
  () => activeRoute.value?.route_polyline ?? activeRoute.value?.route_geometry ?? [],
);
const activeNavigationSummary = computed(() => activeRoute.value?.navigation_summary ?? "");
const activeAlternatives = computed<SingleRouteResult[]>(
  () => planner.singleRoute.value?.alternatives ?? [],
);

const activeModeTitle = computed(() => {
  if (routeMode.value === "wander") return "随便逛逛";
  if (routeMode.value === "destination") return "去指定地点";
  if (routeMode.value === "multi") return "多点游览";
  if (routeMode.value === "facility") return "找最近设施";
  return "";
});

const activeTransportLabel = computed(
  () => transportOptions.find((item) => item.value === transportMode.value)?.label ?? "步行",
);

const submitLabel = computed(() => {
  if (routeMode.value === "wander") return "生成漫游路线";
  if (routeMode.value === "multi") return "生成多点闭环";
  if (routeMode.value === "facility") return "查找最近设施";
  return "生成到达路线";
});

const isPlanning = computed(
  () =>
    planner.singleLoading.value ||
    planner.multiLoading.value ||
    planner.wanderLoading.value ||
    planner.facilityLoading.value,
);

const resultKicker = computed(() => {
  if (planner.wanderRoute.value) return "随便逛逛";
  if (planner.multiRoute.value) return "多点游览";
  if (planner.facilityRoute.value) return "最近设施";
  return "到达路线";
});

const resultTitle = computed(() => {
  if (planner.wanderRoute.value) return planner.wanderRoute.value.optimization_label;
  if (planner.multiRoute.value) return planner.multiRoute.value.optimization_label;
  if (planner.facilityRoute.value?.facility) return planner.facilityRoute.value.facility.name;
  return activeRoute.value?.strategy_label ?? "路线结果";
});

const resultSubtitle = computed(() => {
  if (planner.wanderRoute.value) return "系统已经为当前场景生成一条闭环漫游路线。";
  if (planner.multiRoute.value) return "系统已经为当前点位生成多点闭环路线。";
  if (planner.facilityRoute.value) return "系统已经按图距离查找到最近设施。";
  return "系统已经生成指定地点的到达路线。";
});

const syncDefaults = () => {
  const options = placeOptions.value;
  if (!options.length) {
    startCode.value = "";
    endCode.value = "";
    return;
  }

  if (!options.some((item) => item.code === startCode.value)) {
    startCode.value = options[0].code;
  }

  if (!options.some((item) => item.code === endCode.value)) {
    endCode.value = options.find((item) => item.code !== startCode.value)?.code ?? startCode.value;
  }

  multiTargetCodes.value = multiTargetCodes.value.filter((code) =>
    options.some((item) => item.code === code),
  );

  if (!multiTargetCodes.value.length) {
    multiTargetCodes.value = options
      .filter((item) => item.code !== startCode.value)
      .slice(0, 3)
      .map((item) => item.code);
  }
};

watch(placeOptions, syncDefaults, { immediate: true });

const selectMode = (mode: Exclude<RouteMode, "">) => {
  routeMode.value = mode;
  routeError.value = "";
  planner.reset();

  if (mode === "wander") {
    strategy.value = "scenic";
    transportMode.value = "walk";
  } else if (mode === "destination") {
    strategy.value = "time";
  } else if (mode === "multi") {
    strategy.value = "scenic";
    syncDefaults();
  } else if (mode === "facility") {
    strategy.value = "time";
    facilityType.value = "restroom";
  }
};

const getLocationPayload = () =>
  locationCaptureRef.value?.locationPayload() ?? {
    prefer_nearest_start: false,
    start_latitude: null,
    start_longitude: null,
  };

const ensureLocationReady = async (): Promise<boolean> =>
  locationCaptureRef.value?.ensureReady() ?? true;

const baseRoutePayload = () => ({
  scene_name: selectedSceneName.value,
  start_code: startCode.value,
  transport_mode: transportMode.value,
  ...getLocationPayload(),
});

const handleGenerateRoute = async () => {
  routeError.value = "";
  const ready = await ensureLocationReady();

  if (!ready) {
    routeError.value = "无法获取当前位置，请改为手动选择起点，或重新尝试定位。";
    return;
  }

  if (routeMode.value === "wander") {
    await planner.planWander({
      ...baseRoutePayload(),
      duration_minutes: durationMinutes.value,
    });
  } else if (routeMode.value === "facility") {
    await planner.planNearbyFacility({
      ...baseRoutePayload(),
      facility_type: facilityType.value,
      radius: radius.value,
      strategy: "time",
    });
  } else if (routeMode.value === "destination") {
    await planner.planSingle({
      ...baseRoutePayload(),
      end_code: endCode.value,
      strategy: strategy.value,
    });
  } else if (routeMode.value === "multi") {
    await planner.planMulti({
      ...baseRoutePayload(),
      target_codes: multiTargetCodes.value,
      strategy: strategy.value,
    });
  }

  if (planner.error.value) {
    routeError.value = planner.error.value;
  }
};

const handleCityChange = async () => {
  selectedSceneName.value = visibleScenes.value[0]?.name ?? "";
  await handleSceneChange();
};

const handleSceneChange = async () => {
  routeError.value = "";
  planner.reset();

  if (!supportsRouting.value) {
    loader.scene.value = { nodes: [] };
    loader.facilities.value = [];
    loader.edges.value = [];
    return;
  }

  await loader.loadScene(selectedSceneName.value);
  syncDefaults();
};

const handleSaveRoute = async () => {
  const route = activeRoute.value;
  if (!route) return;

  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }

  await auth.saveRouteFavorite({
    scene_name: selectedSceneName.value,
    strategy: route.strategy,
    transport_mode: route.transport_mode,
    path_codes: route.path_codes,
    path_names: route.path_names,
    total_distance_m: route.total_distance_m,
    estimated_minutes: route.estimated_minutes,
    explanation: route.explanation,
  });
};

onMounted(async () => {
  await loader.loadMeta();
  selectedSceneName.value = visibleScenes.value[0]?.name ?? "";
  await handleSceneChange();
});
</script>
