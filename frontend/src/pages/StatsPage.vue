<template>
  <div class="stats-page space-y-6">
    <section class="stats-hero">
      <div>
        <p class="home-section-kicker">数据洞察</p>
        <h2>验收证据工作台</h2>
        <p>
          汇总课程硬阈值、推荐评估、热门内容和算法证据，答辩时可以直接从这里证明系统规模与核心数据结构能力。
        </p>
      </div>
      <button class="btn-soft-primary text-sm" type="button" @click="load">
        {{ loading ? "正在刷新..." : "刷新数据" }}
      </button>
    </section>

    <div v-if="error" class="alert-soft-error">{{ error }}</div>

    <section v-if="overview" class="stats-grid stats-count-grid">
      <article v-for="item in countCards" :key="item.key" class="stats-count-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.hint }}</small>
      </article>
    </section>

    <section v-if="overview" class="stats-two-col">
      <div class="card-elevated rounded-[24px] p-5 lg:p-6">
        <div class="stats-section-head">
          <div>
            <span class="route-panel-kicker">课程阈值</span>
            <h3>硬性要求完成度</h3>
          </div>
          <span class="route-summary-chip route-summary-chip-accent">PPT 对照</span>
        </div>

        <div class="stats-progress-list">
          <div v-for="item in requirementCards" :key="item.key" class="stats-progress-row">
            <div class="stats-progress-top">
              <span>{{ item.label }}</span>
              <strong>{{ item.actual }} / {{ item.required }}</strong>
            </div>
            <div class="stats-progress-track">
              <span :style="{ width: `${Math.min(item.ratio, 100)}%` }" />
            </div>
            <small :class="item.passed ? 'text-emerald-600' : 'text-amber-600'">
              {{ item.passed ? "已达标" : "需要补充" }}
            </small>
          </div>
        </div>
      </div>

      <div class="stats-eval-panel">
        <div class="stats-section-head">
          <div>
            <span class="route-panel-kicker">推荐评估</span>
            <h3>F1 / Precision / Recall</h3>
          </div>
          <span class="route-summary-chip">Top-{{ evaluation?.top_k ?? 10 }}</span>
        </div>

        <div v-if="evaluation" class="stats-metric-ring-grid">
          <article>
            <strong>{{ toPercent(evaluation.f1) }}</strong>
            <span>F1</span>
          </article>
          <article>
            <strong>{{ toPercent(evaluation.precision) }}</strong>
            <span>Precision</span>
          </article>
          <article>
            <strong>{{ toPercent(evaluation.recall) }}</strong>
            <span>Recall</span>
          </article>
        </div>
        <p v-if="evaluation" class="stats-formula">{{ evaluation.formula }}</p>
        <div v-if="evaluation?.samples?.length" class="stats-sample-list">
          <div v-for="sample in evaluation.samples.slice(0, 3)" :key="sample.user_id">
            <strong>{{ sample.display_name }}</strong>
            <span>命中 {{ sample.hit_count }} / 推荐 {{ sample.recommended_count }}</span>
          </div>
        </div>
      </div>
    </section>

    <section v-if="overview" class="stats-three-col">
      <StatsRanking title="热门目的地" :items="overview.top_destinations" metric-key="heat" />
      <StatsRanking title="热门日记" :items="overview.top_diaries" metric-key="views" />
      <StatsRanking title="热门美食" :items="overview.top_foods" metric-key="heat" />
    </section>

    <section v-if="overview" class="stats-two-col">
      <div class="card-elevated rounded-[24px] p-5 lg:p-6">
        <div class="stats-section-head">
          <div>
            <span class="route-panel-kicker">分布结构</span>
            <h3>城市、类别与口碑</h3>
          </div>
        </div>
        <div class="stats-distribution-grid">
          <StatsDistribution title="目的地类别" :items="overview.distributions.destination_categories" />
          <StatsDistribution title="城市规模" :items="overview.distributions.cities" />
          <StatsDistribution title="设施类型" :items="overview.distributions.facility_types" />
          <StatsDistribution title="评分分布" :items="overview.distributions.rating_buckets" />
        </div>
      </div>

      <div class="card-elevated rounded-[24px] p-5 lg:p-6">
        <div class="stats-section-head">
          <div>
            <span class="route-panel-kicker">算法证据</span>
            <h3>可讲解的核心实现</h3>
          </div>
        </div>
        <div class="stats-evidence-list">
          <article v-for="item in overview.algorithm_evidence" :key="item.name">
            <strong>{{ item.name }}</strong>
            <span>{{ item.implementation }}</span>
          </article>
        </div>
        <div class="stats-compression-card">
          <span>{{ overview.compression_summary.algorithm }}</span>
          <strong>{{ toPercent(overview.compression_summary.average_ratio) }}</strong>
          <small>
            {{ overview.compression_summary.item_count }} 篇日记内容，压缩后 /
            原始位数比
          </small>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable vue/one-component-per-file */
import { computed, defineComponent, h, onMounted, ref } from "vue";
import type { PropType } from "vue";

import { api } from "../api/client";
import type { RecommendationEvaluationResponse, StatsOverviewResponse } from "../types/api";

const overview = ref<StatsOverviewResponse | null>(null);
const evaluation = ref<RecommendationEvaluationResponse | null>(null);
const loading = ref(false);
const error = ref("");

const numberFormat = new Intl.NumberFormat("zh-CN");
const toPercent = (value: number) => `${Math.round(value * 100)}%`;
const metricValue = (item: Record<string, unknown>, key: string) => {
  const raw = item[key];
  return typeof raw === "number" ? numberFormat.format(raw) : raw ? String(raw) : "-";
};

const countCards = computed(() => {
  const counts = overview.value?.counts ?? {};
  return [
    { key: "destinations", label: "目的地", value: counts.destinations ?? 0, hint: "景点 / 校园 / 商圈" },
    { key: "buildings", label: "建筑地点", value: counts.buildings ?? 0, hint: "内部建筑与场所" },
    { key: "facilities", label: "服务设施", value: counts.facilities ?? 0, hint: "图距离可查询" },
    { key: "edges", label: "道路边", value: counts.edges ?? 0, hint: "本地有向图" },
    { key: "foods", label: "美食", value: counts.foods ?? 0, hint: "Top-K 推荐" },
    { key: "diaries", label: "日记", value: counts.diaries ?? 0, hint: "检索与压缩" },
  ].map((item) => ({ ...item, value: numberFormat.format(item.value) }));
});

const requirementCards = computed(() =>
  Object.entries(overview.value?.requirement_progress ?? {}).map(([key, item]) => ({
    key,
    ...item,
    ratio: item.required ? (item.actual / item.required) * 100 : 0,
  })),
);

const load = async () => {
  loading.value = true;
  error.value = "";
  try {
    const [overviewResponse, evaluationResponse] = await Promise.all([
      api.get<StatsOverviewResponse>("/stats/overview"),
      api.get<RecommendationEvaluationResponse>("/stats/recommendation-evaluation", {
        params: { top_k: 10 },
      }),
    ]);
    overview.value = overviewResponse.data;
    evaluation.value = evaluationResponse.data;
  } catch {
    error.value = "数据洞察加载失败，请确认后端服务已启动。";
  } finally {
    loading.value = false;
  }
};

const StatsRanking = defineComponent({
  props: {
    title: { type: String, required: true },
    items: { type: Array as PropType<Record<string, unknown>[]>, required: true },
    metricKey: { type: String, required: true },
  },
  setup(props) {
    return () =>
      h("article", { class: "stats-ranking-card" }, [
        h("div", { class: "stats-section-head" }, [
          h("div", [h("span", { class: "route-panel-kicker" }, "Top-K"), h("h3", props.title)]),
        ]),
        h(
          "div",
          { class: "stats-ranking-list" },
          props.items.slice(0, 5).map((item, index) =>
            h("div", { class: "stats-ranking-row", key: `${item.source_id ?? item.id ?? item.name}` }, [
              h("span", { class: "stats-rank-index" }, String(index + 1).padStart(2, "0")),
              h("strong", String(item.name ?? item.title ?? "未命名")),
              h("small", metricValue(item, props.metricKey)),
            ]),
          ),
        ),
      ]);
  },
});

const StatsDistribution = defineComponent({
  props: {
    title: { type: String, required: true },
    items: { type: Array as PropType<Array<{ label: string; value: number }>>, required: true },
  },
  setup(props) {
    return () => {
      const max = Math.max(...props.items.map((item) => item.value), 1);
      return h("article", { class: "stats-distribution-card" }, [
        h("h4", props.title),
        h(
          "div",
          { class: "stats-distribution-list" },
          props.items.slice(0, 6).map((item) =>
            h("div", { class: "stats-distribution-row", key: item.label }, [
              h("div", [h("span", item.label), h("strong", numberFormat.format(item.value))]),
              h("div", { class: "stats-mini-track" }, [
                h("span", { style: { width: `${Math.max(6, (item.value / max) * 100)}%` } }),
              ]),
            ]),
          ),
        ),
      ]);
    };
  },
});

onMounted(load);
</script>

<style scoped>
.stats-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.75rem;
  border: 1px solid rgba(45, 92, 130, 0.12);
  border-radius: 28px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(234, 245, 244, 0.92)),
    radial-gradient(circle at right top, rgba(242, 107, 29, 0.15), transparent 32%);
  box-shadow: 0 24px 70px rgba(37, 64, 96, 0.1);
}

.stats-hero h2 {
  margin: 0.2rem 0 0;
  font-size: clamp(1.8rem, 3vw, 3rem);
  font-weight: 800;
  color: #172331;
}

.stats-hero p {
  max-width: 56rem;
  margin: 0.75rem 0 0;
  color: #64758a;
  line-height: 1.8;
}

.stats-grid,
.stats-two-col,
.stats-three-col {
  display: grid;
  gap: 1rem;
}

.stats-count-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.stats-two-col {
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
}

.stats-three-col {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.stats-count-card,
.stats-eval-panel,
.stats-ranking-card {
  border: 1px solid rgba(176, 202, 222, 0.76);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 20px 56px rgba(45, 74, 104, 0.08);
}

.stats-count-card {
  min-height: 126px;
  padding: 1rem;
}

.stats-count-card span,
.stats-count-card small {
  display: block;
  color: #6b7d91;
  font-size: 0.78rem;
}

.stats-count-card strong {
  display: block;
  margin: 0.45rem 0 0.25rem;
  color: #172331;
  font-size: 1.8rem;
  font-weight: 800;
}

.stats-section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stats-section-head h3 {
  margin: 0.2rem 0 0;
  color: #172331;
  font-size: 1.05rem;
  font-weight: 800;
}

.stats-progress-list,
.stats-ranking-list,
.stats-evidence-list,
.stats-sample-list,
.stats-distribution-list {
  display: grid;
  gap: 0.8rem;
}

.stats-progress-top,
.stats-ranking-row,
.stats-sample-list > div,
.stats-distribution-row > div:first-child {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
}

.stats-progress-top span,
.stats-ranking-row strong,
.stats-sample-list strong,
.stats-distribution-row span {
  min-width: 0;
  color: #263647;
  font-weight: 700;
}

.stats-progress-top strong,
.stats-distribution-row strong {
  color: #1475c4;
  white-space: nowrap;
}

.stats-progress-track,
.stats-mini-track {
  overflow: hidden;
  height: 0.55rem;
  border-radius: 999px;
  background: #e8f0f7;
}

.stats-progress-track span,
.stats-mini-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #1475c4, #31b58b);
}

.stats-eval-panel {
  padding: 1.25rem;
  background: linear-gradient(180deg, #18344d, #112536);
  color: #ffffff;
}

.stats-eval-panel h3,
.stats-eval-panel .route-panel-kicker {
  color: #ffffff;
}

.stats-metric-ring-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.stats-metric-ring-grid article {
  min-height: 112px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.08);
}

.stats-metric-ring-grid strong {
  display: block;
  font-size: 1.9rem;
}

.stats-metric-ring-grid span,
.stats-formula,
.stats-sample-list span {
  color: rgba(255, 255, 255, 0.72);
  font-size: 0.82rem;
}

.stats-formula {
  margin: 1rem 0;
  line-height: 1.7;
}

.stats-ranking-card {
  padding: 1.25rem;
}

.stats-rank-index {
  display: grid;
  width: 2.1rem;
  height: 2.1rem;
  place-items: center;
  border-radius: 12px;
  color: #1475c4;
  background: #e8f4ff;
  font-weight: 800;
  flex: 0 0 auto;
}

.stats-ranking-row strong {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stats-ranking-row small {
  color: #6b7d91;
  white-space: nowrap;
}

.stats-distribution-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.stats-distribution-card {
  padding: 1rem;
  border-radius: 18px;
  background: #f7fbff;
}

.stats-distribution-card h4 {
  margin: 0 0 0.8rem;
  color: #172331;
  font-size: 0.95rem;
}

.stats-evidence-list article {
  padding: 0.9rem 1rem;
  border-radius: 16px;
  background: #f7fbff;
}

.stats-evidence-list strong,
.stats-evidence-list span {
  display: block;
}

.stats-evidence-list span {
  margin-top: 0.2rem;
  color: #637589;
  font-size: 0.84rem;
}

.stats-compression-card {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 18px;
  color: #ffffff;
  background: linear-gradient(135deg, #1475c4, #31b58b);
}

.stats-compression-card span,
.stats-compression-card small,
.stats-compression-card strong {
  display: block;
}

.stats-compression-card strong {
  margin: 0.2rem 0;
  font-size: 2rem;
}

.stats-compression-card small {
  color: rgba(255, 255, 255, 0.82);
}

@media (max-width: 1180px) {
  .stats-count-grid,
  .stats-three-col {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .stats-two-col {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .stats-hero {
    display: grid;
    padding: 1.25rem;
  }

  .stats-count-grid,
  .stats-three-col,
  .stats-distribution-grid,
  .stats-metric-ring-grid {
    grid-template-columns: 1fr;
  }
}
</style>
