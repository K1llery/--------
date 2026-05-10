<template>
  <div class="bg-white rounded-3xl card-elevated p-6 space-y-5">
    <!-- 页面标题 -->
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <h2 class="text-xl font-bold text-gray-900">地图导航</h2>
        <p class="text-sm text-gray-500 mt-1">你想怎么做？</p>
      </div>
      <button
        v-if="activeRoute"
        class="btn-soft-secondary text-sm"
        type="button"
        @click="handleSaveRoute"
      >
        收藏路线
      </button>
    </div>

    <!-- 城市/场景筛选 -->
    <div class="flex flex-wrap gap-3 p-4 bg-gray-50 rounded-2xl">
      <select v-model="selectedCity" class="soft-control text-sm" @change="handleCityChange">
        <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
      </select>
      <select v-model="selectedSceneName" class="soft-control text-sm" @change="handleSceneChange">
        <option v-for="scene in visibleScenes" :key="scene.name" :value="scene.name">
          {{ scene.label }}
        </option>
      </select>
    </div>

    <!-- 地图 -->
    <RouteMap :nodes="mapNodes" :path="displayPathCodes" :current-location="currentLocation" />

    <!-- 状态卡片 -->
    <div class="grid grid-cols-2 gap-4">
      <div class="card-elevated p-4">
        <h3 class="text-sm font-bold text-gray-900">{{ currentSceneLabel }}</h3>
        <p class="text-xs text-gray-500 mt-1">{{ currentSceneMessage }}</p>
      </div>
      <div class="card-elevated p-4">
        <h3 class="text-sm font-bold text-gray-900">{{ activeNavigationSummary || "等待规划" }}</h3>
        <p class="text-xs text-gray-500 mt-1">
          {{ activeRoute ? resultSubtitle : "选择一个行动方式后开始生成路线。" }}
        </p>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="routeError" class="alert-soft-error">{{ routeError }}</div>

    <template v-if="supportsRouting">
      <!-- 模式选择：随便逛逛 / 去指定地点 / 找最近设施 -->
      <div class="grid grid-cols-3 gap-4" aria-label="路线规划模式">
        <button
          v-for="item in modeOptions"
          :key="item.key"
          type="button"
          class="card-elevated p-4 text-left glow-border cursor-pointer"
          :class="{ 'ring-2 ring-primary-300': routeMode === item.key }"
          @click="selectMode(item.key)"
        >
          <span
            class="inline-block px-2 py-0.5 rounded-full text-xs font-bold text-teal-700 bg-teal-50 mb-2"
            >{{ item.label }}</span
          >
          <strong class="block text-base font-bold text-gray-900">{{ item.title }}</strong>
          <small class="text-xs text-gray-500 mt-1 block line-clamp-2">{{ item.caption }}</small>
        </button>
      </div>

      <!-- 规划器：表单 + 结果 -->
      <section v-if="routeMode" class="grid lg:grid-cols-[1.1fr_0.9fr] gap-4 items-start">
        <!-- 左侧：表单 -->
        <div class="card-elevated p-5 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-base font-bold text-gray-900">{{ activeModeTitle }}</h3>
            <span class="text-xs text-gray-400">{{ activeTransportLabel }}</span>
          </div>

          <LocationCapture ref="locationCaptureRef" v-model="useCurrentLocation" />

          <form class="grid grid-cols-2 gap-3" @submit.prevent="handleGenerateRoute">
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

            <label v-if="routeMode === 'destination'" class="space-y-1">
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

            <button class="btn-soft-primary w-full col-span-2" type="submit" :disabled="isPlanning">
              {{ isPlanning ? "生成中..." : submitLabel }}
            </button>
          </form>
        </div>

        <!-- 右侧：结果 -->
        <aside v-if="activeRoute" class="card-elevated sticky top-4 p-5 space-y-3">
          <span
            class="inline-block px-2 py-0.5 rounded-full text-xs font-extrabold text-amber-700 bg-amber-50"
            >{{ resultKicker }}</span
          >
          <h3 class="text-lg font-bold text-gray-900">{{ resultTitle }}</h3>
          <p class="text-sm text-gray-500">{{ activeRoute.explanation }}</p>
          <div class="flex flex-wrap gap-2">
            <span class="stat-pill">{{ activeRoute.total_distance_m }} m</span>
            <span class="stat-pill">{{ activeRoute.estimated_minutes }} 分钟</span>
            <span class="stat-pill">{{ activeRoute.transport_mode_label }}</span>
          </div>
          <p v-if="activeRoute.resolved_start_name" class="text-xs text-gray-400">
            实际起点：{{ activeRoute.resolved_start_name }}
          </p>
          <p v-if="planner.facilityRoute.value?.facility" class="text-xs text-gray-400">
            最近设施：{{ planner.facilityRoute.value.facility.name }} ·
            {{ planner.facilityRoute.value.facility.facility_label }}
          </p>
          <p
            v-if="planner.wanderRoute.value?.ordered_stop_names?.length"
            class="text-xs text-gray-400"
          >
            停靠：{{ planner.wanderRoute.value.ordered_stop_names.join(" → ") }}
          </p>
        </aside>
      </section>

      <!-- 备选路线 -->
      <section v-if="activeAlternatives.length" class="space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-gray-900">备选路线</h3>
          <span class="text-xs text-gray-400">点击卡片切换地图高亮</span>
        </div>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <article
            v-for="item in activeAlternatives"
            :key="item.strategy"
            class="card-elevated p-4 cursor-pointer glow-border"
            :class="{
              'ring-2 ring-primary-300':
                planner.selectedAlternativeStrategy.value === item.strategy,
            }"
            @click="planner.selectedAlternativeStrategy.value = item.strategy"
          >
            <h4 class="text-sm font-bold text-gray-900">{{ item.strategy_label }}</h4>
            <p class="text-xs text-gray-500 mt-1">
              {{ item.total_distance_m }} m · {{ item.estimated_minutes }} 分钟
            </p>
          </article>
        </div>
      </section>

      <!-- 分段导航 -->
      <section v-if="activeSegments.length" class="space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-gray-900">分段导航</h3>
          <span class="text-xs text-gray-400">按顺序执行即可完成整段行程</span>
        </div>
        <ol class="timeline-list">
          <li
            v-for="segment in activeSegments"
            :key="`segment-${segment.index}-${segment.from_code}-${segment.to_code}`"
            class="timeline-item !bg-gray-50"
          >
            <span class="timeline-index">{{ segment.index }}</span>
            <div class="timeline-content">
              <strong class="text-sm font-bold text-gray-900"
                >{{ segment.from_name }} → {{ segment.to_name }}</strong
              >
              <p class="text-xs text-gray-500 mt-0.5">{{ segment.instruction }}</p>
              <p class="text-xs text-gray-400 mt-0.5">
                {{ segment.distance_m }} 米 · {{ segment.estimated_minutes }} 分钟 · 累计
                {{ segment.cumulative_distance_m }} 米
              </p>
            </div>
          </li>
        </ol>
      </section>
    </template>

    <div v-else class="alert-soft-info">
      {{ selectedCity }}当前支持城市地图浏览与精选地点查看，精细导航即将上线。
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import RouteMap from "../components/RouteMap.vue";
import LocationCapture from "../components/route/LocationCapture.vue";
import { useRoutePlanner } from "../composables/useRoutePlanner";
import { useSceneLoader } from "../composables/useSceneLoader";
import { useAuthStore } from "../stores/auth";
import type { MultiRouteResult, RouteSegment, SingleRouteResult } from "../types/models";

type RouteMode = "" | "wander" | "destination" | "facility";
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
const transportMode = ref("walk");
const strategy = ref("time");
const durationMinutes = ref(35);
const facilityType = ref("restroom");
const radius = ref(1500);
const useCurrentLocation = ref(false);
const routeError = ref("");

const modeOptions: RouteModeOption[] = [
  {
    key: "wander",
    label: "随便逛逛",
    title: "自动安排一圈",
    caption: "按时长挑选附近点位并回到起点",
  },
  {
    key: "destination",
    label: "去指定地点",
    title: "查到达方法",
    caption: "输入起点和目的地生成最短路径",
  },
  {
    key: "facility",
    label: "找最近设施",
    title: "厕所/餐厅/服务点",
    caption: "按道路距离找最近可达设施",
  },
];

const transportOptions = [
  { value: "walk", label: "步行" },
  { value: "bike", label: "骑行" },
  { value: "taxi", label: "打车" },
];

const strategyOptions = [
  { value: "distance", label: "最短距离" },
  { value: "time", label: "最快到达" },
  { value: "congestion", label: "避开拥堵" },
  { value: "scenic", label: "轻松逛/打卡优先" },
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

const placeOptions = computed(() => [
  ...(loader.scene.value?.nodes ?? []),
  ...loader.facilities.value,
]);

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
    ? `${mapNodes.value.length} 个点位可规划。`
    : `${mapNodes.value.length} 个精选地点可浏览。`,
);

const currentLocation = computed(() => locationCaptureRef.value?.currentLocation ?? null);

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
  return planner.facilityRoute.value || planner.wanderRoute.value || planner.singleRoute.value;
});

const activeSegments = computed<RouteSegment[]>(() => activeRoute.value?.segments ?? []);

const displayPathCodes = computed<string[]>(() => activeRoute.value?.path_codes ?? []);

const activeNavigationSummary = computed(() => activeRoute.value?.navigation_summary ?? "");

const activeAlternatives = computed<SingleRouteResult[]>(
  () => planner.singleRoute.value?.alternatives ?? [],
);

const activeModeTitle = computed(() => {
  if (routeMode.value === "wander") return "随便逛逛";
  if (routeMode.value === "destination") return "去指定地点";
  if (routeMode.value === "facility") return "找最近设施";
  return "";
});

const activeTransportLabel = computed(
  () => transportOptions.find((item) => item.value === transportMode.value)?.label ?? "步行",
);

const submitLabel = computed(() => {
  if (routeMode.value === "wander") return "生成漫游路线";
  if (routeMode.value === "facility") return "查找最近设施";
  return "生成到达路线";
});

const isPlanning = computed(
  () => planner.singleLoading.value || planner.wanderLoading.value || planner.facilityLoading.value,
);

const resultKicker = computed(() => {
  if (planner.wanderRoute.value) return "Wander Route";
  if (planner.facilityRoute.value) return "Nearest Facility";
  return "Destination Route";
});

const resultTitle = computed(() => {
  if (planner.wanderRoute.value) return planner.wanderRoute.value.optimization_label;
  if (planner.facilityRoute.value?.facility) return planner.facilityRoute.value.facility.name;
  return activeRoute.value?.strategy_label ?? "路线结果";
});

const resultSubtitle = computed(() => {
  if (planner.wanderRoute.value) return "自动闭环路线已生成。";
  if (planner.facilityRoute.value) return "已按道路距离找到最近设施。";
  return "已生成指定地点到达路线。";
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
  } else if (mode === "facility") {
    strategy.value = "time";
    facilityType.value = "restroom";
  }
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
    routeError.value = "无法获取当前位置，请改为手动起点或重试定位。";
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
  }

  if (planner.error.value) routeError.value = planner.error.value;
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
