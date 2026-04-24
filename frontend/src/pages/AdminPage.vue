<template>
  <PanelCard title="数据导入与状态" subtitle="查看当前演示数据和导入目录">
    <button class="btn-soft-primary text-sm" @click="load">刷新状态</button>
    <pre
      class="mt-4 p-4 rounded-2xl bg-gray-50 border-0 shadow-md shadow-gray-200/50 text-xs overflow-auto whitespace-pre-wrap"
      >{{ JSON.stringify(status, null, 2) }}</pre
    >
  </PanelCard>
</template>
<script setup lang="ts">
import { ref } from "vue";
import { api } from "../api/client";
import PanelCard from "../components/PanelCard.vue";
const status = ref<Record<string, unknown>>({});
const load = async () => {
  const { data } = await api.get("/admin/import/status");
  status.value = data;
};
</script>
