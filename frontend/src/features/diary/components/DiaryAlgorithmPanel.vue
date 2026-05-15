<template>
  <details class="diary-algorithm-panel" :open="defaultOpen">
    <summary class="diary-algorithm-summary">
      <span class="diary-algorithm-toggle-label">算法说明</span>
      <span class="diary-algorithm-tags">
        <span v-if="searchTypeLabel" class="diary-algorithm-tag">检索：{{ searchTypeLabel }}</span>
        <span v-if="sortLabel" class="diary-algorithm-tag">排序：{{ sortLabel }}</span>
      </span>
    </summary>

    <div class="diary-algorithm-body">
      <section v-if="searchTypeLabel" class="diary-algorithm-section">
        <h4>当前检索方式</h4>
        <p>
          <strong>{{ searchTypeLabel }}</strong> ·
          {{ SEARCH_TYPE_DESCRIPTIONS[searchType ?? "fulltext"] }}
        </p>
      </section>

      <section v-if="sortLabel" class="diary-algorithm-section">
        <h4>当前排序方式</h4>
        <p>
          <strong>{{ sortLabel }}</strong> · {{ sortDescription }}
        </p>
        <p v-if="debug?.formula" class="diary-algorithm-formula">
          公式：<code>{{ debug.formula }}</code>
        </p>
        <p v-if="debug?.reason" class="diary-algorithm-reason">原因：{{ debug.reason }}</p>
        <p v-if="debug?.fallback" class="diary-algorithm-reason">
          回落策略：{{ debug.fallback }}
        </p>
        <p v-if="debug?.limitation" class="diary-algorithm-reason">
          限制：{{ debug.limitation }}
        </p>
      </section>

      <section v-if="hasInterestInfo" class="diary-algorithm-section">
        <h4>兴趣信号</h4>
        <p v-if="interestDestinations.length">
          命中目的地（{{ interestMatchedCount }}）：
          <span
            v-for="name in interestDestinations"
            :key="name"
            class="diary-algorithm-chip"
          >{{ name }}</span>
        </p>
        <p v-else>未检测到足够的兴趣信号。</p>
      </section>

      <section v-if="hasScores" class="diary-algorithm-section">
        <h4>命中分数（前 {{ scoreEntries.length }} 项）</h4>
        <table class="diary-algorithm-table">
          <thead>
            <tr>
              <th>日记 ID</th>
              <th>分数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="[id, score] in scoreEntries" :key="id">
              <td>{{ id }}</td>
              <td>{{ formatScore(score) }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-if="!debug" class="diary-algorithm-section">
        <h4>无后端调试信息</h4>
        <p>该上下文未提供命中分数与排序原因，仅展示静态算法说明。</p>
      </section>

      <section v-if="hasGlobalMean" class="diary-algorithm-section">
        <h4>贝叶斯平滑参数</h4>
        <p>
          先验权重 C = {{ debug?.prior_C }}，全局均值 m = {{ debug?.global_mean }}
        </p>
      </section>
    </div>
  </details>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type {
  DiaryAlgorithmDebug,
  DiarySearchType,
  DiarySortKey,
} from "../types/diary";

const props = withDefaults(
  defineProps<{
    searchType?: DiarySearchType | null;
    sort?: DiarySortKey | null;
    debug?: DiaryAlgorithmDebug | null;
    defaultOpen?: boolean;
  }>(),
  {
    searchType: null,
    sort: null,
    debug: null,
    defaultOpen: false,
  },
);

const SEARCH_TYPE_LABELS: Record<DiarySearchType, string> = {
  destination: "目的地搜索",
  title_exact: "标题精确查询",
  fulltext: "正文全文检索",
};

const SEARCH_TYPE_DESCRIPTIONS: Record<DiarySearchType, string> = {
  destination: "在 destination_index 里按归一化后的目的地名做 HashMap 等值查找；命中失败时只在目的地键集合中做子串匹配，不退化到全量扫描。",
  title_exact: "在 title_index 里按归一化后的标题做 HashMap O(1) 等值查找；不命中直接返回空。",
  fulltext: "构建带字段权重的倒排索引，中文按 bigram 切分；查询按 (title=5, destination=4, tags=3, content=1) 加权累计相关度。",
};

const SORT_LABELS: Record<DiarySortKey | "hot" | "interest", string> = {
  recommend: "综合推荐",
  views: "热度最高",
  rating: "评分最高",
  latest: "最新发布",
  hot: "热度最高",
  interest: "兴趣推荐",
};

const SORT_DESCRIPTIONS: Record<string, string> = {
  recommend: "对 views 与 rating 分别归一化后线性加权，避免单一维度被极端值主导。",
  views: "直接按浏览量降序，体现热度。",
  hot: "直接按浏览量降序，体现热度。",
  rating: "若有 rating_count 则做贝叶斯平滑，否则用原始平均分（无法平滑会在面板里注明）。",
  latest: "按 created_at 字符串降序，最新发布的优先。",
  interest: "结合用户自有日记、4 分以上评分、收藏目的地构成兴趣集合，命中过少时回落到综合推荐。",
};

const searchTypeLabel = computed(() =>
  props.searchType ? SEARCH_TYPE_LABELS[props.searchType] : "",
);

const sortLabel = computed(() => {
  const key = (props.debug?.sort ?? props.sort) as string | undefined;
  if (!key) return "";
  return SORT_LABELS[key as keyof typeof SORT_LABELS] ?? key;
});

const sortDescription = computed(() => {
  const key = (props.debug?.sort ?? props.sort) as string | undefined;
  if (!key) return "";
  return SORT_DESCRIPTIONS[key] ?? "";
});

const scoreEntries = computed<[string, number][]>(() => {
  const scores = props.debug?.scores;
  if (!scores) return [];
  return Object.entries(scores).slice(0, 20);
});

const hasScores = computed(() => scoreEntries.value.length > 0);

const interestDestinations = computed<string[]>(() => props.debug?.interest_destinations ?? []);

const interestMatchedCount = computed<number>(
  () => props.debug?.matched_count ?? interestDestinations.value.length,
);

const hasInterestInfo = computed(
  () =>
    (props.debug?.sort ?? props.sort) === "interest" ||
    props.debug?.interest_destinations !== undefined,
);

const hasGlobalMean = computed(
  () =>
    typeof props.debug?.global_mean === "number" &&
    typeof props.debug?.prior_C === "number",
);

const formatScore = (value: number): string => {
  if (Number.isInteger(value)) return String(value);
  return value.toFixed(3);
};
</script>

<style scoped>
.diary-algorithm-panel {
  border: 1px solid rgb(226 232 240);
  border-radius: 18px;
  background: rgb(248 250 252);
  padding: 12px 18px;
}

.diary-algorithm-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  list-style: none;
  font-size: 14px;
  color: rgb(15 23 42);
  font-weight: 600;
}

.diary-algorithm-summary::-webkit-details-marker {
  display: none;
}

.diary-algorithm-summary::before {
  content: "▸";
  margin-right: 6px;
  color: rgb(100 116 139);
  transition: transform 120ms ease;
}

.diary-algorithm-panel[open] .diary-algorithm-summary::before {
  transform: rotate(90deg);
}

.diary-algorithm-toggle-label {
  flex: 1;
}

.diary-algorithm-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.diary-algorithm-tag {
  font-size: 11px;
  color: rgb(71 85 105);
  background: white;
  border: 1px solid rgb(226 232 240);
  border-radius: 999px;
  padding: 2px 10px;
  font-weight: 500;
}

.diary-algorithm-body {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.diary-algorithm-section h4 {
  font-size: 12px;
  font-weight: 600;
  color: rgb(51 65 85);
  margin-bottom: 4px;
  letter-spacing: 0.04em;
}

.diary-algorithm-section p {
  font-size: 13px;
  color: rgb(71 85 105);
  line-height: 1.6;
}

.diary-algorithm-formula code {
  background: rgb(15 23 42);
  color: rgb(226 232 240);
  font-size: 12px;
  border-radius: 6px;
  padding: 2px 6px;
}

.diary-algorithm-reason {
  font-size: 12px;
  color: rgb(100 116 139);
}

.diary-algorithm-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  background: white;
  border: 1px solid rgb(226 232 240);
  margin-right: 4px;
  margin-top: 2px;
  font-size: 12px;
  color: rgb(15 23 42);
}

.diary-algorithm-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.diary-algorithm-table th,
.diary-algorithm-table td {
  padding: 4px 8px;
  border-bottom: 1px solid rgb(226 232 240);
  text-align: left;
}

.diary-algorithm-table th {
  color: rgb(100 116 139);
  font-weight: 500;
}
</style>
