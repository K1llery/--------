<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="bg-white rounded-3xl card-elevated p-6">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 class="text-xl font-bold text-gray-900">旅游规划</h2>
          <p class="text-sm text-gray-500 mt-1">设计多日行程，安排每天的游览计划。</p>
        </div>
        <button class="btn-soft-primary text-sm" @click="startCreate">
          {{ isEditing ? "取消新建" : "新建计划" }}
        </button>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="planStore.error" class="alert-soft-error flex items-center justify-between gap-3">
      <span>{{ planStore.error }}</span>
      <button class="text-sm font-bold opacity-60 hover:opacity-100" @click="planStore.error = ''">
        &times;
      </button>
    </div>

    <!-- 主内容区：左侧计划列表 + 右侧详情/编辑器 -->
    <div class="grid lg:grid-cols-[340px_1fr] gap-6">
      <!-- 左侧：计划列表 -->
      <div class="bg-white rounded-3xl card-elevated p-5 space-y-4">
        <h3 class="text-base font-bold text-gray-900">我的计划</h3>

        <div v-if="planStore.loading" class="text-sm text-gray-500 text-center py-8">加载中...</div>
        <div
          v-else-if="planStore.items.length === 0"
          class="text-sm text-gray-400 text-center py-8"
        >
          暂无计划，点击上方"新建计划"开始
        </div>
        <div v-else class="space-y-3">
          <article
            v-for="plan in planStore.items"
            :key="plan.id"
            class="card-elevated p-4 cursor-pointer glow-border transition-all duration-200"
            :class="{ 'ring-2 ring-primary-300': planStore.selected?.id === plan.id && !isEditing }"
            @click="selectPlan(plan)"
          >
            <h4 class="text-sm font-bold text-gray-900">{{ plan.title }}</h4>
            <p class="text-xs text-gray-500 mt-1">
              {{ plan.days.length }} 天 · {{ plan.days[0]?.date }} ~
              {{ plan.days[plan.days.length - 1]?.date }}
            </p>
            <p class="text-xs text-gray-400 mt-0.5">{{ plan.updated_at }}</p>
          </article>
        </div>
      </div>

      <!-- 右侧：详情 / 编辑器 -->
      <div class="bg-white rounded-3xl card-elevated p-6 space-y-5">
        <!-- 未选中状态 -->
        <div v-if="!planStore.selected && !isEditing" class="text-center py-16">
          <p class="text-gray-400 text-sm">从左侧选择一个计划，或点击"新建计划"</p>
        </div>

        <!-- 编辑模式 -->
        <div v-else-if="isEditing" class="space-y-5">
          <div class="flex items-center justify-between">
            <h3 class="text-base font-bold text-gray-900">
              {{ editingPlan.id ? "编辑计划" : "新建计划" }}
            </h3>
          </div>

          <!-- 计划标题 -->
          <div>
            <label class="field-label">计划名称</label>
            <input
              v-model="editingPlan.title"
              class="soft-control w-full"
              placeholder="例如：北京三日游"
            />
          </div>

          <!-- 日期范围 -->
          <div class="grid grid-cols-2 gap-4">
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

          <!-- 每日行程 -->
          <div class="space-y-4">
            <div
              v-for="(day, dayIndex) in editingPlan.days"
              :key="dayIndex"
              class="card-elevated p-4 space-y-3"
            >
              <!-- 每天头部：第X天 + 日期 + 城市选择 -->
              <div class="flex items-center gap-3 flex-wrap">
                <span
                  class="px-2 py-0.5 rounded-full bg-primary-50 text-primary-700 text-xs font-bold"
                >
                  第 {{ dayIndex + 1 }} 天
                </span>
                <span class="text-gray-500 text-xs">{{ day.date }}</span>
                <select
                  v-model="day.city"
                  class="soft-control text-sm ml-auto min-w-[120px]"
                  @change="onCityChange(day)"
                >
                  <option value="">选择城市</option>
                  <option v-for="city in availableCities" :key="city" :value="city">
                    {{ city }}
                  </option>
                </select>
              </div>

              <!-- 路线优化提示 -->
              <div
                v-if="optimizationResult[dayIndex]"
                class="text-xs text-green-600 bg-green-50 rounded-lg px-3 py-2"
              >
                路线已优化：{{ optimizationResult[dayIndex].label }}，总距离约
                {{ optimizationResult[dayIndex].total_distance_km }} km
              </div>

              <!-- 三个时段 -->
              <div class="space-y-2">
                <div v-for="slot in timeSlots" :key="slot.key" class="space-y-2">
                  <div class="flex items-center gap-3">
                    <span class="text-xs font-medium w-16 shrink-0" :class="slot.colorClass">
                      {{ slot.label }}
                    </span>
                    <select
                      v-model="day.time_slots[slot.key].destination_id"
                      class="soft-control flex-1 text-sm"
                      :disabled="!day.city"
                      @change="onDestinationChange(day, slot.key)"
                    >
                      <option value="">{{ day.city ? "不安排" : "先选城市" }}</option>
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
                      placeholder="备注，如预约方式"
                    />
                  </div>

                  <!-- 时段美食推荐按钮 -->
                  <div
                    v-if="day.time_slots[slot.key].destination_id"
                    class="flex items-center gap-2 pl-20"
                  >
                    <button
                      class="btn-soft-secondary text-[10px] px-2 py-0.5"
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
                  </div>

                  <!-- 时段美食推荐面板 -->
                  <div v-if="slotFoods[`${dayIndex}-${slot.key}`]?.length" class="pl-20 space-y-2">
                    <p class="text-xs text-gray-500 font-medium">附近美食推荐</p>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <div
                        v-for="food in slotFoods[`${dayIndex}-${slot.key}`]"
                        :key="food.id || food.name"
                        class="card-elevated p-3 text-sm flex items-center justify-between gap-2"
                      >
                        <div class="min-w-0">
                          <p class="font-medium text-gray-800 truncate">{{ food.name }}</p>
                          <p class="text-xs text-gray-400">
                            {{ food.cuisine }} · 评分{{ food.rating ?? "-" }} · 距{{
                              food.distance_km ?? "?"
                            }}km
                          </p>
                        </div>
                        <button
                          class="text-[10px] px-1.5 py-0.5 rounded bg-primary-50 text-primary-700 hover:bg-primary-100 shrink-0"
                          @click="addFoodToSlot(dayIndex, food, slot.key)"
                        >
                          加入
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 路线优化按钮 -->
              <div class="flex flex-wrap gap-2 pt-2 border-t border-gray-100">
                <button
                  class="btn-soft-primary text-xs"
                  :disabled="optimizing || getDayDestinationIds(day).length < 2"
                  @click="optimizeDayRoute(dayIndex)"
                >
                  {{ optimizing ? "优化中..." : "优化路线" }}
                </button>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex flex-wrap gap-3">
            <button class="btn-soft-primary" :disabled="saving" @click="savePlan">
              {{ saving ? "保存中..." : "保存计划" }}
            </button>
            <button class="btn-soft-secondary" @click="cancelEdit">取消</button>
          </div>
        </div>

        <!-- 查看模式 -->
        <div v-else-if="planStore.selected" class="space-y-5">
          <div class="flex items-start justify-between gap-4">
            <div>
              <h3 class="text-lg font-bold text-gray-900">{{ planStore.selected.title }}</h3>
              <p class="text-xs text-gray-500 mt-1">
                {{ planStore.selected.days.length }} 天行程 ·
                {{ planStore.selected.days[0]?.date }} ~
                {{ planStore.selected.days[planStore.selected.days.length - 1]?.date }}
              </p>
              <p class="text-xs text-gray-400 mt-0.5">创建于 {{ planStore.selected.created_at }}</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <button class="btn-soft-primary text-sm" @click="startEdit">编辑</button>
              <button class="btn-soft-secondary text-sm text-red-500" @click="deleteCurrentPlan">
                删除
              </button>
            </div>
          </div>

          <!-- 每日行程展示 -->
          <div class="space-y-4">
            <div
              v-for="(day, dayIndex) in planStore.selected.days"
              :key="dayIndex"
              class="card-elevated p-4 space-y-3"
            >
              <div class="flex items-center gap-3">
                <span
                  class="px-2 py-0.5 rounded-full bg-primary-50 text-primary-700 text-xs font-bold"
                >
                  第 {{ dayIndex + 1 }} 天
                </span>
                <span class="text-gray-500 text-xs">{{ day.date }}</span>
                <span
                  v-if="day.city"
                  class="ml-auto text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600"
                >
                  {{ day.city }}
                </span>
              </div>

              <div class="space-y-2">
                <div v-for="slot in timeSlots" :key="slot.key" class="flex items-start gap-3">
                  <span class="text-xs font-medium w-16 shrink-0 pt-0.5" :class="slot.colorClass">
                    {{ slot.label }}
                  </span>
                  <div v-if="day.time_slots[slot.key]?.destination_name" class="flex-1">
                    <p class="text-sm font-medium text-gray-800">
                      {{ day.time_slots[slot.key]!.destination_name }}
                    </p>
                    <p v-if="day.time_slots[slot.key]!.notes" class="text-xs text-gray-400 mt-0.5">
                      {{ day.time_slots[slot.key]!.notes }}
                    </p>
                  </div>
                  <span v-else class="text-xs text-gray-300 italic">不安排</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useAuthStore } from "../stores/auth";
import { usePlanStore } from "../stores/plans";
import { useTravelStore } from "../stores/travel";
import { api } from "../api/client";
import type { TimeSlotEntry, TimeSlots, TravelPlan, Food } from "../types/models";
import type { NearbyFoodResponse, OptimizeOrderResponse } from "../types/api";

const auth = useAuthStore();
const planStore = usePlanStore();
const travelStore = useTravelStore();

const isEditing = ref(false);
const saving = ref(false);
const optimizing = ref(false);
const startDate = ref("");
const endDate = ref("");

// 美食推荐（按 dayIndex + slotKey 粒度）
const slotFoods = ref<Record<string, Food[]>>({});
const loadingSlotFoods = ref<Record<string, boolean>>({});

// 优化结果
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

const emptyTimeSlots = (): TimeSlots => ({
  morning: emptyTimeSlot(),
  afternoon: emptyTimeSlot(),
  evening: emptyTimeSlot(),
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

const destinationsForCity = (city: string) =>
  travelStore.destinations.items.filter((d) => d.city === city);

const makeDay = (date: string, city: string = ""): EditingDay => ({
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
    endDate.value = plan.days[plan.days.length - 1].date;
  }
};

const startCreate = () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  isEditing.value = !isEditing.value;
  if (isEditing.value) {
    planStore.selected = null;
    editingPlan.id = null;
    editingPlan.title = "";
    editingPlan.days = [];
    startDate.value = "";
    endDate.value = "";
  }
};

const startEdit = () => {
  if (!planStore.selected) return;
  isEditing.value = true;
  planToEditingPlan(planStore.selected);
};

const cancelEdit = () => {
  isEditing.value = false;
  editingPlan.id = null;
  editingPlan.title = "";
  editingPlan.days = [];
  startDate.value = "";
  endDate.value = "";
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

// 获取当天已选的所有目的地ID（有重复城市的情况，但目前设计是一天一城）
const getDayDestinationIds = (day: EditingDay): string[] => {
  const ids: string[] = [];
  for (const slot of ["morning", "afternoon", "evening"] as const) {
    const id = day.time_slots[slot].destination_id;
    if (id) ids.push(id);
  }
  return ids;
};

// 路线优化
const optimizeDayRoute = async (dayIndex: number) => {
  const day = editingPlan.days[dayIndex];
  const ids = getDayDestinationIds(day);
  if (ids.length < 2) {
    alert("一天内至少选择2个景点才能优化路线");
    return;
  }
  optimizing.value = true;
  try {
    const { data } = await api.post<OptimizeOrderResponse>("/routes/optimize-order", {
      destination_ids: ids,
    });
    // 按返回顺序重新排列
    const ordered = data.ordered_ids;
    for (let i = 0; i < ordered.length; i++) {
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
    // 清空多余slot
    for (let i = ordered.length; i < 3; i++) {
      const slotKey = (["morning", "afternoon", "evening"] as const)[i];
      if (slotKey) day.time_slots[slotKey] = emptyTimeSlot();
    }
    optimizationResult.value[dayIndex] = {
      total_distance_km: data.total_distance_km,
      label: data.optimization_label,
    };
  } catch {
    alert("路线优化失败，请稍后重试");
  } finally {
    optimizing.value = false;
  }
};

// 加载某个时段附近美食
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

// 切换美食推荐面板的显示/隐藏
const toggleFoodsForSlot = (dayIndex: number, slotKey: "morning" | "afternoon" | "evening") => {
  const key = `${dayIndex}-${slotKey}`;
  if (slotFoods.value[key]?.length) {
    slotFoods.value[key] = [];
  } else {
    loadFoodsForSlot(dayIndex, slotKey);
  }
};

// 将美食加入时段（保留景点信息，在备注中追加美食）
const addFoodToSlot = (
  dayIndex: number,
  food: Food,
  slotKey: "morning" | "afternoon" | "evening",
) => {
  const day = editingPlan.days[dayIndex];
  const current = day.time_slots[slotKey];
  const foodNote = `美食推荐：${food.name}（${food.cuisine || ""} · 评分${food.rating ?? "-"} · 距${food.distance_km ?? "?"}km）`;
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

// 监听登录态变化：session 恢复后自动加载计划，刷新页面后不丢失
watch(
  () => auth.isLoggedIn,
  (loggedIn) => {
    if (loggedIn && planStore.items.length === 0 && !planStore.loading) {
      planStore.loadPlans();
    }
  },
);
</script>
