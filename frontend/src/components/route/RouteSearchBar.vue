<template>
  <div class="route-search-bar">
    <div class="search-input-row">
      <span class="search-icon">🔍</span>
      <input
        ref="inputRef"
        v-model="query"
        class="search-input"
        type="text"
        :placeholder="placeholderText"
        @focus="open = true"
        @input="open = true"
        @keydown.enter.prevent="handleEnter"
        @keydown.down.prevent="moveActive(1)"
        @keydown.up.prevent="moveActive(-1)"
        @keydown.escape="open = false"
      />
      <button
        v-if="query"
        type="button"
        class="search-clear"
        aria-label="清空"
        @click="clearQuery"
      >
        ✕
      </button>
      <div class="search-actions">
        <button
          type="button"
          class="search-action-btn"
          :class="{ active: useCurrentLocation }"
          title="使用我的位置作为起点"
          @click="emit('toggle-current-location')"
        >
          📍 我的位置
        </button>
        <button
          type="button"
          class="search-action-btn"
          title="多点路线"
          @click="emit('open-multi-stop')"
        >
          行程
        </button>
        <button
          type="button"
          class="search-action-btn"
          title="按时长推荐路线"
          @click="emit('open-recommend')"
        >
          随便逛逛
        </button>
      </div>
    </div>

    <Transition name="page-fade-slide">
      <div v-if="open && suggestions.length" class="search-suggestions">
        <div
          v-for="(item, idx) in suggestions"
          :key="`sug-${item.code}`"
          class="search-suggestion"
          :class="{ active: idx === activeIdx }"
          @mouseenter="activeIdx = idx"
        >
          <button type="button" class="suggestion-main" @click="pickSuggestion(item)">
            <span class="suggestion-icon">{{ iconFor(item) }}</span>
            <span class="suggestion-name">{{ item.name }}</span>
            <span class="suggestion-tag">{{ tagFor(item) }}</span>
          </button>
          <button
            type="button"
            class="suggestion-add"
            :disabled="tripStopCodes.includes(item.code)"
            @click.stop="addToTrip(item)"
          >
            {{ tripStopCodes.includes(item.code) ? "已加入" : "加入" }}
          </button>
        </div>
      </div>
    </Transition>

    <Transition name="page-fade-slide">
      <div v-if="open && !suggestions.length && query" class="search-suggestions empty">
        无匹配地点。试试搜索 "图书馆"、"食堂"、"教学楼"。
      </div>
    </Transition>

    <div v-if="originHint" class="search-origin-hint">
      起点：<strong>{{ originHint }}</strong>
      <button class="origin-change-btn" type="button" @click="emit('open-origin-picker')">
        更换
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import type { Facility, SceneNode } from "../../types/models";

interface SearchablePlace extends SceneNode {
  __kind?: "node" | "facility";
  facility_label?: string;
  facility_type?: string;
}

const props = withDefaults(defineProps<{
  nodes: SceneNode[];
  facilities: Facility[];
  useCurrentLocation: boolean;
  originName?: string;
  tripStopCodes?: string[];
}>(), {
  tripStopCodes: () => [],
});

const emit = defineEmits<{
  "select-destination": [code: string];
  "toggle-current-location": [];
  "open-multi-stop": [];
  "open-recommend": [];
  "open-origin-picker": [];
  "add-destination-to-trip": [code: string];
}>();

const query = ref("");
const open = ref(false);
const activeIdx = ref(0);
const inputRef = ref<HTMLInputElement | null>(null);

const placeholderText = "你想去哪里？搜索地点、设施、教学楼…";

const allPlaces = computed<SearchablePlace[]>(() => {
  const list: SearchablePlace[] = [];
  for (const n of props.nodes) {
    if (n.route_node_type === "road") continue;
    list.push({ ...n, __kind: "node" });
  }
  for (const f of props.facilities) {
    list.push({
      code: f.code,
      name: f.name,
      latitude: f.latitude,
      longitude: f.longitude,
      __kind: "facility",
      facility_label: f.facility_label,
      facility_type: f.facility_type,
    });
  }
  // Deduplicate by code
  const map = new Map<string, SearchablePlace>();
  for (const p of list) {
    if (!map.has(p.code)) map.set(p.code, p);
  }
  return [...map.values()];
});

const suggestions = computed<SearchablePlace[]>(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) {
    // No query → show first 8 places (popular highlights)
    return allPlaces.value.slice(0, 8);
  }
  return allPlaces.value
    .filter((p) => {
      if (p.name.toLowerCase().includes(q)) return true;
      if (p.facility_label?.toLowerCase().includes(q)) return true;
      // simple pinyin first-letter match: only triggers if q is all latin
      if (/^[a-z]+$/.test(q)) {
        // crude: look for any node whose name starts with similar letter pattern (no real pinyin lib here)
        return false;
      }
      return false;
    })
    .slice(0, 12);
});

const originHint = computed(() => {
  if (props.useCurrentLocation) return "我的位置（自动定位）";
  return props.originName || "";
});

watch(suggestions, () => {
  activeIdx.value = 0;
});

const moveActive = (delta: number) => {
  if (!suggestions.value.length) return;
  activeIdx.value =
    (activeIdx.value + delta + suggestions.value.length) % suggestions.value.length;
};

const handleEnter = () => {
  if (suggestions.value.length) {
    pickSuggestion(suggestions.value[activeIdx.value]);
  }
};

const pickSuggestion = (item: SearchablePlace) => {
  query.value = item.name;
  open.value = false;
  emit("select-destination", item.code);
};

const addToTrip = (item: SearchablePlace) => {
  query.value = "";
  open.value = false;
  emit("add-destination-to-trip", item.code);
};

const clearQuery = () => {
  query.value = "";
  inputRef.value?.focus();
  open.value = true;
};

const iconFor = (item: SearchablePlace) => {
  if (item.__kind === "facility") {
    const t = item.facility_type;
    if (t === "restroom") return "🚻";
    if (t === "restaurant") return "🍽️";
    if (t === "supermarket") return "🛒";
    if (t === "service") return "☕";
    if (t === "shop") return "🏪";
    if (t === "sports") return "🏃";
    return "📍";
  }
  return "🏛️";
};

const tagFor = (item: SearchablePlace) => {
  if (item.__kind === "facility") return item.facility_label || "设施";
  return "地点";
};

const handleClickOutside = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  if (!target.closest(".route-search-bar")) {
    open.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});
onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});

defineExpose({
  focus: () => inputRef.value?.focus(),
  setQuery: (v: string) => {
    query.value = v;
  },
});
</script>
