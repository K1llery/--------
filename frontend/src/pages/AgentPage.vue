<template>
  <div class="space-y-6">
    <!-- ============ HERO ============ -->
    <section
      class="relative soft-surface rounded-3xl card-elevated overflow-hidden p-6 lg:p-8"
    >
      <div class="gradient-blob w-60 h-60 bg-primary-400 -top-16 -right-10" />
      <div class="flex items-start justify-between gap-6 flex-wrap">
        <div class="max-w-2xl">
          <span
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/80 backdrop-blur-sm text-primary-700 text-xs font-semibold border-0 shadow-md shadow-gray-200/50 shadow-sm shadow-primary-500/5 mb-3"
          >
            <svg
              class="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z"
              />
            </svg>
            Multi-Agent Collaboration
          </span>
          <h2
            class="text-2xl lg:text-3xl font-bold text-gray-900 leading-tight"
          >
            智能体协作展示
          </h2>
          <p class="text-sm text-gray-500 mt-2">
            课程要求中的任务分解、文档辅助与并行协作流程一览。
          </p>
        </div>
        <button
          v-ripple
          :disabled="loading"
          class="btn-soft-primary inline-flex items-center gap-2 text-sm disabled:opacity-70"
          @click="load"
        >
          <svg
            v-if="loading"
            class="w-4 h-4 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v8z"
            />
          </svg>
          <svg
            v-else
            class="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"
            />
          </svg>
          {{ hasData ? "重新加载" : "加载智能体说明" }}
        </button>
      </div>
    </section>
    <!-- Loading skeleton -->
    <div
      v-if="loading && !hasData"
      class="grid grid-cols-1 lg:grid-cols-2 gap-6"
    >
      <div
        class="bg-white rounded-2xl border-0 shadow-md shadow-gray-200/50 p-6 space-y-3 animate-pulse"
      >
        <div class="h-5 w-40 bg-gray-200 rounded-md" />
        <div class="h-3 w-60 bg-gray-100 rounded-md" />
        <div class="grid grid-cols-2 gap-3 pt-3">
          <div v-for="n in 4" :key="n" class="h-14 bg-gray-100 rounded-2xl" />
        </div>
      </div>
      <div
        class="bg-white rounded-2xl border-0 shadow-md shadow-gray-200/50 p-6 space-y-3 animate-pulse"
      >
        <div class="h-5 w-32 bg-gray-200 rounded-md" />
        <div class="h-3 w-48 bg-gray-100 rounded-md" />
        <div class="space-y-2 pt-3">
          <div v-for="n in 3" :key="n" class="h-10 bg-gray-100 rounded-2xl" />
        </div>
      </div>
    </div>
    <!-- Content -->
    <div v-if="hasData" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Knowledge agents -->
      <article
        v-if="knowledgeAgents.length"
        class="bg-white rounded-3xl card-elevated overflow-hidden"
      >
        <div
          class="flex items-center gap-3 p-5 lg:p-6 border-0 shadow-md shadow-gray-200/50"
        >
          <div
            class="w-11 h-11 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 text-white flex items-center justify-center shadow-lg shadow-primary-500/25"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.8"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18"
              />
            </svg>
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="text-base font-bold text-gray-900">知识型智能体</h3>
            <p class="text-xs text-gray-500 mt-0.5">
              共 {{ knowledgeAgents.length }} 位 · 按工种分工协作
            </p>
          </div>
        </div>
        <div
          class="p-5 lg:p-6 grid grid-cols-1 sm:grid-cols-2 gap-3 stagger-children"
        >
          <div
            v-for="(name, idx) in knowledgeAgents"
            :key="name"
            v-tilt
            class="group relative p-4 rounded-2xl border-0 shadow-md shadow-gray-200/50 bg-gradient-to-br from-white to-gray-50 hover:shadow-md hover:shadow-primary-500/10 transition-all"
          >
            <div class="flex items-start gap-3">
              <div
                class="w-9 h-9 rounded-2xl flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-sm"
                :class="knowledgeAgentStyle(idx)"
              >
                {{ nameInitial(name) }}
              </div>
              <div class="min-w-0">
                <h4 class="text-sm font-semibold text-gray-900 leading-tight">
                  {{ name }}
                </h4>
                <p class="text-[11px] text-gray-500 mt-1 leading-relaxed">
                  {{ roleHint(name) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </article>
      <!-- Collaboration flow -->
      <article
        v-if="collaborationFlow.length"
        class="bg-white rounded-3xl card-elevated overflow-hidden"
      >
        <div
          class="flex items-center gap-3 p-5 lg:p-6 border-0 shadow-md shadow-gray-200/50"
        >
          <div
            class="w-11 h-11 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white flex items-center justify-center shadow-lg shadow-emerald-500/25"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.8"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z"
              />
            </svg>
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="text-base font-bold text-gray-900">协作流程</h3>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ collaborationFlow.length }} 步 · 从需求到验收
            </p>
          </div>
        </div>
        <ol class="p-5 lg:p-6 space-y-3">
          <li
            v-for="(step, idx) in collaborationFlow"
            :key="`step-${idx}`"
            class="flex gap-3 items-start p-3 rounded-2xl bg-gradient-to-br from-gray-50 to-white border-0 shadow-md shadow-gray-200/50"
          >
            <div
              class="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 shadow-sm"
            >
              {{ idx + 1 }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm text-gray-700 leading-relaxed">{{ step }}</p>
            </div>
          </li>
        </ol>
      </article>
      <!-- Extra sections (for future fields) -->
      <article
        v-for="[key, values] in extraSections"
        :key="key"
        class="bg-white rounded-3xl card-elevated overflow-hidden lg:col-span-2"
      >
        <div
          class="flex items-center gap-3 p-5 border-0 shadow-md shadow-gray-200/50"
        >
          <div
            class="w-10 h-10 rounded-2xl bg-gradient-to-br from-slate-500 to-slate-700 text-white flex items-center justify-center"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.8"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M6 20.25h12m-7.5-3v3m3-3v3m-10.125-3h17.25c.621 0 1.125-.504 1.125-1.125V4.875c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125Z"
              />
            </svg>
          </div>
          <h3 class="text-base font-bold text-gray-900">
            {{ formatKey(key) }}
          </h3>
        </div>
        <ul class="p-5 grid gap-2 grid-cols-1 sm:grid-cols-2">
          <li
            v-for="(item, idx) in values"
            :key="`${key}-${idx}`"
            class="flex items-start gap-2 p-3 rounded-2xl bg-gray-50/70 border-0 shadow-md shadow-gray-200/50 text-sm text-gray-700"
          >
            <svg
              class="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 12 12"
            >
              <circle cx="6" cy="6" r="3" />
            </svg>
            {{ item }}
          </li>
        </ul>
      </article>
    </div>
    <!-- Empty -->
    <div
      v-else-if="!loading"
      class="flex flex-col items-center text-center py-12 px-6 bg-white rounded-3xl card-elevated"
    >
      <div
        class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-100 to-accent-100 text-primary-600 flex items-center justify-center mb-3"
      >
        <svg
          class="w-7 h-7"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18"
          />
        </svg>
      </div>
      <p class="text-sm font-semibold text-gray-900">尚未加载智能体说明</p>
      <p class="text-xs text-gray-500 mt-1">点击上方按钮从后端拉取。</p>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { api } from "../api/client";
type AgentOverview = Record<string, unknown>;
const overview = ref<AgentOverview>({});
const loading = ref(false);
const KNOWN_LIST_KEYS = new Set(["knowledge_agents", "collaboration_flow"]);
const knowledgeAgents = computed<string[]>(() => {
  const raw = overview.value.knowledge_agents;
  return Array.isArray(raw) ? raw.map(String) : [];
});
const collaborationFlow = computed<string[]>(() => {
  const raw = overview.value.collaboration_flow;
  return Array.isArray(raw) ? raw.map(String) : [];
});
const extraSections = computed<[string, string[]][]>(() => {
  return Object.entries(overview.value)
    .filter(
      ([key, value]) =>
        !KNOWN_LIST_KEYS.has(key) && Array.isArray(value) && value.length > 0,
    )
    .map(([key, value]) => [key, (value as unknown[]).map(String)]);
});
const hasData = computed(
  () =>
    knowledgeAgents.value.length > 0 ||
    collaborationFlow.value.length > 0 ||
    extraSections.value.length > 0,
);
const nameInitial = (name: string) => {
  const trimmed = (name || "").trim();
  return trimmed ? trimmed.slice(0, 1) : "A";
};
const roleHint = (name: string) => {
  if (name.includes("需求")) return "拆解课程目标与可验收指标";
  if (name.includes("数据") || name.includes("采集"))
    return "抓取并清洗 OSM / Wikipedia 数据";
  if (name.includes("算法") || name.includes("实验"))
    return "跑通算法实验与基准";
  if (name.includes("测试") || name.includes("文档"))
    return "撰写报告、脚本与验收清单";
  if (name.includes("前端")) return "打磨交互与视觉细节";
  if (name.includes("后端")) return "实现 API 与服务层";
  return "面向课程任务的专业协作者";
};
const GRADIENTS = [
  "bg-gradient-to-br from-primary-500 to-accent-500",
  "bg-gradient-to-br from-sky-500 to-primary-500",
  "bg-gradient-to-br from-emerald-500 to-teal-500",
  "bg-gradient-to-br from-amber-500 to-rose-500",
  "bg-gradient-to-br from-fuchsia-500 to-rose-500",
  "bg-gradient-to-br from-indigo-500 to-blue-500",
];
const knowledgeAgentStyle = (idx: number) => GRADIENTS[idx % GRADIENTS.length];
const formatKey = (key: string) =>
  key.replace(/_/g, "").replace(/\b\w/g, (char) => char.toUpperCase());
const load = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/agents");
    overview.value = (data ?? {}) as AgentOverview;
  } finally {
    loading.value = false;
  }
};
onMounted(() => {
  load();
});
</script>
