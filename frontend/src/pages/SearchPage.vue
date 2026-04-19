<template>
  <section class="panel-card">
    <div class="section-top">
      <div>
        <h2>搜索目的地</h2>
        <p>支持名称搜索，并按城市和类别进一步缩小范围。</p>
      </div>
    </div>

    <form class="search-form" @submit.prevent="search">
      <input v-model="query" placeholder="搜索景点、高校、商圈名称" />
      <select v-model="cityFilter" class="select-input">
        <option value="全部">全部城市</option>
        <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
      </select>
      <select v-model="categoryFilter" class="select-input">
        <option value="全部">全部类别</option>
        <option value="scenic">景点</option>
        <option value="shopping">商场/商圈</option>
        <option value="campus">高校/校园</option>
      </select>
      <button class="primary-btn" type="submit">{{ loading ? "搜索中..." : "搜索" }}</button>
    </form>

    <div v-if="error" class="status-card error-card">{{ error }}</div>
    <div v-else-if="loading" class="status-card">正在查找匹配目的地...</div>
    <div v-else-if="!displayResults.length" class="status-card">
      暂时没有找到匹配结果，可以试试更短的关键词或切换城市。
    </div>
    <div v-else class="content-split">
      <div class="results-stack">
        <section v-if="exactResults.length" class="results-section">
          <div class="section-top compact">
            <h3>精确匹配</h3>
            <span class="toolbar-hint">{{ exactResults.length }} 条</span>
          </div>
          <div class="card-grid compact-grid">
            <article
              v-for="item in exactResults"
              :key="`exact-${item.source_id}`"
              class="item-card media-card"
              :class="{ selected: selected?.source_id === item.source_id }"
              @click="selected = item"
            >
              <RealImage
                :src="item.image_url"
                :alt="item.name"
                :name="item.name"
                :city="item.city"
                :latitude="item.latitude"
                :longitude="item.longitude"
                :source-url="item.source_url"
                class="media-thumb small-thumb"
              />
              <div class="media-body">
                <h3>{{ item.name }}</h3>
                <p>{{ categoryLabel(item.category) }} · {{ item.city }}</p>
                <p>评分 {{ displayMetric(item.rating) }} · 热度 {{ displayMetric(item.heat) }}</p>
              </div>
            </article>
          </div>
        </section>

        <section class="results-section">
          <div class="section-top compact">
            <h3>相关结果</h3>
            <span class="toolbar-hint">{{ fuzzyResults.length }} 条</span>
          </div>
          <div class="card-grid compact-grid">
            <article
              v-for="item in fuzzyResults"
              :key="`fuzzy-${item.source_id}`"
              class="item-card media-card"
              :class="{ selected: selected?.source_id === item.source_id }"
              @click="selected = item"
            >
              <RealImage
                :src="item.image_url"
                :alt="item.name"
                :name="item.name"
                :city="item.city"
                :latitude="item.latitude"
                :longitude="item.longitude"
                :source-url="item.source_url"
                class="media-thumb small-thumb"
              />
              <div class="media-body">
                <h3>{{ item.name }}</h3>
                <p>{{ categoryLabel(item.category) }} · {{ item.city || "北京" }}</p>
                <p>评分 {{ displayMetric(item.rating) }} · 热度 {{ displayMetric(item.heat) }}</p>
              </div>
            </article>
          </div>
        </section>
      </div>

      <section v-if="selected" class="detail-panel detail-stack">
        <RealImage
          :src="selected.image_url"
          :alt="selected.name"
          :name="selected.name"
          :city="selected.city"
          :latitude="selected.latitude"
          :longitude="selected.longitude"
          :source-url="selected.source_url"
          class="detail-image"
        />
        <div>
          <h3>{{ selected.name }}</h3>
          <p>{{ categoryLabel(selected.category) }} · {{ selected.city || "北京" }}</p>
          <p>{{ selected.address || "地址待补充" }}</p>
          <p>{{ selected.description || "这是一个值得进一步探索的城市目的地。" }}</p>
          <div class="detail-stats">
            <span class="stat-pill">评分 {{ displayMetric(selected.rating) }}</span>
            <span class="stat-pill">热度 {{ displayMetric(selected.heat) }}</span>
          </div>
          <p class="detail-note" v-if="selected.source_url">
            数据来源：
            <a :href="selected.source_url" target="_blank" rel="noreferrer">{{ selected.source_name || "公开来源" }}</a>
          </p>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { api } from "../api/client";
import RealImage from "../components/RealImage.vue";
import { useTravelStore } from "../stores/travel";

const store = useTravelStore();
const query = ref("外滩");
const cityFilter = ref("全部");
const categoryFilter = ref("全部");
const loading = ref(false);
const error = ref("");

const exactRaw = ref<any[]>([]);
const fuzzyRaw = ref<any[]>([]);
const selected = ref<any | null>(null);
const cities = ["北京", "上海", "广州", "深圳"];

const categoryLabel = (value: string) => {
  if (value === "shopping") return "商场/商圈";
  if (value === "campus") return "高校/校园";
  return "景点";
};

const displayMetric = (value: number | null | undefined) => value ?? "待补充";

const filtered = (items: any[]) =>
  items.filter((item) => {
    const cityMatch = cityFilter.value === "全部" || item.city === cityFilter.value;
    const categoryMatch = categoryFilter.value === "全部" || item.category === categoryFilter.value;
    return cityMatch && categoryMatch;
  });

const exactResults = computed(() => filtered(exactRaw.value));
const fuzzyResults = computed(() => filtered(fuzzyRaw.value));
const displayResults = computed(() => [...exactResults.value, ...fuzzyResults.value]);

const uniqueMerge = (...groups: any[][]) => {
  const seen = new Set<string>();
  return groups.flat().filter((item) => {
    const key = item.source_id || item.name;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
};

const search = async () => {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await api.post("/destinations/search", {
      query: query.value,
      keywords: query.value.split(/\s+/).filter(Boolean),
      category: categoryFilter.value === "全部" ? null : categoryFilter.value
    });
    exactRaw.value = data.exact ? [data.exact] : [];
    fuzzyRaw.value = uniqueMerge(data.fuzzy ?? [], data.featured ?? []);
    selected.value = exactRaw.value[0] ?? fuzzyRaw.value[0] ?? null;
  } catch (searchError) {
    error.value = "搜索失败，请稍后再试。";
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await store.loadFeaturedDestinations(false);
  await search();
});
</script>
