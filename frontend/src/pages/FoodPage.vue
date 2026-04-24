<template>
  <div class="space-y-6">
    <div class="bg-white rounded-3xl card-elevated p-6">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 class="text-xl font-bold text-gray-900">美食推荐</h2>
          <p class="text-sm text-gray-500 mt-1">
            从城市特色餐厅到景点周边高评分选择，快速筛出这一顿该去哪里。
          </p>
        </div>
        <button v-ripple class="btn-soft-primary text-sm" @click="load(true)">
          {{ loading ? "加载中..." : "刷新推荐" }}
        </button>
      </div>
      <div class="flex flex-wrap gap-3 mt-5">
        <select v-model="cityFilter" class="soft-control text-sm text-gray-700">
          <option value="全部">全部城市</option>
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>
        <select
          v-model="cuisineFilter"
          class="soft-control text-sm text-gray-700"
        >
          <option value="全部">全部菜系</option>
          <option v-for="cuisine in cuisines" :key="cuisine" :value="cuisine">
            {{ cuisine }}
          </option>
        </select>
        <select
          v-model="destinationFilter"
          class="soft-control text-sm text-gray-700"
        >
          <option value="全部">全部关联目的地</option>
          <option
            v-for="destination in destinations"
            :key="destination"
            :value="destination"
          >
            {{ destination }}
          </option>
        </select>
        <select v-model="sortMode" class="soft-control text-sm text-gray-700">
          <option value="recommended">推荐优先</option>
          <option value="rating">评分优先</option>
          <option value="heat">热度优先</option>
        </select>
        <span v-if="lastUpdated" class="text-xs text-gray-400 self-center"
          >更新于 {{ lastUpdated }}</span
        >
      </div>
    </div>
    <div v-if="error" class="alert-soft-error">{{ error }}</div>
    <div
      v-else-if="loading"
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <SkeletonCard v-for="n in 6" :key="n" />
    </div>
    <EmptyState
      v-else-if="filteredFoods.length === 0"
      title="暂无美食推荐"
      description="当前筛选条件下没有结果，换个城市或菜系试试。"
    />
    <div v-else class="grid lg:grid-cols-[1.4fr_1fr] gap-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
        <article
          v-for="item in filteredFoods"
          :key="item.source_id"
          v-tilt
          class="group rounded-2xl bg-white overflow-hidden cursor-pointer glow-border shadow-md shadow-gray-200/50 transition-all duration-300"
          :class="
            selected?.source_id === item.source_id
              ? ' shadow-md shadow-primary-500/10 ring-1 ring-primary-200'
              : ' '
          "
          @click="select(item)"
        >
          <div class="h-36 bg-gray-100 overflow-hidden">
            <RealImage
              :src="item.image_url"
              :alt="item.name"
              :name="item.name"
              :search-hint="item.destination_name"
              :city="item.city"
              :latitude="item.latitude"
              :longitude="item.longitude"
              :source-url="item.source_url"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          </div>
          <div class="p-3.5">
            <h3 class="font-semibold text-gray-900 text-sm">{{ item.name }}</h3>
            <p class="text-xs text-gray-500 mt-1">
              {{ item.city }} · {{ item.cuisine }}
            </p>
            <p class="text-xs text-gray-400 mt-0.5 truncate">
              {{ item.destination_name }}
            </p>
            <div class="flex gap-2 mt-2">
              <span
                class="text-xs px-2 py-0.5 rounded-full bg-primary-50 text-primary-600 font-medium"
                >{{ item.rating }}</span
              >
              <span
                class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
                >热度 {{ item.heat }}</span
              >
            </div>
          </div>
        </article>
      </div>
      <div
        v-if="selected"
        class="bg-white rounded-3xl card-elevated p-5 sticky top-16 self-start space-y-4"
      >
        <RealImage
          :src="selected.image_url"
          :alt="selected.name"
          :name="selected.name"
          :search-hint="selected.destination_name"
          :city="selected.city"
          :latitude="selected.latitude"
          :longitude="selected.longitude"
          :source-url="selected.source_url"
          class="w-full h-56 object-cover rounded-2xl bg-gray-100"
        />
        <div>
          <h3 class="text-lg font-bold text-gray-900">{{ selected.name }}</h3>
          <p class="text-sm text-gray-500 mt-1">
            {{ selected.city }} · {{ selected.cuisine }}
          </p>
          <p class="text-sm text-gray-600 mt-3 leading-relaxed">
            {{ selected.description }}
          </p>
          <div class="flex flex-wrap gap-2 mt-4">
            <span
              class="text-xs px-3 py-1.5 rounded-full bg-primary-50 text-primary-700 font-medium"
              >评分 {{ selected.rating }}</span
            >
            <span
              class="text-xs px-3 py-1.5 rounded-full bg-accent-50 text-accent-600 font-medium"
              >热度 {{ selected.heat }}</span
            >
            <span
              class="text-xs px-3 py-1.5 rounded-full bg-gray-100 text-gray-600"
              >{{ selected.destination_name }}</span
            >
          </div>
          <p class="text-xs text-gray-400 mt-3">
            推荐地点：{{ selected.destination_name }}
          </p>
          <p class="text-xs text-gray-400">
            图片来源：{{
              selected.image_source_name || "Wikipedia / OpenStreetMap"
            }}
          </p>
          <p class="text-xs text-gray-400">
            数据来源：<a
              :href="selected.source_url"
              target="_blank"
              rel="noreferrer"
              class="text-primary-600 hover:underline"
              >{{ selected.source_name }}</a
            >
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import EmptyState from "../components/EmptyState.vue";
import RealImage from "../components/RealImage.vue";
import SkeletonCard from "../components/SkeletonCard.vue";
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
const cities = computed(() => [
  ...new Set(foods.value.map((item) => item.city).filter(Boolean)),
]);
const cuisines = computed(() => [
  ...new Set(foods.value.map((item) => item.cuisine).filter(Boolean)),
]);
const destinations = computed(() => [
  ...new Set(foods.value.map((item) => item.destination_name).filter(Boolean)),
]);
const filteredFoods = computed(() => {
  const items = foods.value.filter((item) => {
    const cityMatch =
      cityFilter.value === "全部" || item.city === cityFilter.value;
    const cuisineMatch =
      cuisineFilter.value === "全部" || item.cuisine === cuisineFilter.value;
    const destinationMatch =
      destinationFilter.value === "全部" ||
      item.destination_name === destinationFilter.value;
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
  if (
    !selected.value ||
    !items.some((item) => item.source_id === selected.value?.source_id)
  ) {
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
