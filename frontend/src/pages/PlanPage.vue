<template>
  <div class="plan-page space-y-6">
    <section class="card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p class="home-section-kicker">行程规划</p>
          <h2 class="text-2xl font-bold text-slate-950 mt-1">旅游规划</h2>
          <p class="text-sm text-slate-500 mt-2 leading-7 max-w-3xl">
            以多日行程为单位安排每天的上午、下午和晚上，支持路线优化和附近美食补充，形成可保存的个性化计划。
          </p>
        </div>
        <button class="btn-soft-primary text-sm" @click="startCreate">
          {{ isEditing ? "取消新建" : "新建计划" }}
        </button>
      </div>
    </section>

    <div v-if="planStore.error" class="alert-soft-error flex items-center justify-between gap-3">
      <span>{{ planStore.error }}</span>
      <button class="text-sm font-bold opacity-60 hover:opacity-100" @click="planStore.error = ''">
        &times;
      </button>
    </div>

    <div class="grid xl:grid-cols-[320px_minmax(0,1fr)] gap-6 items-start">
      <aside class="card-elevated rounded-[24px] p-5 space-y-4">
        <div>
          <span class="route-panel-kicker">我的计划</span>
          <h3 class="text-lg font-bold text-slate-950 mt-1">已保存的行程</h3>
          <p class="text-sm text-slate-500 mt-2">
            左侧保留你已创建的旅游计划，右侧负责查看详情或编辑。
          </p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="route-metric-tile">
            <strong>{{ planStore.items.length }}</strong>
            <span>计划数量</span>
          </div>
          <div class="route-metric-tile">
            <strong>{{ selectedPlanDays }}</strong>
            <span>当前天数</span>
          </div>
        </div>

        <div v-if="planStore.loading" class="text-sm text-slate-500 text-center py-8">
          加载中...
        </div>
        <div
          v-else-if="planStore.items.length === 0"
          class="text-sm text-slate-400 text-center py-8"
        >
          暂无计划，点击右上角“新建计划”开始安排行程。
        </div>
        <div v-else class="space-y-3">
          <article
            v-for="plan in planStore.items"
            :key="plan.id"
            class="plan-list-card"
            :class="{ 'plan-list-card-active': planStore.selected?.id === plan.id && !isEditing }"
            @click="selectPlan(plan)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <h4 class="text-sm font-bold text-slate-900 truncate">{{ plan.title }}</h4>
                <p class="text-xs text-slate-500 mt-1">
                  {{ plan.days.length }} 天 · {{ plan.days[0]?.date }} ~
                  {{ plan.days[plan.days.length - 1]?.date }}
                </p>
              </div>
              <span class="route-summary-chip">{{ plan.days.length }} 天</span>
            </div>
            <p class="text-xs text-slate-400 mt-2 truncate">{{ plan.updated_at }}</p>
          </article>
        </div>
      </aside>

      <section class="space-y-5">
        <div
          v-if="!planStore.selected && !isEditing"
          class="card-elevated rounded-[24px] p-8 text-center"
        >
          <span class="route-panel-kicker">详情面板</span>
          <h3 class="text-lg font-bold text-slate-950 mt-2">先选择一个计划，或直接新建</h3>
          <p class="text-sm text-slate-500 leading-7 mt-3">
            右侧会展示当前计划的每日安排，进入编辑模式后可以调整日期、城市、景点、路线优化和美食补充。
          </p>
        </div>

        <template v-else-if="isEditing">
          <section class="card-elevated rounded-[24px] p-5 lg:p-6 space-y-5">
            <div class="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <span class="route-panel-kicker">编辑模式</span>
                <h3 class="text-xl font-bold text-slate-950 mt-1">
                  {{ editingPlan.id ? "编辑计划" : "新建计划" }}
                </h3>
              </div>
              <span class="route-summary-chip">
                {{ editingPlan.days.length ? `${editingPlan.days.length} 天行程` : "等待设置日期" }}
              </span>
            </div>

            <div>
              <label class="field-label">计划名称</label>
              <input
                v-model="editingPlan.title"
                class="soft-control w-full"
                placeholder="例如：北京三日游"
              />
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="field-label">开始日期</label>
                <input
                  v-model="startDate"
                  type="date"
                  class="soft-control w-full"
                  @change="generateDays"
                />
              </div>
              <div>
                <label class="field-label">结束日期</label>
                <input
                  v-model="endDate"
                  type="date"
                  class="soft-control w-full"
                  @change="generateDays"
                />
              </div>
            </div>
          </section>

          <section v-if="editingPlan.days.length" class="space-y-4">
            <article
              v-for="(day, dayIndex) in editingPlan.days"
              :key="dayIndex"
              class="card-elevated rounded-[24px] p-5 space-y-4"
            >
              <div class="flex items-center gap-3 flex-wrap">
                <span class="route-summary-chip">第 {{ dayIndex + 1 }} 天</span>
                <span class="text-sm text-slate-500">{{ day.date }}</span>
                <select
                  v-model="day.city"
                  class="soft-control text-sm ml-auto min-w-[140px]"
                  @change="onCityChange(day)"
                >
                  <option value="">选择城市</option>
                  <option v-for="city in availableCities" :key="city" :value="city">
                    {{ city }}
                  </option>
                </select>
              </div>

              <div
                v-if="optimizationResult[dayIndex]"
                class="text-xs text-emerald-700 bg-emerald-50 rounded-xl px-3 py-2"
              >
                路线已优化：{{ optimizationResult[dayIndex].label }}，总距离约
                {{ optimizationResult[dayIndex].total_distance_km }} km
              </div>

              <div class="space-y-3">
                <div v-for="slot in timeSlots" :key="slot.key" class="plan-slot-card">
                  <div class="plan-slot-row">
                    <span class="plan-slot-label" :class="slot.colorClass">{{ slot.label }}</span>
                    <select
                      v-model="day.time_slots[slot.key].destination_id"
                      class="soft-control flex-1 text-sm"
                      :disabled="!day.city"
                      @change="onDestinationChange(day, slot.key)"
                    >
                      <option value="">{{ day.city ? "暂不安排" : "先选城市" }}</option>
                      <option
                        v-for="dest in destinationsForCity(day.city)"
                        :key="dest.source_id"
                        :value="dest.source_id"
                      >
                        {{ dest.name }}
                      </option>
                    </select>
                    <input
                      v-if="day.city && day.time_slots[slot.key].destination_id"
                      v-model="day.time_slots[slot.key].notes"
                      class="soft-control flex-1 text-sm"
                      placeholder="备注，例如预约方式、集合点"
                    />
                  </div>

                  <div
                    v-if="day.time_slots[slot.key].destination_id"
                    class="flex items-center gap-2 pl-[5rem]"
                  >
                    <button
                      class="btn-soft-secondary text-[11px] px-3 py-1"
                      :disabled="loadingSlotFoods[`${dayIndex}-${slot.key}`]"
                      @click="toggleFoodsForSlot(dayIndex, slot.key)"
                    >
                      {{
                        loadingSlotFoods[`${dayIndex}-${slot.key}`]
                          ? "加载中..."
                          : slotFoods[`${dayIndex}-${slot.key}`]?.length
                            ? "收起美食"
                            : "附近美食"
                      }}
                    </button>
                    <button
                      class="btn-soft-secondary text-[11px] px-3 py-1"
                      @click="openFoodRecommendations(day.time_slots[slot.key])"
                    >
                      查看附近美食
                    </button>
                  </div>

                  <div
                    v-if="slotFoods[`${dayIndex}-${slot.key}`]?.length"
                    class="pl-[5rem] grid grid-cols-1 lg:grid-cols-2 gap-2"
                  >
                    <article
                      v-for="food in slotFoods[`${dayIndex}-${slot.key}`]"
                      :key="food.id || food.name"
                      class="plan-food-card"
                    >
                      <div class="min-w-0">
                        <p class="font-medium text-slate-800 truncate">{{ food.name }}</p>
                        <p class="text-xs text-slate-400">
                          {{ food.cuisine || "美食推荐" }} · 评分 {{ food.rating ?? "-" }} · 距离
                          {{ food.distance_km ?? "?" }} km
                        </p>
                      </div>
                      <button
                        class="text-[10px] px-2 py-1 rounded bg-primary-50 text-primary-700 hover:bg-primary-100 shrink-0"
                        @click="addFoodToSlot(dayIndex, food, slot.key)"
                      >
                        加入备注
                      </button>
                    </article>
                  </div>
                </div>
              </div>

              <div class="flex flex-wrap gap-2 pt-2 border-t border-slate-100">
                <button
                  class="btn-soft-primary text-xs"
                  :disabled="optimizing || getDayDestinationIds(day).length < 2"
                  @click="optimizeDayRoute(dayIndex)"
                >
                  {{ optimizing ? "优化中..." : "优化当天路线" }}
                </button>
              </div>
            </article>
          </section>

          <section class="card-elevated rounded-[24px] p-5">
            <div class="flex flex-wrap gap-3">
              <button class="btn-soft-primary" :disabled="saving" @click="savePlan">
                {{ saving ? "保存中..." : "保存计划" }}
              </button>
              <button class="btn-soft-secondary" @click="cancelEdit">取消</button>
            </div>
          </section>
        </template>

        <template v-else-if="planStore.selected">
          <section class="card-elevated rounded-[24px] p-5 lg:p-6 space-y-5">
            <div class="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <span class="route-panel-kicker">计划详情</span>
                <h3 class="text-xl font-bold text-slate-950 mt-1">
                  {{ planStore.selected.title }}
                </h3>
                <p class="text-sm text-slate-500 mt-2">
                  {{ planStore.selected.days.length }} 天行程 ·
                  {{ planStore.selected.days[0]?.date }} ~
                  {{ planStore.selected.days[planStore.selected.days.length - 1]?.date }}
                </p>
                <p class="text-xs text-slate-400 mt-1">
                  创建于 {{ planStore.selected.created_at }}
                </p>
              </div>
              <div class="flex flex-wrap gap-2">
                <button class="btn-soft-primary text-sm" @click="startEdit">编辑</button>
                <button class="btn-soft-secondary text-sm text-red-500" @click="deleteCurrentPlan">
                  删除
                </button>
              </div>
            </div>

            <div class="space-y-4">
              <article
                v-for="(day, dayIndex) in planStore.selected.days"
                :key="dayIndex"
                class="card-elevated rounded-[20px] p-4 space-y-3"
              >
                <div class="flex items-center gap-3 flex-wrap">
                  <span class="route-summary-chip">第 {{ dayIndex + 1 }} 天</span>
                  <span class="text-sm text-slate-500">{{ day.date }}</span>
                  <span
                    v-if="day.city"
                    class="route-summary-chip route-summary-chip-accent ml-auto"
                  >
                    {{ day.city }}
                  </span>
                </div>

                <div class="space-y-3">
                  <div v-for="slot in timeSlots" :key="slot.key" class="plan-slot-view">
                    <span class="plan-slot-label" :class="slot.colorClass">{{ slot.label }}</span>
                    <div v-if="day.time_slots[slot.key]?.destination_name" class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-slate-800">
                        {{ day.time_slots[slot.key]!.destination_name }}
                      </p>
                      <p v-if="day.time_slots[slot.key]!.notes" class="text-xs text-slate-400 mt-1">
                        {{ day.time_slots[slot.key]!.notes }}
                      </p>
                      <button
                        class="btn-soft-secondary text-[11px] px-3 py-1 mt-2"
                        @click="openFoodRecommendations(day.time_slots[slot.key])"
                      >
                        查看附近美食
                      </button>
                    </div>
                    <span v-else class="text-xs text-slate-300 italic">暂不安排</span>
                  </div>
                </div>
              </article>
            </div>
          </section>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from "vue";
import { useRouter } from "vue-router";

import { api } from "../api/client";
import { useAuthStore } from "../stores/auth";
import { usePlanStore } from "../stores/plans";
import { useTravelStore } from "../stores/travel";
import type { NearbyFoodResponse, OptimizeOrderResponse } from "../types/api";
import type { Destination, Food, TimeSlotEntry, TravelPlan } from "../types/models";

const auth = useAuthStore();
const planStore = usePlanStore();
const travelStore = useTravelStore();
const router = useRouter();

const isEditing = ref(false);
const saving = ref(false);
const optimizing = ref(false);
const startDate = ref("");
const endDate = ref("");

const slotFoods = ref<Record<string, Food[]>>({});
const loadingSlotFoods = ref<Record<string, boolean>>({});
const optimizationResult = ref<Record<number, { total_distance_km: number; label: string }>>({});

const timeSlots = [
  { key: "morning" as const, label: "上午", colorClass: "text-amber-600" },
  { key: "afternoon" as const, label: "下午", colorClass: "text-orange-600" },
  { key: "evening" as const, label: "晚上", colorClass: "text-purple-600" },
];

interface EditingDay {
  date: string;
  city: string;
  time_slots: {
    morning: TimeSlotEntry;
    afternoon: TimeSlotEntry;
    evening: TimeSlotEntry;
  };
}

const emptyTimeSlot = (): TimeSlotEntry => ({
  destination_id: "",
  destination_name: "",
  notes: "",
});

const editingPlan = reactive<{
  id: number | null;
  title: string;
  days: EditingDay[];
}>({
  id: null,
  title: "",
  days: [],
});

const availableCities = computed(() => {
  const cities = travelStore.destinations.items.map((d) => d.city).filter(Boolean) as string[];
  return [...new Set(cities)].sort();
});

const selectedPlanDays = computed(() => planStore.selected?.days.length ?? 0);

const destinationsForCity = (city: string) =>
  travelStore.destinations.items.filter((d) => d.city === city);

const makeDay = (date: string, city = ""): EditingDay => ({
  date,
  city,
  time_slots: {
    morning: emptyTimeSlot(),
    afternoon: emptyTimeSlot(),
    evening: emptyTimeSlot(),
  },
});

const generateDays = () => {
  if (!startDate.value || !endDate.value) return;

  const start = new Date(startDate.value);
  const end = new Date(endDate.value);
  if (start > end) return;

  const defaultCity = availableCities.value[0] ?? "";
  const days: EditingDay[] = [];
  const current = new Date(start);

  while (current <= end) {
    const dateStr = current.toISOString().split("T")[0];
    const existing = editingPlan.days.find((d) => d.date === dateStr);
    days.push(existing ?? makeDay(dateStr, defaultCity));
    current.setDate(current.getDate() + 1);
  }

  editingPlan.days = days;
};

const onCityChange = (day: EditingDay) => {
  day.time_slots.morning = emptyTimeSlot();
  day.time_slots.afternoon = emptyTimeSlot();
  day.time_slots.evening = emptyTimeSlot();
};

const onDestinationChange = (day: EditingDay, slotKey: "morning" | "afternoon" | "evening") => {
  const destId = day.time_slots[slotKey].destination_id;
  if (!destId) {
    day.time_slots[slotKey] = emptyTimeSlot();
    return;
  }

  const dest = travelStore.destinations.items.find((d) => d.source_id === destId);
  if (dest) {
    day.time_slots[slotKey] = {
      destination_id: dest.source_id,
      destination_name: dest.name,
      notes: day.time_slots[slotKey].notes,
    };
  }
};

const findDestinationForSlot = (
  entry: TimeSlotEntry | null | undefined,
): Destination | undefined => {
  if (!entry) return undefined;

  return travelStore.destinations.items.find(
    (destination) =>
      destination.source_id === entry.destination_id ||
      (entry.destination_name && destination.name === entry.destination_name),
  );
};

const hasDestinationCoordinates = (
  destination: Destination | undefined,
): destination is Destination =>
  typeof destination?.latitude === "number" &&
  Number.isFinite(destination.latitude) &&
  typeof destination.longitude === "number" &&
  Number.isFinite(destination.longitude);

const openFoodRecommendations = (entry: TimeSlotEntry | null | undefined) => {
  if (!entry?.destination_id && !entry?.destination_name) return;

  const destination = findDestinationForSlot(entry);
  const anchorName = destination?.name || entry.destination_name;
  if (!anchorName) return;

  const query: Record<string, string> = {
    anchorType: "destination",
    anchorId: destination?.source_id || entry.destination_id || `destination:${anchorName}`,
    anchorName,
    radius: "2",
    sort: "recommend",
  };

  if (hasDestinationCoordinates(destination)) {
    query.lat = String(destination.latitude);
    query.lng = String(destination.longitude);
  }

  void router.push({ path: "/foods", query });
};

const planToEditingPlan = (plan: TravelPlan) => {
  editingPlan.id = plan.id;
  editingPlan.title = plan.title;
  editingPlan.days = plan.days.map((d) => ({
    date: d.date,
    city: d.city || "",
    time_slots: {
      morning: d.time_slots.morning ?? emptyTimeSlot(),
      afternoon: d.time_slots.afternoon ?? emptyTimeSlot(),
      evening: d.time_slots.evening ?? emptyTimeSlot(),
    },
  }));

  if (plan.days.length > 0) {
    startDate.value = plan.days[0].date;
    endDate.value = plan.days[plan.days.length - 1]?.date ?? plan.days[0].date;
  }
};

const resetEditingState = () => {
  editingPlan.id = null;
  editingPlan.title = "";
  editingPlan.days = [];
  startDate.value = "";
  endDate.value = "";
  slotFoods.value = {};
  optimizationResult.value = {};
};

const startCreate = () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }

  isEditing.value = !isEditing.value;
  if (isEditing.value) {
    planStore.selected = null;
    resetEditingState();
  }
};

const startEdit = () => {
  if (!planStore.selected) return;
  isEditing.value = true;
  planToEditingPlan(planStore.selected);
};

const cancelEdit = () => {
  isEditing.value = false;
  resetEditingState();
};

const selectPlan = async (plan: TravelPlan) => {
  if (isEditing.value) return;
  await planStore.getPlan(plan.id);
};

const savePlan = async () => {
  if (!editingPlan.title.trim()) return;
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }

  saving.value = true;
  try {
    const payload = {
      title: editingPlan.title.trim(),
      days: editingPlan.days.map((d) => ({
        date: d.date,
        city: d.city,
        time_slots: {
          morning: d.time_slots.morning.destination_id
            ? {
                destination_id: d.time_slots.morning.destination_id,
                destination_name: d.time_slots.morning.destination_name,
                notes: d.time_slots.morning.notes,
              }
            : null,
          afternoon: d.time_slots.afternoon.destination_id
            ? {
                destination_id: d.time_slots.afternoon.destination_id,
                destination_name: d.time_slots.afternoon.destination_name,
                notes: d.time_slots.afternoon.notes,
              }
            : null,
          evening: d.time_slots.evening.destination_id
            ? {
                destination_id: d.time_slots.evening.destination_id,
                destination_name: d.time_slots.evening.destination_name,
                notes: d.time_slots.evening.notes,
              }
            : null,
        },
      })),
    };

    if (editingPlan.id) {
      await planStore.updatePlan(editingPlan.id, payload);
    } else {
      const created = await planStore.createPlan(payload);
      if (created) {
        planStore.selected = created;
      }
    }

    isEditing.value = false;
  } finally {
    saving.value = false;
  }
};

const deleteCurrentPlan = async () => {
  if (!planStore.selected) return;
  if (!confirm("确定要删除这个计划吗？")) return;
  await planStore.deletePlan(planStore.selected.id);
};

const getDayDestinationIds = (day: EditingDay): string[] => {
  const ids: string[] = [];
  for (const slot of ["morning", "afternoon", "evening"] as const) {
    const id = day.time_slots[slot].destination_id;
    if (id) ids.push(id);
  }
  return ids;
};

const optimizeDayRoute = async (dayIndex: number) => {
  const day = editingPlan.days[dayIndex];
  const ids = getDayDestinationIds(day);
  if (ids.length < 2) {
    alert("一天内至少选择 2 个目的地，才能优化路线。");
    return;
  }

  optimizing.value = true;
  try {
    const { data } = await api.post<OptimizeOrderResponse>("/routes/optimize-order", {
      destination_ids: ids,
    });

    const ordered = data.ordered_ids;
    for (let i = 0; i < ordered.length; i += 1) {
      const slotKey = (["morning", "afternoon", "evening"] as const)[i];
      const dest = travelStore.destinations.items.find((d) => d.source_id === ordered[i]);
      if (dest && slotKey) {
        day.time_slots[slotKey] = {
          destination_id: dest.source_id,
          destination_name: dest.name,
          notes: day.time_slots[slotKey]?.notes || "",
        };
      }
    }

    for (let i = ordered.length; i < 3; i += 1) {
      const slotKey = (["morning", "afternoon", "evening"] as const)[i];
      if (slotKey) day.time_slots[slotKey] = emptyTimeSlot();
    }

    optimizationResult.value[dayIndex] = {
      total_distance_km: data.total_distance_km,
      label: data.optimization_label,
    };
  } catch {
    alert("路线优化失败，请稍后重试。");
  } finally {
    optimizing.value = false;
  }
};

const loadFoodsForSlot = async (dayIndex: number, slotKey: "morning" | "afternoon" | "evening") => {
  const day = editingPlan.days[dayIndex];
  const id = day.time_slots[slotKey].destination_id;
  if (!id) return;

  const dest = travelStore.destinations.items.find((d) => d.source_id === id);
  if (!dest?.latitude || !dest?.longitude) return;

  const key = `${dayIndex}-${slotKey}`;
  loadingSlotFoods.value[key] = true;
  try {
    const { data } = await api.get<NearbyFoodResponse>("/foods", {
      params: { lat: dest.latitude, lng: dest.longitude, radius: 3, top_k: 6 },
    });
    slotFoods.value[key] = data.items;
  } catch {
    slotFoods.value[key] = [];
  } finally {
    loadingSlotFoods.value[key] = false;
  }
};

const toggleFoodsForSlot = (dayIndex: number, slotKey: "morning" | "afternoon" | "evening") => {
  const key = `${dayIndex}-${slotKey}`;
  if (slotFoods.value[key]?.length) {
    slotFoods.value[key] = [];
  } else {
    loadFoodsForSlot(dayIndex, slotKey);
  }
};

const addFoodToSlot = (
  dayIndex: number,
  food: Food,
  slotKey: "morning" | "afternoon" | "evening",
) => {
  const day = editingPlan.days[dayIndex];
  const current = day.time_slots[slotKey];
  const foodNote = `美食推荐：${food.name}，${food.cuisine || "附近餐饮"} · 评分 ${
    food.rating ?? "-"
  } · 距离 ${food.distance_km ?? "?"} km`;

  day.time_slots[slotKey] = {
    ...current,
    notes: current.notes ? `${current.notes}；${foodNote}` : foodNote,
  };
};

onMounted(async () => {
  await travelStore.loadFeaturedDestinations(false);
  if (auth.isLoggedIn) {
    await planStore.loadPlans();
  }
});

watch(
  () => auth.isLoggedIn,
  (loggedIn) => {
    if (loggedIn && planStore.items.length === 0 && !planStore.loading) {
      planStore.loadPlans();
    }
  },
);
</script>
