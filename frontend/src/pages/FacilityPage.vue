<template>
  <section class="panel-card">
    <div class="section-top">
      <div>
        <h2>附近设施</h2>
        <p>按路线距离查看当前场景周边的餐厅、超市、服务点和其他设施。</p>
      </div>
    </div>

    <div class="filter-bar">
      <select v-model="sceneName" class="select-input" @change="loadScene">
        <option v-for="scene in scenes" :key="scene.value" :value="scene.value">
          {{ scene.label }}
        </option>
      </select>
      <select v-model="originCode" class="select-input">
        <option v-for="node in originOptions" :key="node.code" :value="node.code">
          {{ node.name }}
        </option>
      </select>
      <select v-model="categoryFilter" class="select-input">
        <option value="">全部设施</option>
        <option v-for="item in categoryOptions" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
      <select v-model="radius" class="select-input">
        <option :value="300">300 米内</option>
        <option :value="600">600 米内</option>
        <option :value="1000">1000 米内</option>
        <option :value="1500">1500 米内</option>
      </select>
      <button class="primary-btn" @click="loadFacilities">
        {{ loading ? "查询中..." : "查询设施" }}
      </button>
    </div>

    <div class="helper-grid">
      <div class="helper-card">
        <h3>当前场景</h3>
        <p>{{ currentSceneLabel }}</p>
        <p>{{ sceneHint }}</p>
      </div>
      <div class="helper-card">
        <h3>已选起点</h3>
        <p>{{ currentOrigin?.name || "请选择起点" }}</p>
        <p>{{ facilities.length }} 个结果可查看</p>
      </div>
    </div>

    <div v-if="error" class="status-card error-card">{{ error }}</div>
    <div v-else-if="loading" class="status-card">正在计算周边设施距离...</div>
    <div v-else-if="facilities.length === 0" class="status-card">
      当前条件下没有找到合适的设施。
    </div>
    <div v-else class="content-split">
      <div class="card-grid">
        <article
          v-for="item in facilities"
          :key="item.code"
          class="item-card"
          :class="{ selected: selected?.code === item.code }"
          @click="selected = item"
        >
          <h3>{{ item.name }}</h3>
          <p>{{ facilityLabel(item) }} · 图距离 {{ Number(item.graph_distance).toFixed(0) }}m</p>
          <p>{{ currentSceneLabel }}</p>
        </article>
      </div>

      <section v-if="selected" class="detail-panel detail-stack">
        <div class="detail-placeholder">
          <span>{{ facilityLabel(selected) }}</span>
        </div>
        <div>
          <h3>{{ selected.name }}</h3>
          <p>{{ facilityLabel(selected) }} · {{ currentSceneLabel }}</p>
          <p>坐标：{{ selected.latitude }}, {{ selected.longitude }}</p>
          <p>{{ facilityDescription(selected) }}</p>
          <div class="detail-stats">
            <span class="stat-pill">图距离 {{ Number(selected.graph_distance).toFixed(0) }}m</span>
            <span class="stat-pill">起点 {{ currentOrigin?.name }}</span>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

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
