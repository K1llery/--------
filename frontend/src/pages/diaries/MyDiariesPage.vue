<template>
  <div class="my-diaries-page space-y-6">
    <div>
      <router-link to="/diaries" class="text-sm text-slate-500 hover:text-slate-900">
        ← 返回日记发现
      </router-link>
    </div>

    <section class="card-elevated rounded-[28px] p-6 lg:p-7">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <p class="home-section-kicker">旅游日记</p>
          <h1 class="text-2xl font-bold text-slate-950 mt-1">我的日记</h1>
          <p class="text-sm text-slate-500 mt-2">
            管理你发布过的日记，可以查看、编辑或删除。
          </p>
        </div>
        <router-link to="/diaries/new" class="btn-soft-primary text-sm">
          写新日记
        </router-link>
      </div>
    </section>

    <div v-if="error" class="alert-soft-error">{{ error }}</div>

    <div v-if="loading" class="card-elevated rounded-[24px] p-6 text-sm text-slate-500">
      加载中...
    </div>
    <div
      v-else-if="!items.length"
      class="card-elevated rounded-[24px] p-6 text-sm text-slate-500"
    >
      你还没有发布过日记，去
      <router-link to="/diaries/new" class="text-slate-900 underline">写一篇</router-link>
      吧。
    </div>
    <ul v-else class="space-y-3">
      <li
        v-for="diary in items"
        :key="diary.id"
        class="card-elevated rounded-[20px] p-4 lg:p-5"
      >
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div class="min-w-0 flex-1">
            <h3 class="text-base font-bold text-slate-900">{{ diary.title }}</h3>
            <p class="text-sm text-slate-500 mt-1">
              目的地：{{ diary.destination_name }}
            </p>
            <div class="flex flex-wrap gap-3 mt-2 text-xs text-slate-500">
              <span>浏览 {{ diary.views }}</span>
              <span>评分 {{ diary.rating.toFixed(1) }}</span>
              <span v-if="diary.created_at">发布于 {{ diary.created_at }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <router-link
              :to="`/diaries/${diary.id}`"
              class="btn-soft-secondary text-sm"
            >
              查看
            </router-link>
            <router-link
              :to="`/diaries/${diary.id}/edit`"
              class="btn-soft-secondary text-sm"
            >
              编辑
            </router-link>
            <button
              type="button"
              class="btn-soft-danger text-sm"
              :disabled="deletingId === diary.id"
              @click="confirmDelete(diary)"
            >
              {{ deletingId === diary.id ? "删除中..." : "删除" }}
            </button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { deleteDiary, listMyDiaries } from "../../features/diary/api/diaryApi";
import type { Diary } from "../../features/diary/types/diary";
import { useAuthStore } from "../../stores/auth";

const auth = useAuthStore();
const router = useRouter();

const items = ref<Diary[]>([]);
const loading = ref(false);
const error = ref("");
const deletingId = ref<number | null>(null);

const load = async () => {
  loading.value = true;
  error.value = "";
  try {
    const res = await listMyDiaries();
    items.value = (res.items ?? []) as Diary[];
  } catch {
    error.value = "加载失败，请稍后再试。";
    items.value = [];
  } finally {
    loading.value = false;
  }
};

const confirmDelete = async (diary: Diary) => {
  if (!window.confirm(`确定要删除日记《${diary.title}》吗？此操作不可撤销。`)) return;
  deletingId.value = diary.id;
  error.value = "";
  try {
    await deleteDiary(diary.id);
    items.value = items.value.filter((item) => item.id !== diary.id);
  } catch {
    error.value = "删除失败，请稍后再试。";
  } finally {
    deletingId.value = null;
  }
};

onMounted(async () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    router.replace("/diaries");
    return;
  }
  await load();
});
</script>

<style scoped>
.btn-soft-danger {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid rgb(254 226 226);
  background: rgb(254 242 242);
  color: rgb(190 18 60);
  font-weight: 600;
  cursor: pointer;
  transition: background 120ms ease;
}

.btn-soft-danger:hover:not(:disabled) {
  background: rgb(254 226 226);
}

.btn-soft-danger:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
