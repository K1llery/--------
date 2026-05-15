<template>
  <section class="diary-compression-panel space-y-4">
    <div class="flex items-start justify-between gap-3 flex-wrap">
      <div>
        <h2 class="text-base font-bold text-slate-900">日记压缩演示</h2>
        <p class="text-xs text-slate-500 mt-1">
          演示使用 Huffman 无损编码对正文进行压缩存储，并在解压后逐字比对验证。
        </p>
      </div>
      <button
        class="btn-soft-primary text-sm"
        :disabled="loading || !content"
        @click="onCompress"
      >
        {{ loading ? "压缩中..." : result ? "重新压缩" : "运行压缩演示" }}
      </button>
    </div>

    <div v-if="error" class="alert-soft-error">{{ error }}</div>

    <div v-if="result" class="diary-compression-stats">
      <div class="diary-compression-stat">
        <span class="diary-compression-label">算法</span>
        <strong>Huffman 无损压缩</strong>
      </div>
      <div class="diary-compression-stat">
        <span class="diary-compression-label">原始大小</span>
        <strong>{{ formatBytes(result.original_bits) }}</strong>
        <small>{{ result.original_bits }} bits</small>
      </div>
      <div class="diary-compression-stat">
        <span class="diary-compression-label">压缩后大小</span>
        <strong>{{ formatBytes(result.compressed_bits) }}</strong>
        <small>{{ result.compressed_bits }} bits</small>
      </div>
      <div class="diary-compression-stat">
        <span class="diary-compression-label">压缩率</span>
        <strong>{{ ratioPercent }}%</strong>
        <small>节省 {{ savingsPercent }}%</small>
      </div>
      <div class="diary-compression-stat">
        <span class="diary-compression-label">是否可无损还原</span>
        <strong :class="verifyClass">{{ verifyLabel }}</strong>
      </div>
    </div>

    <div v-if="result">
      <button
        type="button"
        class="diary-compression-toggle"
        @click="showDetails = !showDetails"
      >
        {{ showDetails ? "▲ 收起技术细节" : "▼ 查看技术细节" }}
      </button>
      <div v-if="showDetails" class="space-y-3 mt-3">
        <div>
          <p class="diary-compression-section-title">编码表（前 12 项）</p>
          <pre class="diary-compression-code">{{ codesSnippet }}</pre>
        </div>
        <div>
          <p class="diary-compression-section-title">压缩 payload（前 200 位）</p>
          <pre class="diary-compression-code">{{ encodedSnippet }}</pre>
        </div>
        <div v-if="decompressed !== null">
          <p class="diary-compression-section-title">解压结果（前 200 字）</p>
          <pre class="diary-compression-code">{{ decompressedSnippet }}</pre>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

import { compressDiary, decompressDiary } from "../api/diaryApi";
import type { CompressionResponse } from "../types/diary";

const props = defineProps<{
  content: string;
}>();

const result = ref<CompressionResponse | null>(null);
const decompressed = ref<string | null>(null);
const loading = ref(false);
const error = ref("");
const showDetails = ref(false);

const verified = computed(
  () => decompressed.value !== null && decompressed.value === props.content,
);

const verifyLabel = computed(() => {
  if (!result.value) return "—";
  if (decompressed.value === null) return "验证失败";
  return verified.value ? "✓ 已通过" : "✗ 未通过";
});

const verifyClass = computed(() =>
  result.value && verified.value ? "text-emerald-600" : "text-rose-600",
);

const ratioPercent = computed(() =>
  result.value ? (result.value.compression_ratio * 100).toFixed(1) : "—",
);

const savingsPercent = computed(() =>
  result.value ? ((1 - result.value.compression_ratio) * 100).toFixed(1) : "—",
);

const escapeChar = (ch: string) => {
  if (ch === "\n") return "\\n";
  if (ch === "\r") return "\\r";
  if (ch === "\t") return "\\t";
  if (ch === " ") return "(空格)";
  return ch;
};

const codesSnippet = computed(() => {
  if (!result.value) return "";
  const entries = Object.entries(result.value.codes).slice(0, 12);
  return entries.map(([ch, code]) => `'${escapeChar(ch)}' → ${code}`).join("\n");
});

const encodedSnippet = computed(() => {
  if (!result.value) return "";
  const s = result.value.encoded;
  return s.length > 200 ? `${s.slice(0, 200)}...` : s;
});

const decompressedSnippet = computed(() => {
  const s = decompressed.value ?? "";
  return s.length > 200 ? `${s.slice(0, 200)}...` : s;
});

const formatBytes = (bits: number) => {
  const bytes = bits / 8;
  if (bytes < 1024) return `${bytes.toFixed(0)} B`;
  return `${(bytes / 1024).toFixed(2)} KB`;
};

const onCompress = async () => {
  if (!props.content) return;
  loading.value = true;
  error.value = "";
  decompressed.value = null;
  try {
    const compressed = await compressDiary(props.content);
    result.value = compressed;
    try {
      const decoded = await decompressDiary({
        encoded: compressed.encoded,
        codes: compressed.codes,
      });
      decompressed.value = decoded.content;
    } catch {
      decompressed.value = null;
    }
  } catch {
    error.value = "压缩失败，请稍后再试";
    result.value = null;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.diary-compression-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.diary-compression-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 14px;
  background: rgb(248 250 252);
  border-radius: 14px;
  border: 1px solid rgb(226 232 240);
}

.diary-compression-label {
  font-size: 11px;
  color: rgb(100 116 139);
}

.diary-compression-stat strong {
  font-size: 15px;
  color: rgb(15 23 42);
  font-weight: 700;
}

.diary-compression-stat small {
  font-size: 11px;
  color: rgb(148 163 184);
}

.diary-compression-toggle {
  font-size: 13px;
  color: rgb(71 85 105);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

.diary-compression-toggle:hover {
  color: rgb(15 23 42);
}

.diary-compression-section-title {
  font-size: 12px;
  font-weight: 600;
  color: rgb(51 65 85);
  margin-bottom: 4px;
}

.diary-compression-code {
  background: rgb(15 23 42);
  color: rgb(226 232 240);
  border-radius: 12px;
  padding: 12px;
  font-size: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.text-emerald-600 {
  color: rgb(5 150 105);
}

.text-rose-600 {
  color: rgb(225 29 72);
}
</style>
