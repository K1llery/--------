<template>
  <div class="space-y-6">
    <!-- Header + filters -->
    <div class="bg-white rounded-3xl card-elevated p-6">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 class="text-xl font-bold text-gray-900">附近设施</h2>
          <p class="text-sm text-gray-500 mt-1">
            按路线距离查看当前场景周边的餐厅、超市、服务点和其他设施。
          </p>
        </div>
        <button class="btn-soft-primary text-sm" @click="loadFacilities">
          {{ loading ? "查询中..." : "查询设施" }}
        </button>
      </div>
      <div class="flex flex-wrap gap-3 mt-5">
        <select v-model="sceneName" class="soft-control text-sm text-gray-700" @change="loadScene">
          <option v-for="scene in scenes" :key="scene.value" :value="scene.value">
            {{ scene.label }}
          </option>
        </select>
        <select v-model="originCode" class="soft-control text-sm text-gray-700">
          <option v-for="node in originOptions" :key="node.code" :value="node.code">
            {{ node.name }}
          </option>
        </select>
        <select v-model="categoryFilter" class="soft-control text-sm text-gray-700">
          <option value="">全部设施</option>
          <option v-for="item in categoryOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
        <select v-model="radius" class="soft-control text-sm text-gray-700">
          <option :value="300">300 米内</option>
          <option :value="600">600 米内</option>
          <option :value="1000">1000 米内</option>
          <option :value="1500">1500 米内</option>
        </select>
      </div>
    </div>
    <!-- Info cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="bg-white rounded-2xl border-0 shadow-md shadow-gray-200/50 p-4">
        <h3 class="text-sm font-semibold text-gray-900">当前场景</h3>
        <p class="text-sm text-gray-600 mt-1">{{ currentSceneLabel }}</p>
        <p class="text-xs text-gray-400 mt-0.5">{{ sceneHint }}</p>
      </div>
      <div class="bg-white rounded-2xl border-0 shadow-md shadow-gray-200/50 p-4">
        <h3 class="text-sm font-semibold text-gray-900">已选起点</h3>
        <p class="text-sm text-gray-600 mt-1">
          {{ currentOrigin?.name || "请选择起点" }}
        </p>
        <p class="text-xs text-gray-400 mt-0.5">{{ facilities.length }} 个结果可查看</p>
      </div>
    </div>
    <!-- Status -->
    <div v-if="error" class="alert-soft-error">{{ error }}</div>
    <div
      v-else-if="loading"
      class="p-4 rounded-2xl bg-gray-50 border-0 shadow-md shadow-gray-200/50 text-sm text-gray-500"
    >
      正在计算周边设施距离...
    </div>
    <div
      v-else-if="facilities.length === 0"
      class="p-4 rounded-2xl bg-gray-50 border-0 shadow-md shadow-gray-200/50 text-sm text-gray-500"
    >
      当前条件下没有找到合适的设施。
    </div>
    <!-- Content -->
    <div v-else class="grid lg:grid-cols-[1.4fr_1fr] gap-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <article
          v-for="item in facilities"
          :key="item.code"
          class="rounded-2xl border-0 shadow-md shadow-gray-200/50 p-4 cursor-pointer transition-all duration-200"
          :class="
            selected?.code === item.code
              ? 'bg-primary-50 shadow-md shadow-primary-500/10 ring-1 ring-primary-200'
              : 'bg-white hover:shadow-lg '
          "
          @click="selected = item"
        >
          <h3 class="font-semibold text-gray-900 text-sm">{{ item.name }}</h3>
          <p class="text-xs text-gray-500 mt-1">
            {{ facilityLabel(item) }} · 图距离 {{ Number(item.graph_distance).toFixed(0) }}m
          </p>
          <p class="text-xs text-gray-400 mt-0.5">{{ currentSceneLabel }}</p>
        </article>
      </div>
      <!-- Detail -->
      <div
        v-if="selected"
        class="bg-white rounded-3xl card-elevated p-5 sticky top-16 self-start space-y-4"
      >
        <div
          class="relative h-32 rounded-2xl overflow-hidden bg-gradient-to-br from-primary-50 via-white to-accent-50 border-0 shadow-md shadow-gray-200/50"
        >
          <div class="absolute -top-6 -right-6 w-28 h-28 rounded-full bg-primary-200/30 blur-2xl" />
          <div
            class="absolute -bottom-8 -left-8 w-28 h-28 rounded-full bg-accent-200/30 blur-2xl"
          />
          <div class="relative h-full flex items-center gap-4 px-5">
            <div
              class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 text-white flex items-center justify-center shadow-lg shadow-primary-500/25 flex-shrink-0"
            >
              <component :is="facilityIcon(selected)" />
            </div>
            <div class="min-w-0">
              <p class="text-[10px] font-semibold uppercase tracking-wider text-primary-600/80">
                Facility
              </p>
              <p class="text-lg font-bold text-gray-900 leading-tight mt-0.5">
                {{ facilityLabel(selected) }}
              </p>
              <p class="text-xs text-gray-500 mt-0.5 truncate">
                距离 {{ Number(selected.graph_distance).toFixed(0) }}m ·
                {{ currentSceneLabel }}
              </p>
            </div>
          </div>
        </div>
        <div>
          <h3 class="text-lg font-bold text-gray-900">{{ selected.name }}</h3>
          <p class="text-sm text-gray-500 mt-1">
            {{ facilityLabel(selected) }} · {{ currentSceneLabel }}
          </p>
          <p class="text-sm text-gray-500 mt-0.5">
            坐标：{{ selected.latitude }}, {{ selected.longitude }}
          </p>
          <p class="text-sm text-gray-600 mt-3 leading-relaxed">
            {{ facilityDescription(selected) }}
          </p>
          <div class="flex flex-wrap gap-2 mt-4">
            <span
              class="text-xs px-3 py-1.5 rounded-full bg-primary-50 text-primary-700 font-medium"
              >图距离 {{ Number(selected.graph_distance).toFixed(0) }}m</span
            >
            <span class="text-xs px-3 py-1.5 rounded-full bg-gray-100 text-gray-600"
              >起点 {{ currentOrigin?.name }}</span
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, h, onMounted, ref } from "vue";
import { api } from "../api/client";
const scenes = [
  { value: "BUPT_Main_Campus", label: "北京邮电大学校园" },
  { value: "Summer_Palace", label: "颐和园景区" },
];
const sceneName = ref("BUPT_Main_Campus");
const originCode = ref("");
const categoryFilter = ref("");
const radius = ref(1000);
const loading = ref(false);
const error = ref("");
const nodes = ref<any[]>([]);
const facilities = ref<any[]>([]);
const selected = ref<any | null>(null);
const categoryOptions = [
  { value: "restaurant", label: "餐厅" },
  { value: "supermarket", label: "超市" },
  { value: "artwork", label: "景观/雕塑" },
  { value: "restroom", label: "洗手间" },
  { value: "service", label: "服务点" },
  { value: "shop", label: "商店" },
  { value: "sports", label: "运动场馆" },
  { value: "other", label: "其他设施" },
];
const currentSceneLabel = computed(
  () => scenes.find((item) => item.value === sceneName.value)?.label ?? "场景",
);
const originOptions = computed(() => nodes.value);
const currentOrigin = computed(() =>
  originOptions.value.find((item) => item.code === originCode.value),
);
const sceneHint = computed(() =>
  sceneName.value === "BUPT_Main_Campus"
    ? "适合演示校园内餐饮、服务点和运动设施。"
    : "适合演示景区内服务点与游客设施。",
);
const inferFacilityType = (item: any) => {
  const name = item.name ?? "";
  const raw = item.facility_type;
  if (raw === "yes") {
    if (/游泳|体育|球馆/.test(name)) return "sports";
    if (/雕像|雕塑|像/.test(name)) return "artwork";
    return "other";
  }
  if (raw === "canteen" || raw === "restaurant" || raw === "cafe") return "restaurant";
  if (raw === "market") return "supermarket";
  if (raw === "museum" || raw === "viewpoint") return "artwork";
  if (raw === "service" || raw === "visitor_center" || raw === "ticket") return "service";
  if (raw === "restroom") return "restroom";
  if (raw === "shop" || raw === "rental" || raw === "guide") return "shop";
  if (raw === "sports") return "sports";
  return raw || "other";
};
const facilityLabel = (item: any) => {
  const type = inferFacilityType(item);
  const mapping: Record<string, string> = {
    restaurant: "餐厅",
    supermarket: "超市",
    artwork: "景观/雕塑",
    restroom: "洗手间",
    service: "服务点",
    shop: "商店",
    sports: "运动场馆",
    other: "其他设施",
  };
  return mapping[type] ?? "其他设施";
};
const facilityDescription = (item: any) =>
  `${item.name} 位于${currentSceneLabel.value}内，适合在行程中途补给、休息或打卡查看。`;
const iconProps = {
  fill: "none",
  viewBox: "0 0 24 24",
  stroke: "currentColor",
  "stroke-width": "1.8",
  class: "w-7 h-7",
};
const IconRestaurant = () =>
  h("svg", iconProps, [
    h("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "M12 8.25v-1.5m0 1.5c-1.355 0-2.697.056-4.024.166C6.845 8.51 6 9.473 6 10.608v2.513m6-4.871c1.355 0 2.697.056 4.024.166C17.155 8.51 18 9.473 18 10.608v2.513M15 8.25v-1.5m-6 1.5v-1.5m12 9.75-1.5.75a3.354 3.354 0 0 1-3 0 3.354 3.354 0 0 0-3 0 3.354 3.354 0 0 1-3 0 3.354 3.354 0 0 0-3 0 3.354 3.354 0 0 1-3 0L3 16.5m15-3.379a48.474 48.474 0 0 0-6-.371c-2.032 0-4.034.126-6 .371m12 0c.39.049.777.102 1.163.16 1.07.16 1.837 1.094 1.837 2.175v5.17c0 .62-.504 1.124-1.125 1.124H4.125A1.125 1.125 0 0 1 3 20.496v-5.17c0-1.08.768-2.014 1.837-2.174A47.78 47.78 0 0 1 6 12.871",
    }),
  ]);
const IconShop = () =>
  h("svg", iconProps, [
    h("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007ZM8.625 10.5a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm7.5 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z",
    }),
  ]);
const IconService = () =>
  h("svg", iconProps, [
    h("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z",
    }),
  ]);
const IconRestroom = () =>
  h("svg", iconProps, [
    h("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "M12 12.75c1.148 0 2.278.08 3.383.237 1.037.146 1.866.966 1.866 2.013 0 3.728-2.35 6.75-5.25 6.75S6.75 18.728 6.75 15c0-1.046.83-1.867 1.866-2.013A24.204 24.204 0 0 1 12 12.75Zm0 0c2.883 0 5.647.508 8.207 1.44a23.91 23.91 0 0 1-1.152 6.06M12 12.75c-2.883 0-5.647.508-8.208 1.44.125 2.104.52 4.136 1.153 6.06M12 12.75V3.104M4.867 19.125h.008v.008h-.008v-.008Zm.125 2.25a.125.125 0 1 1-.25 0 .125.125 0 0 1 .25 0Z",
    }),
  ]);
const IconSports = () =>
  h("svg", iconProps, [
    h("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418",
    }),
  ]);
const IconArtwork = () =>
  h("svg", iconProps, [
    h("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z",
    }),
  ]);
const IconSupermarket = () =>
  h("svg", iconProps, [
    h("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 0 0-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 0 0-16.536-1.84M7.5 14.25 5.106 5.272M6 20.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm12.75 0a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z",
    }),
  ]);
const IconGeneric = () =>
  h("svg", iconProps, [
    h("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21m-5.25 0h5.25",
    }),
  ]);
const facilityIcon = (item: any) => {
  const type = inferFacilityType(item);
  if (type === "restaurant") return IconRestaurant;
  if (type === "shop") return IconShop;
  if (type === "supermarket") return IconSupermarket;
  if (type === "service") return IconService;
  if (type === "restroom") return IconRestroom;
  if (type === "sports") return IconSports;
  if (type === "artwork") return IconArtwork;
  return IconGeneric;
};
const loadScene = async () => {
  try {
    const { data } = await api.get(`/map/scenes/${sceneName.value}`);
    nodes.value = data.scene?.nodes ?? [];
    originCode.value = nodes.value[0]?.code ?? "";
    selected.value = null;
  } catch (sceneError) {
    error.value = "场景加载失败，请刷新重试。";
  }
};
const loadFacilities = async () => {
  if (!originCode.value) return;
  loading.value = true;
  error.value = "";
  try {
    const params: Record<string, string | number> = {
      scene_name: sceneName.value,
      origin_code: originCode.value,
      radius: radius.value,
    };
    if (categoryFilter.value && categoryFilter.value !== "other") {
      params.category = categoryFilter.value;
    }
    const { data } = await api.get("/facilities/nearby", { params });
    facilities.value = (data as any[]).filter((item) => {
      if (!categoryFilter.value) return true;
      return inferFacilityType(item) === categoryFilter.value;
    });
    selected.value = facilities.value[0] ?? null;
  } catch (facilityError) {
    error.value = "设施查询失败，请稍后再试。";
  } finally {
    loading.value = false;
  }
};
onMounted(async () => {
  await loadScene();
  await loadFacilities();
});
</script>
