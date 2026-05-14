<template>
  <div class="facility-page space-y-6">
    <section class="card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">设施查询</p>
          <h2 class="text-2xl font-bold text-slate-950 mt-1">场景周边服务与配套</h2>
          <p class="text-sm text-slate-500 mt-2 leading-7 max-w-3xl">
            以场景和起点为基础，按图距离快速查询周边餐饮、商店、服务点和游客设施，适合在导航与行程之间补足临时需求。
          </p>
        </div>
        <button class="btn-soft-primary text-sm" @click="loadFacilities">
          {{ loading ? "正在查询..." : "查询设施" }}
        </button>
      </div>

      <div class="facility-filter-bar mt-5">
        <select v-model="sceneName" class="soft-control text-sm text-slate-700" @change="loadScene">
          <option v-for="scene in scenes" :key="scene.value" :value="scene.value">
            {{ scene.label }}
          </option>
        </select>
        <select v-model="originCode" class="soft-control text-sm text-slate-700">
          <option v-for="node in originOptions" :key="node.code" :value="node.code">
            {{ node.name }}
          </option>
        </select>
        <select v-model="categoryFilter" class="soft-control text-sm text-slate-700">
          <option value="">全部设施</option>
          <option v-for="item in categoryOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
        <select v-model="radius" class="soft-control text-sm text-slate-700">
          <option :value="300">300 米内</option>
          <option :value="600">600 米内</option>
          <option :value="1000">1000 米内</option>
          <option :value="1500">1500 米内</option>
        </select>
      </div>

      <div v-if="selectedTags.length" class="flex flex-wrap gap-2 mt-4">
        <button v-for="tag in selectedTags" :key="tag.key" class="destination-tag-pill" @click="removeTag(tag.key)">
          {{ tag.label }}
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </section>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <section class="route-insight-card">
        <span class="route-panel-kicker">当前场景</span>
        <h3>{{ currentSceneLabel }}</h3>
        <p>{{ sceneHint }}</p>
      </section>
      <section class="route-insight-card">
        <span class="route-panel-kicker">查询起点</span>
        <h3>{{ currentOrigin?.name || "请选择起点" }}</h3>
        <p>设施距离会按图距离计算，适合展示真实场景中的步行可达关系。</p>
      </section>
      <section class="route-insight-card">
        <span class="route-panel-kicker">结果规模</span>
        <div class="grid grid-cols-2 gap-3 mt-4">
          <div class="route-metric-tile">
            <strong>{{ facilities.length }}</strong>
            <span>当前结果</span>
          </div>
          <div class="route-metric-tile">
            <strong>{{ radius }}</strong>
            <span>搜索半径 / 米</span>
          </div>
        </div>
      </section>
    </div>

    <div v-if="error" class="alert-soft-error">{{ error }}</div>
    <div v-else-if="loading" class="card-elevated rounded-[22px] p-5 text-sm text-slate-500">
      正在计算周边设施图距离，请稍候…
    </div>
    <EmptyState
      v-else-if="facilities.length === 0"
      title="暂无匹配设施"
      description="当前场景、设施类型和半径组合下没有找到结果，可以扩大半径或切换设施类型。"
      action-hint="优先试试全部设施或 1000 米内。"
    />

    <div v-else class="grid xl:grid-cols-[minmax(0,1.2fr)_360px] gap-6 items-start">
      <section class="card-elevated rounded-[24px] p-5 lg:p-6">
        <div class="flex items-start justify-between gap-4 flex-wrap mb-5">
          <div>
            <span class="route-panel-kicker">结果列表</span>
            <h3 class="text-lg font-bold text-slate-950 mt-1">共 {{ facilities.length }} 个周边设施</h3>
            <p class="text-sm text-slate-500 mt-2">
              当前优先展示 {{ currentSceneLabel }} 中距
              {{ currentOrigin?.name || "所选起点" }}
              最近的设施，便于直接判断是否值得绕行或顺路补给。
            </p>
          </div>
          <span class="route-summary-chip">
            {{ currentCategoryLabel || "全部设施" }}
          </span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
          <article
            v-for="item in facilities"
            :key="item.code"
            class="facility-card"
            :class="{ 'facility-card-active': selected?.code === item.code }"
            @click="selected = item"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <h3 class="text-base font-bold text-slate-900 truncate">{{ item.name }}</h3>
                <p class="text-sm text-slate-500 mt-1">
                  {{ facilityLabel(item) }} · {{ currentSceneLabel }}
                </p>
              </div>
              <span class="facility-card-badge">{{ facilityLabel(item) }}</span>
            </div>

            <p class="text-sm text-slate-400 mt-3">
              图距离 {{ formatDistance(item.graph_distance) }} · 起点 {{ currentOrigin?.name || "未选择" }}
            </p>

            <div class="flex flex-wrap gap-2 mt-3">
              <span class="route-summary-chip">图距离 {{ formatDistance(item.graph_distance) }}</span>
              <span class="route-summary-chip route-summary-chip-accent">
                {{ item.normalized_type || inferFacilityType(item) }}
              </span>
            </div>
          </article>
        </div>
      </section>

      <aside class="space-y-5">
        <section
          v-if="selected"
          class="card-elevated rounded-[24px] p-5 sticky top-18 self-start space-y-4 facility-detail-card"
        >
          <div class="facility-detail-hero">
            <div class="facility-detail-icon">
              <component :is="facilityIcon(selected)" />
            </div>
            <div class="min-w-0">
              <span class="route-panel-kicker">当前详情</span>
              <h3 class="text-xl font-bold text-slate-950 mt-1">{{ selected.name }}</h3>
              <p class="text-sm text-slate-500 mt-1">
                {{ facilityLabel(selected) }} · {{ currentSceneLabel }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="route-metric-tile">
              <strong>{{ formatDistance(selected.graph_distance) }}</strong>
              <span>图距离</span>
            </div>
            <div class="route-metric-tile">
              <strong>{{ currentOrigin?.name || "未选" }}</strong>
              <span>当前起点</span>
            </div>
          </div>

          <div class="space-y-3">
            <p class="text-sm text-slate-500">
              坐标：{{ selected.latitude }}, {{ selected.longitude }}
            </p>
            <p class="text-sm text-slate-600 leading-7">
              {{ facilityDescription(selected) }}
            </p>
          </div>

          <div class="flex flex-wrap gap-2">
            <span class="route-summary-chip">{{ facilityLabel(selected) }}</span>
            <span class="route-summary-chip">{{ currentSceneLabel }}</span>
            <span class="route-summary-chip route-summary-chip-accent">半径 {{ radius }} 米</span>
          </div>
        </section>

        <section v-else class="card-elevated rounded-[24px] p-5 space-y-3">
          <span class="route-panel-kicker">详情面板</span>
          <h3 class="text-lg font-bold text-slate-950">先从左侧选择一个设施</h3>
          <p class="text-sm text-slate-500 leading-7">
            这里会集中展示设施类别、图距离、场景位置和用途说明，方便继续决定是否前往。
          </p>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from "vue";

import EmptyState from "../components/EmptyState.vue";
import { api } from "../api/client";
import type { Facility, SceneNode } from "../types/models";

type FacilityItem = Facility & {
  graph_distance?: number;
  normalized_type?: string;
  facility_label?: string;
};

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
const nodes = ref<SceneNode[]>([]);
const facilities = ref<FacilityItem[]>([]);
const selected = ref<FacilityItem | null>(null);

const categoryOptions = [
  { value: "restaurant", label: "餐厅" },
  { value: "supermarket", label: "超市" },
  { value: "artwork", label: "景观 / 雕塑" },
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

const currentCategoryLabel = computed(
  () => categoryOptions.find((item) => item.value === categoryFilter.value)?.label ?? "",
);

const sceneHint = computed(() =>
  sceneName.value === "BUPT_Main_Campus"
    ? "适合演示校园内餐饮、服务点、洗手间和运动设施的最近可达关系。"
    : "适合演示景区内游客服务点、餐饮与公共设施的步行补给场景。",
);

const inferFacilityType = (item: FacilityItem) => {
  if (item.normalized_type) return item.normalized_type;

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

const facilityLabel = (item: FacilityItem) => {
  if (item.facility_label) return item.facility_label;

  const type = inferFacilityType(item);
  const mapping: Record<string, string> = {
    restaurant: "餐厅",
    supermarket: "超市",
    artwork: "景观 / 雕塑",
    restroom: "洗手间",
    service: "服务点",
    shop: "商店",
    sports: "运动场馆",
    other: "其他设施",
  };
  return mapping[type] ?? "其他设施";
};

const facilityDescription = (item: FacilityItem) =>
  `${item.name} 位于 ${currentSceneLabel.value} 内，适合在游览过程中作为顺路补给、休息、服务咨询或短暂停留的节点。`;

const formatDistance = (value: number | undefined) => `${Number(value ?? 0).toFixed(0)} 米`;

const removeTag = (key: string) => {
  if (key === "category") categoryFilter.value = "";
  if (key === "radius") radius.value = 1000;
};

const selectedTags = computed<Array<{ key: string; label: string }>>(() => {
  const tags: Array<{ key: string; label: string }> = [];

  if (categoryFilter.value) {
    tags.push({ key: "category", label: `设施类型：${currentCategoryLabel.value}` });
  }

  if (radius.value !== 1000) {
    tags.push({ key: "radius", label: `半径：${radius.value} 米` });
  }

  return tags;
});

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

const facilityIcon = (item: FacilityItem) => {
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
  } catch {
    error.value = "场景加载失败，请刷新后重试。";
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

    const { data } = await api.get<FacilityItem[]>("/facilities/nearby", { params });
    facilities.value = data.filter((item) => {
      if (!categoryFilter.value) return true;
      return inferFacilityType(item) === categoryFilter.value;
    });
    selected.value = facilities.value[0] ?? null;
  } catch {
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
