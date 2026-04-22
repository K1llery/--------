<template>
  <section class="panel-card route-page">
    <div class="section-top">
      <div>
        <h2>地图导航</h2>
        <p>按真实出行流程规划：先确定风格，再选起终点，最后查看分段导航与备选线路。</p>
      </div>
    </div>

    <section class="route-experience">
      <article class="helper-card">
        <h3>出行风格</h3>
        <div class="profile-grid">
          <button
            v-for="profile in travelProfiles"
            :key="profile.key"
            type="button"
            class="profile-chip"
            :class="{ active: activeProfileKey === profile.key }"
            @click="applyTravelProfile(profile.key)"
          >
            <strong>{{ profile.label }}</strong>
            <span>{{ profile.description }}</span>
          </button>
        </div>
      </article>

      <article class="helper-card">
        <h3>出发方式</h3>
        <div class="route-start-row">
          <label class="route-toggle">
            <input v-model="useCurrentLocation" type="checkbox" />
            <span>使用当前位置自动匹配最近起点</span>
          </label>
          <button class="secondary-btn" type="button" :disabled="!supportsGeolocation || locating" @click="captureCurrentLocation">
            {{ locating ? "定位中..." : "刷新定位" }}
          </button>
        </div>
        <p class="toolbar-hint">{{ locationMessage }}</p>
      </article>
    </section>

    <div class="filter-bar">
      <select v-model="selectedCity" class="select-input" @change="handleCityChange">
        <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
      </select>
      <select v-model="selectedSceneName" class="select-input" @change="loadScene">
        <option v-for="scene in visibleScenes" :key="scene.name" :value="scene.name">{{ scene.label }}</option>
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

    <RouteMap :nodes="mapNodes" :path="displayPathCodes" :current-location="currentLocation" />

    <div class="helper-grid">
      <div class="helper-card">
        <h3>当前城市</h3>
        <p>{{ selectedCity }}</p>
        <p>{{ currentSceneMessage }}</p>
      </div>
      <div class="helper-card">
        <h3>推荐起点/停靠</h3>
        <p v-for="item in suggestedNodes" :key="item.code">{{ item.name }}</p>
      </div>
      <div class="helper-card">
        <h3>导航摘要</h3>
        <p>{{ activeNavigationSummary || "规划后会显示路段数量、总时长与策略说明。" }}</p>
      </div>
    </div>

    <div v-if="routeError" class="status-card error-card">{{ routeError }}</div>

    <template v-if="supportsRouting">
      <form class="search-form" @submit.prevent="planRoute">
        <select v-model="startCode" class="select-input" :disabled="useCurrentLocation">
          <option v-for="node in placeOptions" :key="node.code" :value="node.code">{{ node.name }}</option>
        </select>
        <select v-model="endCode" class="select-input">
          <option v-for="node in placeOptions" :key="node.code" :value="node.code">{{ node.name }}</option>
        </select>
        <button class="primary-btn" type="submit">{{ singleLoading ? "规划中..." : "规划单点路线" }}</button>
      </form>

      <div v-if="singleRoute" class="route-summary route-card">
        <div class="section-top compact">
          <h3>{{ singleRoute.strategy_label }}</h3>
          <button class="secondary-btn" @click="saveCurrentRoute">收藏当前路线</button>
        </div>
        <p>{{ singleRoute.explanation }}</p>
        <p v-if="singleRoute.resolved_start_name" class="detail-note">实际起点：{{ singleRoute.resolved_start_name }}</p>
        <div class="detail-stats">
          <span class="stat-pill">{{ singleRoute.total_distance_m }} m</span>
          <span class="stat-pill">{{ singleRoute.estimated_minutes }} 分钟</span>
          <span class="stat-pill">平均拥堵 {{ singleRoute.average_congestion }}</span>
        </div>
        <p><strong>路线：</strong> {{ singleRoute.path_names.join(" → ") }}</p>
      </div>

      <section v-if="singleRoute?.alternatives?.length" class="results-section">
        <div class="section-top compact">
          <h3>备选路线</h3>
          <span class="toolbar-hint">点击卡片可切换地图高亮</span>
        </div>
        <div class="card-grid compact-grid">
          <article
            v-for="item in singleRoute.alternatives"
            :key="item.strategy"
            class="item-card"
            :class="{ selected: selectedAlternativeStrategy === item.strategy }"
            @click="selectedAlternativeStrategy = item.strategy"
          >
            <h3>{{ item.strategy_label }}</h3>
            <p>{{ item.explanation }}</p>
            <p>{{ item.total_distance_m }} m · {{ item.estimated_minutes }} 分钟</p>
          </article>
        </div>
      </section>

      <form class="search-form" @submit.prevent="planMultiRoute">
        <select v-model="multiTargetCodes" class="select-input" multiple size="4">
          <option v-for="node in placeOptions" :key="node.code" :value="node.code">{{ node.name }}</option>
        </select>
        <button class="primary-btn" type="submit">{{ multiLoading ? "规划中..." : "规划多点闭环" }}</button>
      </form>

      <div v-if="multiRoute" class="route-summary route-card">
        <h3>{{ multiRoute.optimization_label }}</h3>
        <p>{{ multiRoute.explanation }}</p>
        <p v-if="multiRoute.resolved_start_name" class="detail-note">实际起点：{{ multiRoute.resolved_start_name }}</p>
        <div class="detail-stats">
          <span class="stat-pill">{{ multiRoute.total_distance_m }} m</span>
          <span class="stat-pill">{{ multiRoute.estimated_minutes }} 分钟</span>
          <span class="stat-pill">{{ multiRoute.strategy_label }}</span>
        </div>
        <p><strong>闭环停靠：</strong> {{ multiRoute.ordered_stop_names.join(" → ") }}</p>
      </div>

      <section v-if="activeSegments.length" class="results-section">
        <div class="section-top compact">
          <h3>分段导航</h3>
          <span class="toolbar-hint">按顺序执行即可完成整段行程</span>
        </div>
        <ol class="timeline-list">
          <li v-for="segment in activeSegments" :key="`segment-${segment.index}-${segment.from_code}-${segment.to_code}`" class="timeline-item">
            <span class="timeline-index">{{ segment.index }}</span>
            <div class="timeline-content">
              <strong>{{ segment.from_name }} → {{ segment.to_name }}</strong>
              <p>{{ segment.instruction }}</p>
              <p class="timeline-meta">
                {{ segment.distance_m }} 米 · {{ segment.estimated_minutes }} 分钟 · 累计 {{ segment.cumulative_distance_m }} 米
              </p>
            </div>
          </li>
        </ol>
      </section>

      <section v-if="indoorBuildingsForScene.length" class="route-summary route-card indoor-card">
        <div class="section-top compact">
          <h3>室内导航模拟</h3>
          <span class="toolbar-hint">支持大门到电梯、跨层换乘和楼层内房间导航</span>
        </div>

        <form class="search-form" @submit.prevent="planIndoorRoute">
          <select v-model="selectedIndoorBuildingCode" class="select-input">
            <option v-for="building in indoorBuildingsForScene" :key="building.building_code" :value="building.building_code">
              {{ building.building_name }}
            </option>
          </select>
          <select v-model="indoorStartNodeCode" class="select-input">
            <option v-for="node in indoorNodeOptions" :key="`indoor-start-${node.code}`" :value="node.code">
              {{ node.name }}（{{ node.floor }}层）
            </option>
          </select>
          <select v-model="indoorEndNodeCode" class="select-input">
            <option v-for="node in indoorNodeOptions" :key="`indoor-end-${node.code}`" :value="node.code">
              {{ node.name }}（{{ node.floor }}层）
            </option>
          </select>
          <select v-model="indoorStrategy" class="select-input">
            <option value="time">最快通过</option>
            <option value="distance">最短距离</option>
            <option value="accessible">无障碍优先</option>
          </select>
          <select v-model="indoorMobilityMode" class="select-input">
            <option value="normal">常规通行</option>
            <option value="wheelchair">轮椅通行</option>
          </select>
          <button class="primary-btn" type="submit">{{ indoorLoading ? "规划中..." : "规划室内路径" }}</button>
        </form>

        <div v-if="indoorRoute" class="results-section">
          <p>{{ indoorRoute.summary }}</p>
          <div class="detail-stats">
            <span class="stat-pill">{{ indoorRoute.total_distance_m }} m</span>
            <span class="stat-pill">{{ indoorRoute.estimated_seconds }} 秒</span>
            <span class="stat-pill">{{ indoorRoute.mobility_mode === "wheelchair" ? "轮椅模式" : "常规模式" }}</span>
          </div>
          <ol class="timeline-list">
            <li v-for="step in indoorRoute.steps" :key="`indoor-step-${step.index}`" class="timeline-item">
              <span class="timeline-index">{{ step.index }}</span>
              <div class="timeline-content">
                <strong>{{ step.from_name }}（{{ step.from_floor }}层） → {{ step.to_name }}（{{ step.to_floor }}层）</strong>
                <p>{{ step.instruction }}</p>
                <p class="timeline-meta">{{ step.distance_m }} 米 · {{ step.estimated_seconds }} 秒 · {{ step.connector }}</p>
              </div>
            </li>
          </ol>
        </div>
      </section>
    </template>

    <div v-else class="status-card">
      {{ selectedCity }}当前支持城市地图浏览与精选地点查看，精细导航即将上线。
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import { api } from "../api/client";
import RouteMap from "../components/RouteMap.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const cities = ["北京", "上海", "广州", "深圳"];
const selectedCity = ref("北京");
const selectedSceneName = ref("BUPT_Main_Campus");
const strategy = ref("distance");
const transportMode = ref("walk");
const activeProfileKey = ref("balanced");
const scenes = ref<any[]>([]);
const featuredDestinations = ref<any[]>([]);
const startCode = ref("");
const endCode = ref("");
const multiTargetCodes = ref<string[]>([]);
const singleRoute = ref<any | null>(null);
const multiRoute = ref<any | null>(null);
const selectedAlternativeStrategy = ref("");
const singleLoading = ref(false);
const multiLoading = ref(false);
const scene = ref<{ nodes: any[] } | null>(null);
const facilities = ref<any[]>([]);
const routeError = ref("");
const useCurrentLocation = ref(false);
const locating = ref(false);
const currentLocation = ref<{ latitude: number; longitude: number } | null>(null);
const indoorBuildings = ref<any[]>([]);
const selectedIndoorBuildingCode = ref("");
const indoorStartNodeCode = ref("");
const indoorEndNodeCode = ref("");
const indoorStrategy = ref("time");
const indoorMobilityMode = ref("normal");
const indoorRoute = ref<any | null>(null);
const indoorLoading = ref(false);

const supportsGeolocation = typeof navigator !== "undefined" && "geolocation" in navigator;

const travelProfiles = [
  {
    key: "balanced",
    label: "省时优先",
    description: "最快到达 + 综合交通",
    strategy: "time",
    transportMode: "mixed",
  },
  {
    key: "urgent",
    label: "赶路直达",
    description: "最短距离 + 骑行",
    strategy: "distance",
    transportMode: "bike",
  },
  {
    key: "relaxed",
    label: "轻松漫游",
    description: "打卡优先 + 步行",
    strategy: "scenic",
    transportMode: "walk",
  },
  {
    key: "stable",
    label: "避堵稳妥",
    description: "避拥堵 + 综合交通",
    strategy: "congestion",
    transportMode: "mixed",
  },
];

const visibleScenes = computed(() => scenes.value.filter((item) => item.city === selectedCity.value));
const supportsRouting = computed(() => visibleScenes.value.find((item) => item.name === selectedSceneName.value)?.supports_routing ?? false);
const placeOptions = computed(() => ([...(scene.value?.nodes ?? []), ...facilities.value]));
const indoorBuildingsForScene = computed(() => indoorBuildings.value.filter((item) => item.scene_name === selectedSceneName.value));
const activeIndoorBuilding = computed(() => {
  if (!indoorBuildingsForScene.value.length) return null;
  return indoorBuildingsForScene.value.find((item) => item.building_code === selectedIndoorBuildingCode.value) ?? indoorBuildingsForScene.value[0];
});
const indoorNodeOptions = computed(() => activeIndoorBuilding.value?.nodes ?? []);
const mapNodes = computed(() => {
  if (supportsRouting.value) return placeOptions.value;
  return featuredDestinations.value
    .filter((item) => item.city === selectedCity.value)
    .map((item) => ({
      code: item.source_id,
      name: item.name,
      latitude: item.latitude,
      longitude: item.longitude
    }));
});
const currentSceneMessage = computed(() =>
  supportsRouting.value ? `${mapNodes.value.length} 个点位可用于精细规划。` : `${mapNodes.value.length} 个精选地点可用于城市浏览。`
);
const suggestedNodes = computed(() => placeOptions.value.slice(0, 4));
const activeNavigationSummary = computed(() => {
  if (selectedAlternativeStrategy.value && singleRoute.value?.alternatives?.length) {
    const alternative = singleRoute.value.alternatives.find((item: any) => item.strategy === selectedAlternativeStrategy.value);
    if (alternative) return alternative.navigation_summary;
  }
  return multiRoute.value?.navigation_summary || singleRoute.value?.navigation_summary || "";
});

const activeSegments = computed(() => {
  if (selectedAlternativeStrategy.value && singleRoute.value?.alternatives?.length) {
    const alternative = singleRoute.value.alternatives.find((item: any) => item.strategy === selectedAlternativeStrategy.value);
    if (alternative?.segments?.length) return alternative.segments;
  }
  return multiRoute.value?.segments || singleRoute.value?.segments || [];
});

const locationMessage = computed(() => {
  if (!supportsGeolocation) return "当前浏览器不支持定位，可手动选择起点。";
  if (!useCurrentLocation.value) return "可手动选择起点，或开启当前位置自动匹配。";
  if (locating.value) return "正在获取当前位置...";
  if (currentLocation.value) {
    return `已定位：${currentLocation.value.latitude.toFixed(5)}, ${currentLocation.value.longitude.toFixed(5)}（规划时将自动匹配最近点）。`;
  }
  return "尚未定位，点击“刷新定位”后可自动匹配最近起点。";
});
const displayPathCodes = computed(() => {
  if (selectedAlternativeStrategy.value && singleRoute.value?.alternatives?.length) {
    const alternative = singleRoute.value.alternatives.find((item: any) => item.strategy === selectedAlternativeStrategy.value);
    if (alternative) return alternative.path_codes;
  }
  if (Array.isArray(multiRoute.value?.path_codes) && multiRoute.value.path_codes.length) return multiRoute.value.path_codes;
  return singleRoute.value?.path_codes ?? [];
});

const loadMeta = async () => {
  const [sceneRes, featuredRes, indoorRes] = await Promise.all([
    api.get("/map/scenes"),
    api.get("/destinations/featured"),
    api.get("/indoor/buildings"),
  ]);
  scenes.value = sceneRes.data;
  featuredDestinations.value = featuredRes.data;
  indoorBuildings.value = indoorRes.data.items ?? [];
};

const syncDefaultNodes = () => {
  startCode.value = placeOptions.value[0]?.code ?? "";
  endCode.value = placeOptions.value[1]?.code ?? startCode.value;
  multiTargetCodes.value = placeOptions.value.slice(1, 4).map((item) => item.code);
};

const syncIndoorDefaults = () => {
  selectedIndoorBuildingCode.value = indoorBuildingsForScene.value[0]?.building_code ?? "";
  indoorStartNodeCode.value = indoorNodeOptions.value[0]?.code ?? "";
  indoorEndNodeCode.value = indoorNodeOptions.value[1]?.code ?? indoorStartNodeCode.value;
  indoorRoute.value = null;
};

const applyTravelProfile = (profileKey: string) => {
  const profile = travelProfiles.find((item) => item.key === profileKey);
  if (!profile) return;
  activeProfileKey.value = profile.key;
  strategy.value = profile.strategy;
  transportMode.value = profile.transportMode;
};

const captureCurrentLocation = async () => {
  if (!supportsGeolocation) return;
  locating.value = true;
  try {
    const coordinates = await new Promise<{ latitude: number; longitude: number }>((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        reject,
        { enableHighAccuracy: true, timeout: 5000 }
      );
    });
    currentLocation.value = coordinates;
  } catch {
    routeError.value = "定位失败，请检查浏览器定位权限或改用手动起点。";
  } finally {
    locating.value = false;
  }
};

const locationPayload = () => {
  if (useCurrentLocation.value && currentLocation.value) {
    return {
      prefer_nearest_start: true,
      start_latitude: currentLocation.value.latitude,
      start_longitude: currentLocation.value.longitude,
    };
  }
  return {
    prefer_nearest_start: false,
    start_latitude: null,
    start_longitude: null,
  };
};

const ensureLocationReady = async () => {
  if (!useCurrentLocation.value) return true;
  if (currentLocation.value) return true;
  await captureCurrentLocation();
  return Boolean(currentLocation.value);
};

const handleCityChange = async () => {
  routeError.value = "";
  selectedSceneName.value = visibleScenes.value[0]?.name ?? "";
  await loadScene();
};

const loadScene = async () => {
  routeError.value = "";
  singleRoute.value = null;
  multiRoute.value = null;
  indoorRoute.value = null;
  selectedAlternativeStrategy.value = "";
  if (!supportsRouting.value) {
    scene.value = { nodes: [] };
    facilities.value = [];
    syncIndoorDefaults();
    return;
  }
  const { data } = await api.get(`/map/scenes/${selectedSceneName.value}`);
  scene.value = data.scene;
  facilities.value = data.facilities;
  syncDefaultNodes();
  syncIndoorDefaults();
};

const planRoute = async () => {
  routeError.value = "";
  const canRoute = await ensureLocationReady();
  if (!canRoute && useCurrentLocation.value) {
    routeError.value = "无法获取当前位置，请改为手动起点或重试定位。";
    return;
  }
  singleLoading.value = true;
  multiRoute.value = null;
  selectedAlternativeStrategy.value = "";
  try {
    const { data } = await api.post("/routes/single", {
      scene_name: selectedSceneName.value,
      start_code: startCode.value,
      end_code: endCode.value,
      strategy: strategy.value,
      transport_mode: transportMode.value,
      ...locationPayload(),
    });
    singleRoute.value = data;
  } catch (error: any) {
    routeError.value = error?.response?.data?.detail || "路线规划失败，请稍后重试。";
  } finally {
    singleLoading.value = false;
  }
};

const planMultiRoute = async () => {
  routeError.value = "";
  const canRoute = await ensureLocationReady();
  if (!canRoute && useCurrentLocation.value) {
    routeError.value = "无法获取当前位置，请改为手动起点或重试定位。";
    return;
  }
  multiLoading.value = true;
  singleRoute.value = null;
  selectedAlternativeStrategy.value = "";
  try {
    const { data } = await api.post("/routes/multi", {
      scene_name: selectedSceneName.value,
      start_code: startCode.value,
      target_codes: multiTargetCodes.value,
      strategy: strategy.value,
      transport_mode: transportMode.value,
      ...locationPayload(),
    });
    multiRoute.value = data;
  } catch (error: any) {
    routeError.value = error?.response?.data?.detail || "多点路线规划失败，请稍后重试。";
  } finally {
    multiLoading.value = false;
  }
};

const planIndoorRoute = async () => {
  routeError.value = "";
  if (!selectedIndoorBuildingCode.value || !indoorStartNodeCode.value || !indoorEndNodeCode.value) {
    routeError.value = "当前场景缺少可用的室内导航点位。";
    return;
  }

  indoorLoading.value = true;
  try {
    const { data } = await api.post("/indoor/route", {
      building_code: selectedIndoorBuildingCode.value,
      start_node_code: indoorStartNodeCode.value,
      end_node_code: indoorEndNodeCode.value,
      strategy: indoorStrategy.value,
      mobility_mode: indoorMobilityMode.value,
    });
    indoorRoute.value = data;
  } catch (error: any) {
    routeError.value = error?.response?.data?.detail || "室内导航失败，请稍后重试。";
  } finally {
    indoorLoading.value = false;
  }
};

const saveCurrentRoute = async () => {
  const payload =
    selectedAlternativeStrategy.value && singleRoute.value?.alternatives?.length
      ? singleRoute.value.alternatives.find((item: any) => item.strategy === selectedAlternativeStrategy.value) || singleRoute.value
      : singleRoute.value;
  if (!payload) return;
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  await auth.saveRouteFavorite({
    scene_name: selectedSceneName.value,
    strategy: payload.strategy,
    transport_mode: transportMode.value,
    path_codes: payload.path_codes,
    path_names: payload.path_names,
    total_distance_m: payload.total_distance_m,
    estimated_minutes: payload.estimated_minutes,
    explanation: payload.explanation
  });
};

onMounted(async () => {
  applyTravelProfile("balanced");
  await loadMeta();
  selectedSceneName.value = visibleScenes.value[0]?.name ?? "";
  await loadScene();
});

watch(useCurrentLocation, async (enabled) => {
  if (enabled && !currentLocation.value) {
    await captureCurrentLocation();
  }
});

watch(selectedIndoorBuildingCode, () => {
  indoorStartNodeCode.value = indoorNodeOptions.value[0]?.code ?? "";
  indoorEndNodeCode.value = indoorNodeOptions.value[1]?.code ?? indoorStartNodeCode.value;
  indoorRoute.value = null;
});
</script>
