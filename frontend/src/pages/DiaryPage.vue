<template>
  <section class="panel-card">
    <div class="section-top">
      <div>
        <h2>旅游日记</h2>
        <p>浏览他人的路线心得，也可以登录后写下自己的城市散步记录。</p>
      </div>
      <button class="primary-btn" @click="openComposer">{{ showComposer ? "收起发布区" : "发布日记" }}</button>
    </div>

    <section v-if="showComposer" class="status-card">
      <div class="section-top compact">
        <h3>写一篇新的游记</h3>
        <span class="toolbar-hint">封面图会从已选目的地的本地图包里读取</span>
      </div>
      <form class="search-form" @submit.prevent="publishDiary">
        <select v-model="draft.destination_name" class="select-input">
          <option v-for="item in destinations" :key="item.source_id" :value="item.name">{{ item.name }}</option>
        </select>
        <input v-model="draft.title" placeholder="标题" />
        <textarea v-model="draft.content" class="text-area" placeholder="写下你的游览体验、路线建议或踩坑提醒"></textarea>
        <button class="primary-btn" type="submit">{{ publishing ? "发布中..." : "确认发布" }}</button>
      </form>
      <div v-if="draftCover" class="draft-cover">
        <img :src="draftCover.image_url" :alt="draft.destination_name" class="detail-image" />
      </div>
    </section>

    <form class="search-form" @submit.prevent="search">
      <input v-model="query" placeholder="输入关键字搜索日记" />
      <button class="primary-btn" type="submit">{{ searching ? "搜索中..." : "搜索" }}</button>
    </form>
    <div v-if="error" class="status-card error-card">{{ error }}</div>

    <section>
      <h3 class="section-title">推荐日记</h3>
      <div class="card-grid">
        <article
          v-for="item in diaries"
          :key="item.id"
          class="item-card media-card"
          :class="{ selected: selected?.id === item.id }"
          @click="store.selectDiary(item)"
        >
          <img :src="item.media_urls?.[0] || '/media/system/explore.svg'" :alt="item.title" class="media-thumb" />
          <div class="media-body">
            <h3>{{ item.title }}</h3>
            <p>{{ item.destination_name }}</p>
            <p>作者 {{ item.author_name || "匿名旅行者" }}</p>
          </div>
        </article>
      </div>
    </section>

    <section>
      <h3 class="section-title">搜索结果</h3>
      <div v-if="searching" class="status-card">正在搜索日记...</div>
      <div v-else-if="searchResults.length === 0" class="status-card">输入关键字后，这里会显示匹配到的日记。</div>
      <div v-else class="card-grid">
        <article
          v-for="item in searchResults"
          :key="`search-${item.id}`"
          class="item-card"
          :class="{ selected: selected?.id === item.id }"
          @click="store.selectDiary(item)"
        >
          <h3>{{ item.title }}</h3>
          <p>{{ item.destination_name }}</p>
          <p>浏览 {{ item.views }} · 评分 {{ item.rating }}</p>
        </article>
      </div>
    </section>

    <section v-if="selected" class="detail-panel detail-stack">
      <img :src="selected.media_urls?.[0] || '/media/system/explore.svg'" :alt="selected.title" class="detail-image" />
      <div>
        <h3>{{ selected.title }}</h3>
        <p>{{ selected.destination_name }}</p>
        <p>作者：{{ selected.author_name || "匿名旅行者" }} · 发布于 {{ selected.created_at || "演示数据" }}</p>
        <div class="detail-stats">
          <span class="stat-pill">浏览 {{ selected.views }}</span>
          <span class="stat-pill">评分 {{ selected.rating }}</span>
        </div>
        <p>{{ selected.content }}</p>
        <div class="hero-actions">
          <button class="primary-btn" @click="compress">压缩正文演示</button>
          <button class="primary-btn" @click="decompress" :disabled="!compressionPayload">解压回放</button>
          <button class="primary-btn" @click="addView">手动+1浏览</button>
          <button class="primary-btn" @click="rateDiary(4.0)">评分 4.0</button>
          <button class="primary-btn" @click="rateDiary(5.0)">评分 5.0</button>
        </div>
        <pre v-if="compressionResult">{{ compressionResult }}</pre>
        <pre v-if="decompressedContent">解压结果:\n{{ decompressedContent }}</pre>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";

import { api } from "../api/client";
import { useAuthStore } from "../stores/auth";
import { useTravelStore } from "../stores/travel";

const store = useTravelStore();
const auth = useAuthStore();
const diaries = computed(() => store.diaries.items);
const selected = computed(() => store.diaries.selected);
const error = computed(() => store.diaries.error);
const searchResults = computed(() => store.diarySearchResults.items);
const searching = computed(() => store.diarySearchResults.loading);
const destinations = computed(() => store.destinations.items);
const query = ref("故宫");
const compressionResult = ref("");
const compressionPayload = ref<{ encoded: string; codes: Record<string, string> } | null>(null);
const decompressedContent = ref("");
const showComposer = ref(false);
const publishing = ref(false);
const draft = reactive({
  destination_name: "",
  title: "",
  content: "",
});

const draftCover = computed(() => destinations.value.find((item) => item.name === draft.destination_name) ?? null);

const search = async () => {
  await store.searchDiaries(query.value);
};

const compress = async () => {
  if (!selected.value) return;
  const { data } = await api.post("/diaries/compress", { content: selected.value.content });
  compressionPayload.value = { encoded: data.encoded, codes: data.codes };
  decompressedContent.value = "";
  compressionResult.value = JSON.stringify(data, null, 2);
};

const decompress = async () => {
  if (!compressionPayload.value) return;
  const { data } = await api.post("/diaries/decompress", compressionPayload.value);
  decompressedContent.value = data.content;
};

const addView = async () => {
  if (!selected.value) return;
  await store.selectDiary(selected.value, true);
};

const rateDiary = async (score: number) => {
  if (!selected.value) return;
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  try {
    await store.rateDiary(selected.value.id, score);
  } catch (ratingError: any) {
    store.diaries.error = ratingError?.response?.data?.detail || "评分失败，请稍后再试。";
  }
};

const openComposer = async () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  showComposer.value = !showComposer.value;
};

const publishDiary = async () => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  publishing.value = true;
  try {
    await api.post("/diaries", {
      destination_name: draft.destination_name,
      title: draft.title,
      content: draft.content,
      cover_image_url: draftCover.value?.image_url,
      media_urls: draftCover.value?.image_url ? [draftCover.value.image_url] : [],
    });
    showComposer.value = false;
    draft.title = "";
    draft.content = "";
    await store.loadDiaries(true);
  } finally {
    publishing.value = false;
  }
};

onMounted(async () => {
  await Promise.all([store.loadDiaries(false), store.loadFeaturedDestinations(false)]);
  draft.destination_name = destinations.value[0]?.name ?? "";
});
</script>
