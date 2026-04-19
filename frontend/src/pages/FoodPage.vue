<template>
  <section class="panel-card">
    <div class="section-top">
      <div>
        <h2>美食推荐</h2>
        <p>从城市特色餐厅到景点周边高评分选择，快速筛出这一顿该去哪里。</p>
      </div>
      <button class="primary-btn" @click="load(true)">{{ loading ? "加载中..." : "刷新推荐" }}</button>
    </div>

    <div class="filter-bar">
      <select v-model="cityFilter" class="select-input">
        <option value="全部">全部城市</option>
        <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
      </select>
      <select v-model="cuisineFilter" class="select-input">
        <option value="全部">全部菜系</option>
        <option v-for="cuisine in cuisines" :key="cuisine" :value="cuisine">{{ cuisine }}</option>
      </select>
      <select v-model="destinationFilter" class="select-input">
        <option value="全部">全部关联目的地</option>
        <option v-for="destination in destinations" :key="destination" :value="destination">{{ destination }}</option>
      </select>
      <select v-model="sortMode" class="select-input">
        <option value="recommended">推荐优先</option>
        <option value="rating">评分优先</option>
        <option value="heat">热度优先</option>
      </select>
      <span class="toolbar-hint" v-if="lastUpdated">更新于 {{ lastUpdated }}</span>
    </div>

    <div v-if="error" class="status-card error-card">{{ error }}</div>
    <div v-else-if="loading" class="status-card">正在刷新四城美食清单...</div>
    <div v-else-if="filteredFoods.length === 0" class="status-card">当前筛选条件下暂无美食推荐，换个城市或菜系试试。</div>
    <div v-else class="content-split">
      <div class="card-grid">
        <article
          v-for="item in filteredFoods"
          :key="item.source_id"
          class="item-card media-card"
          :class="{ selected: selected?.source_id === item.source_id }"
          @click="select(item)"
        >
          <RealImage
            :src="item.image_url"
            :alt="item.name"
            :name="item.name"
            :search-hint="item.destination_name"
            :city="item.city"
            :latitude="item.latitude"
            :longitude="item.longitude"
            :source-url="item.source_url"
            class="media-thumb"
          />
          <div class="media-body">
            <h3>{{ item.name }}</h3>
            <p>{{ item.city }} · {{ item.cuisine }}</p>
            <p>{{ item.destination_name }}</p>
            <p>评分 {{ item.rating }} · 热度 {{ item.heat }}</p>
          </div>
        </article>
      </div>

      <section v-if="selected" class="detail-panel detail-stack">
        <RealImage
          :src="selected.image_url"
          :alt="selected.name"
          :name="selected.name"
          :search-hint="selected.destination_name"
          :city="selected.city"
          :latitude="selected.latitude"
          :longitude="selected.longitude"
          :source-url="selected.source_url"
          class="detail-image"
        />
        <div>
          <h3>{{ selected.name }}</h3>
          <p>{{ selected.city }} · {{ selected.cuisine }}</p>
          <p>{{ selected.description }}</p>
          <div class="detail-stats">
            <span class="stat-pill">评分 {{ selected.rating }}</span>
            <span class="stat-pill">热度 {{ selected.heat }}</span>
            <span class="stat-pill">{{ selected.destination_name }}</span>
          </div>
          <p class="detail-note">推荐地点：{{ selected.destination_name }}</p>
          <p class="detail-note">图片来源：{{ selected.image_source_name || "Wikipedia / OpenStreetMap" }}</p>
          <p class="detail-note">
            数据来源：
            <a :href="selected.source_url" target="_blank" rel="noreferrer">{{ selected.source_name }}</a>
          </p>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import RealImage from "../components/RealImage.vue";
import { useTravelStore } from "../stores/travel";

const store = useTravelStore();
const foods = computed(() => store.foods.items);
const selected = computed(() => store.foods.selected);
const loading = computed(() => store.foods.loading);
const error = computed(() => store.foods.error);
const lastUpdated = computed(() => store.foods.lastUpdated);

const cityFilter = ref("全部");
const cuisineFilter = ref("全部");
const destinationFilter = ref("全部");
const sortMode = ref("recommended");

const cities = computed(() => [...new Set(foods.value.map((item) => item.city).filter(Boolean))]);
const cuisines = computed(() => [...new Set(foods.value.map((item) => item.cuisine).filter(Boolean))]);
const destinations = computed(() => [...new Set(foods.value.map((item) => item.destination_name).filter(Boolean))]);

const filteredFoods = computed(() => {
  const items = foods.value.filter((item) => {
    const cityMatch = cityFilter.value === "全部" || item.city === cityFilter.value;
    const cuisineMatch = cuisineFilter.value === "全部" || item.cuisine === cuisineFilter.value;
    const destinationMatch = destinationFilter.value === "全部" || item.destination_name === destinationFilter.value;
    return cityMatch && cuisineMatch && destinationMatch;
  });
  const ranked = [...items];
  if (sortMode.value === "rating") {
    ranked.sort((left, right) => (right.rating ?? 0) - (left.rating ?? 0));
  } else if (sortMode.value === "heat") {
    ranked.sort((left, right) => (right.heat ?? 0) - (left.heat ?? 0));
  }
  return ranked;
});

const select = (item: any) => store.selectFood(item);
const load = (force = false) => store.loadFoods(force);

watch(filteredFoods, (items) => {
  if (!items.length) {
    store.selectFood(null);
    return;
  }
  if (!selected.value || !items.some((item) => item.source_id === selected.value?.source_id)) {
    store.selectFood(items[0]);
  }
});

onMounted(async () => {
  await load(false);
  if (filteredFoods.value.length) {
    store.selectFood(filteredFoods.value[0]);
  }
});
</script>
