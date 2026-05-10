<template>
  <div class="space-y-6">
    <!-- Header + filters -->
    <div class="bg-white rounded-3xl card-elevated p-6">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 class="text-xl font-bold text-gray-900">目的地推荐</h2>
          <p class="text-sm text-gray-500 mt-1">
            按城市、类别和热度快速筛选，挑出更适合当天行程的目的地。
          </p>
        </div>
        <button v-ripple class="btn-soft-primary text-sm" @click="load(true)">
          {{ loading ? "加载中..." : "刷新推荐" }}
        </button>
      </div>
      <!-- 已选筛选项标签流 -->
      <div v-if="selectedTags.length" class="flex flex-wrap gap-2 mt-4">
        <button
          v-for="tag in selectedTags"
          :key="tag.key"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary-50 text-primary-700 text-xs font-medium hover:bg-primary-100 transition-colors"
          @click="removeTag(tag.key)"
        >
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
      <div class="flex flex-wrap gap-3 mt-3">
        <select v-model="cityFilter" class="soft-control text-sm text-gray-700">
          <option value="全部">全部城市</option>
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>
        <select v-model="categoryFilter" class="soft-control text-sm text-gray-700">
          <option value="全部">全部类别</option>
          <option value="scenic">景点</option>
          <option value="shopping">商场/商圈</option>
          <option value="campus">高校/校园</option>
        </select>
        <select v-model="sortMode" class="soft-control text-sm text-gray-700">
          <option value="recommended">推荐优先</option>
          <option value="rating">评分降序</option>
          <option value="heat">热度降序</option>
        </select>
        <span v-if="lastUpdated" class="text-xs text-gray-400 self-center"
          >更新于 {{ lastUpdated }}</span
        >
      </div>
    </div>
    <!-- Status -->
    <div v-if="error" class="alert-soft-error">{{ error }}</div>
    <div v-else-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <SkeletonCard v-for="n in 6" :key="n" />
    </div>
    <EmptyState
      v-else-if="filteredDestinations.length === 0"
      title="暂无匹配结果"
      description="当前筛选条件下没有目的地，换个城市或类别试试。"
      action-hint="换个城市或类别？试试全部城市或景点"
    />
    <!-- Content -->
    <div v-else class="grid lg:grid-cols-[1.4fr_1fr] gap-6">
      <!-- Card list -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 stagger-children">
        <article
          v-for="item in filteredDestinations"
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
          <div class="relative h-36 bg-gray-100 overflow-hidden">
            <RealImage
              :src="item.image_url"
              :alt="item.name"
              :name="item.name"
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
              {{ categoryLabel(item.category) }} · {{ item.city }}
            </p>
            <p class="text-xs text-gray-400 mt-0.5 truncate">
              {{ item.district || item.address }}
            </p>
            <div class="flex gap-2 mt-2">
              <span
                class="text-xs px-2 py-0.5 rounded-full bg-primary-50 text-primary-600 font-medium"
                >{{ displayMetric(item.rating) }}</span
              >
              <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
                >热度 {{ displayMetric(item.heat) }}</span
              >
            </div>
          </div>
        </article>
      </div>
      <!-- Detail panel -->
      <div
        v-if="selected"
        class="bg-white rounded-3xl card-elevated p-5 sticky top-16 self-start space-y-4"
      >
        <RealImage
          :src="selected.image_url"
          :alt="selected.name"
          :name="selected.name"
          :city="selected.city"
          :latitude="selected.latitude"
          :longitude="selected.longitude"
          :source-url="selected.source_url"
          class="w-full h-56 object-cover rounded-2xl bg-gray-100"
        />
        <div>
          <h3 class="text-lg font-bold text-gray-900">{{ selected.name }}</h3>
          <p class="text-sm text-gray-500 mt-1">
            {{ categoryLabel(selected.category) }} · {{ selected.city }} ·
            {{ selected.district || "热门区域" }}
          </p>
          <p class="text-sm text-gray-500 mt-0.5">{{ selected.address }}</p>
          <p class="text-sm text-gray-600 mt-3 leading-relaxed">
            {{ selected.description }}
          </p>
          <div class="flex flex-wrap gap-2 mt-4">
            <span
              class="text-xs px-3 py-1.5 rounded-full bg-primary-50 text-primary-700 font-medium"
              >评分 {{ displayMetric(selected.rating) }}</span
            >
            <span class="text-xs px-3 py-1.5 rounded-full bg-accent-50 text-accent-600 font-medium"
              >热度 {{ displayMetric(selected.heat) }}</span
            >
            <span class="text-xs px-3 py-1.5 rounded-full bg-gray-100 text-gray-600">{{
              selected.heat_metric || "平台热度"
            }}</span>
          </div>
          <button
            class="mt-4 w-full text-sm"
            :class="
              isFavorite(selected.source_id)
                ? 'btn-soft-secondary text-primary-700 bg-primary-50'
                : 'btn-soft-primary'
            "
            v-ripple
            @click="toggleFavorite(selected.source_id)"
          >
            {{ isFavorite(selected.source_id) ? "已收藏，点击取消" : "收藏目的地" }}
          </button>
          <p class="text-xs text-gray-400 mt-3">
            数据来源：<a
              :href="selected.source_url"
              target="_blank"
              rel="noreferrer"
              class="text-primary-600 hover:underline"
              >{{ selected.source_name }}</a
            >
          </p>
          <p class="text-xs text-gray-400">
            图片来源：{{ selected.image_source_name || "Wikipedia / OpenStreetMap" }}
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
import { useAuthStore } from "../stores/auth";
import { useToastStore } from "../stores/toast";
import { useTravelStore } from "../stores/travel";
const store = useTravelStore();
const auth = useAuthStore();
const toast = useToastStore();
const cityFilter = ref("全部");
const categoryFilter = ref("全部");
const sortMode = ref("recommended");
const destinations = computed(() => store.destinations.items);
const selected = computed(() => store.destinations.selected);
const loading = computed(() => store.destinations.loading);
const error = computed(() => store.destinations.error);
const lastUpdated = computed(() => store.destinations.lastUpdated);
const cities = computed(() => [
  ...new Set(destinations.value.map((item) => item.city).filter(Boolean)),
]);
const displayMetric = (value: number | null | undefined) => value ?? "待补充";
const categoryLabel = (value: string) => {
  if (value === "shopping") return "商场/商圈";
  if (value === "campus") return "高校/校园";
  return "景点";
};
const filteredDestinations = computed(() => {
  const items = destinations.value.filter((item) => {
    const cityMatch = cityFilter.value === "全部" || item.city === cityFilter.value;
    const categoryMatch = categoryFilter.value === "全部" || item.category === categoryFilter.value;
    return cityMatch && categoryMatch;
  });
  const ranked = [...items];
  if (sortMode.value === "rating") {
    ranked.sort((left, right) => (right.rating ?? 0) - (left.rating ?? 0));
  } else if (sortMode.value === "heat") {
    ranked.sort((left, right) => (right.heat ?? 0) - (left.heat ?? 0));
  }
  return ranked;
});
const ensureSelection = () => {
  if (!filteredDestinations.value.length) {
    store.selectDestination(null);
    return;
  }
  if (
    !selected.value ||
    !filteredDestinations.value.some((item) => item.source_id === selected.value?.source_id)
  ) {
    store.selectDestination(filteredDestinations.value[0]);
  }
};
const select = (item: any) => store.selectDestination(item);
const load = (force = false) => store.loadFeaturedDestinations(force);
const isFavorite = (sourceId: string) => auth.user?.favorite_destination_ids?.includes(sourceId);
const toggleFavorite = async (sourceId: string) => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  await auth.toggleDestinationFavorite(sourceId);
  toast.success(isFavorite(sourceId) ? "已添加到收藏" : "已取消收藏");
};
const removeTag = (key: string) => {
  if (key === "city") cityFilter.value = "全部";
  if (key === "category") categoryFilter.value = "全部";
  if (key === "sort") sortMode.value = "recommended";
};
const selectedTags = computed(() => {
  const tags = [];
  if (cityFilter.value !== "全部") tags.push({ key: "city", label: `城市:${cityFilter.value}` });
  if (categoryFilter.value !== "全部")
    tags.push({ key: "category", label: `类别:${categoryFilter.value}` });
  if (sortMode.value !== "recommended") {
    const label = sortMode.value === "rating" ? "评分降序" : "热度降序";
    tags.push({ key: "sort", label });
  }
  return tags;
});
watch([filteredDestinations, selected], ensureSelection, { immediate: false });
onMounted(async () => {
  await load(false);
  ensureSelection();
});
</script>
