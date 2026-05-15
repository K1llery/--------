<template>
  <div class="diary-editor-page space-y-6">
    <div>
      <router-link :to="cancelTarget" class="text-sm text-slate-500 hover:text-slate-900">
        ← {{ isEditMode ? "返回详情" : "返回日记列表" }}
      </router-link>
    </div>

    <section class="card-elevated rounded-[28px] p-6 lg:p-7 space-y-2">
      <p class="home-section-kicker">旅游日记</p>
      <h1 class="text-2xl font-bold text-slate-950">
        {{ isEditMode ? "编辑日记" : "写一篇新的旅行日记" }}
      </h1>
      <p class="text-sm text-slate-500">
        填写目的地、标题和正文，可选地用 AI 帮写、生成封面或粘贴媒体 URL。
      </p>
    </section>

    <div v-if="loadError" class="alert-soft-error">{{ loadError }}</div>
    <div v-else-if="loading" class="card-elevated rounded-[24px] p-6 text-sm text-slate-500">
      加载中...
    </div>

    <section v-else class="card-elevated rounded-[24px] p-6 lg:p-7 space-y-5">
      <form class="space-y-5" @submit.prevent="onSubmit">
        <div class="grid lg:grid-cols-[minmax(0,1fr)_320px] gap-6 items-start">
          <div class="space-y-4">
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="field-label">目的地</label>
                <input
                  v-model="draft.destination_name"
                  list="diary-destination-list"
                  class="soft-control w-full"
                  placeholder="输入或选择目的地名称"
                  required
                />
                <datalist id="diary-destination-list">
                  <option
                    v-for="item in destinations"
                    :key="item.source_id"
                    :value="item.name"
                  />
                </datalist>
              </div>
              <div>
                <label class="field-label">标题</label>
                <input
                  v-model="draft.title"
                  class="soft-control w-full"
                  placeholder="例如：一天走完鼓浪屿的轻松路线"
                  required
                />
              </div>
            </div>

            <div>
              <label class="field-label">正文</label>
              <textarea
                v-model="draft.content"
                class="soft-control w-full min-h-48"
                placeholder="写下游览体验、路线建议、避坑提醒或值得停留的细节。"
                required
              ></textarea>
            </div>

            <div class="space-y-3">
              <div>
                <label class="field-label">上传图片 / 视频</label>
                <input
                  ref="fileInputRef"
                  type="file"
                  accept="image/*,video/*"
                  multiple
                  class="diary-editor-file-input"
                  :disabled="uploading"
                  @change="onFileChange"
                />
                <p class="text-xs text-slate-400 mt-1">
                  图片单文件 ≤ 8MB，视频 ≤ 64MB；首张图片或视频会作为封面。
                </p>
                <p v-if="uploading" class="text-xs text-slate-500 mt-1">
                  正在上传：{{ uploadingName }}…
                </p>
                <p v-if="uploadError" class="text-xs text-rose-600 mt-1">{{ uploadError }}</p>
              </div>

              <div v-if="uploadedMedia.length" class="diary-editor-media-list">
                <div
                  v-for="(item, idx) in uploadedMedia"
                  :key="`${item.url}-${idx}`"
                  class="diary-editor-media-cell"
                >
                  <video
                    v-if="item.type === 'video'"
                    :src="item.url"
                    controls
                    playsinline
                    preload="metadata"
                  />
                  <img v-else :src="item.url" :alt="item.url" />
                  <button
                    type="button"
                    class="diary-editor-media-remove"
                    @click="removeUploaded(idx)"
                  >
                    移除
                  </button>
                </div>
              </div>

              <div>
                <label class="field-label">额外媒体 URL（每行一个，可选）</label>
                <textarea
                  v-model="mediaUrlsRaw"
                  class="soft-control w-full min-h-20"
                  placeholder="https://example.com/photo.jpg"
                ></textarea>
              </div>
            </div>

            <div class="flex flex-wrap gap-3">
              <button
                class="btn-soft-secondary text-sm"
                type="button"
                :disabled="aiDrafting"
                @click="generateDiaryDraft"
              >
                {{ aiDrafting ? "正在生成..." : "AI 帮写日记" }}
              </button>
              <button
                class="btn-soft-secondary text-sm"
                type="button"
                :disabled="aiImageGenerating || !draft.title || !draft.content"
                @click="generateCoverImage"
              >
                {{ aiImageGenerating ? "正在生成..." : "AI 生成封面" }}
              </button>
              <button
                class="btn-soft-primary text-sm"
                type="submit"
                :disabled="submitting"
              >
                {{ submitting ? (isEditMode ? "保存中..." : "发布中...") : (isEditMode ? "保存修改" : "确认发布") }}
              </button>
            </div>

            <div v-if="aiError" class="alert-soft-error">{{ aiError }}</div>
            <div v-if="submitError" class="alert-soft-error">{{ submitError }}</div>
          </div>

          <aside class="diary-composer-preview">
            <span class="route-panel-kicker">封面预览</span>
            <RealImage
              v-if="coverPreview"
              :src="coverPreview.image_url"
              :alt="draft.destination_name || '日记封面'"
              :name="draft.destination_name || '旅行日记'"
              :city="coverPreview.city"
              :latitude="coverPreview.latitude"
              :longitude="coverPreview.longitude"
              :source-url="coverPreview.source_url"
              class="w-full h-52 object-cover rounded-[20px] bg-slate-100 mt-3"
            />
            <div v-else class="diary-composer-empty mt-3">
              <p>选择目的地、填写媒体 URL 或生成 AI 封面后会显示在这里。</p>
            </div>
          </aside>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { api } from "../../api/client";
import RealImage from "../../components/RealImage.vue";
import {
  createDiary,
  getDiary,
  updateDiary,
  uploadDiaryMedia,
} from "../../features/diary/api/diaryApi";
import type { Diary, DiaryMedia } from "../../features/diary/types/diary";
import { inferMediaType } from "../../features/diary/utils/media";
import { useAuthStore } from "../../stores/auth";
import { useTravelStore } from "../../stores/travel";
import type { DiaryDraftResponse, ImageGenerateResponse } from "../../types/api";
import type { Destination } from "../../types/models";

type CoverPreview = {
  image_url: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  source_url?: string;
};

type ApiFailure = {
  response?: {
    data?: {
      detail?: string;
    };
  };
};

const auth = useAuthStore();
const store = useTravelStore();
const router = useRouter();
const route = useRoute();

const destinations = computed(() => store.destinations.items as Destination[]);

const editId = computed(() => {
  const raw = route.params.id;
  if (raw === undefined || raw === "") return null;
  const id = Number(Array.isArray(raw) ? raw[0] : raw);
  return Number.isFinite(id) ? id : null;
});

const isEditMode = computed(() => editId.value !== null);

const cancelTarget = computed(() =>
  isEditMode.value && editId.value !== null ? `/diaries/${editId.value}` : "/diaries",
);

const draft = reactive({
  destination_name: "",
  title: "",
  content: "",
});

const mediaUrlsRaw = ref("");
const generatedCoverUrl = ref("");
const aiDrafting = ref(false);
const aiImageGenerating = ref(false);
const aiError = ref("");
const submitting = ref(false);
const submitError = ref("");
const loading = ref(false);
const loadError = ref("");

const fileInputRef = ref<HTMLInputElement | null>(null);
const uploadedMedia = ref<DiaryMedia[]>([]);
const uploading = ref(false);
const uploadingName = ref("");
const uploadError = ref("");

type ApiFailureWithDetail = { response?: { data?: { detail?: string } } };

const onFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const files = input.files ? Array.from(input.files) : [];
  if (!files.length) return;
  uploadError.value = "";
  for (const file of files) {
    uploading.value = true;
    uploadingName.value = file.name;
    try {
      const data = await uploadDiaryMedia(file);
      uploadedMedia.value.push({
        type: data.type,
        url: data.url,
        order: uploadedMedia.value.length,
      });
    } catch (err) {
      uploadError.value =
        (err as ApiFailureWithDetail)?.response?.data?.detail || `上传失败：${file.name}`;
      break;
    } finally {
      uploading.value = false;
      uploadingName.value = "";
    }
  }
  if (fileInputRef.value) fileInputRef.value.value = "";
};

const removeUploaded = (index: number) => {
  uploadedMedia.value.splice(index, 1);
};

const draftCover = computed(
  () => destinations.value.find((item) => item.name === draft.destination_name) ?? null,
);

const mediaUrls = computed(() =>
  mediaUrlsRaw.value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean),
);

const coverPreview = computed<CoverPreview | null>(() => {
  if (generatedCoverUrl.value) {
    return {
      image_url: generatedCoverUrl.value,
      city: draftCover.value?.city,
      latitude: draftCover.value?.latitude,
      longitude: draftCover.value?.longitude,
      source_url: generatedCoverUrl.value,
    };
  }

  const firstImageUpload = uploadedMedia.value.find((m) => m.type === "image");
  if (firstImageUpload) {
    return {
      image_url: firstImageUpload.url,
      city: draftCover.value?.city,
      latitude: draftCover.value?.latitude,
      longitude: draftCover.value?.longitude,
      source_url: firstImageUpload.url,
    };
  }

  const firstUrlImage = mediaUrls.value.find((url) => inferMediaType(url) === "image");
  if (firstUrlImage) {
    return {
      image_url: firstUrlImage,
      city: draftCover.value?.city,
      latitude: draftCover.value?.latitude,
      longitude: draftCover.value?.longitude,
      source_url: firstUrlImage,
    };
  }

  if (draftCover.value?.image_url) {
    return {
      image_url: draftCover.value.image_url,
      city: draftCover.value.city,
      latitude: draftCover.value.latitude,
      longitude: draftCover.value.longitude,
      source_url: draftCover.value.source_url,
    };
  }

  return null;
});

const apiErrorDetail = (error: unknown, fallback: string) =>
  (error as ApiFailure)?.response?.data?.detail || fallback;

const ensureLoggedIn = (): boolean => {
  if (auth.isLoggedIn) return true;
  auth.openAuthModal("login");
  return false;
};

const generateDiaryDraft = async () => {
  if (!ensureLoggedIn()) return;
  aiDrafting.value = true;
  aiError.value = "";
  try {
    const { data } = await api.post<DiaryDraftResponse>("/ai/diary/draft", {
      destination_name: draft.destination_name,
      keywords: [draft.destination_name].filter(Boolean),
      style: "轻松真实，适合课程演示",
    });
    draft.title = data.title;
    draft.content = data.content;
  } catch (err) {
    aiError.value = apiErrorDetail(err, "AI 日记生成失败，请检查模型配置。");
  } finally {
    aiDrafting.value = false;
  }
};

const generateCoverImage = async () => {
  if (!ensureLoggedIn()) return;
  aiImageGenerating.value = true;
  aiError.value = "";
  try {
    const { data } = await api.post<ImageGenerateResponse>("/ai/images/generate", {
      destination_name: draft.destination_name,
      title: draft.title,
      content: draft.content,
    });
    generatedCoverUrl.value = data.image_url;
  } catch (err) {
    aiError.value = apiErrorDetail(err, "AI 封面生成失败，请检查模型配置。");
  } finally {
    aiImageGenerating.value = false;
  }
};

const buildPayload = () => {
  const uploadedUrls = uploadedMedia.value.map((m) => m.url);
  const merged = [
    ...(generatedCoverUrl.value ? [generatedCoverUrl.value] : []),
    ...uploadedUrls,
    ...mediaUrls.value,
  ];
  const seen = new Set<string>();
  const finalUrls = merged.filter((url) => {
    if (!url || seen.has(url)) return false;
    seen.add(url);
    return true;
  });
  return {
    destination_name: draft.destination_name.trim(),
    title: draft.title.trim(),
    content: draft.content.trim(),
    cover_image_url: finalUrls[0] ?? "",
    media_urls: finalUrls,
  };
};

const onSubmit = async () => {
  if (!ensureLoggedIn()) return;
  submitting.value = true;
  submitError.value = "";
  try {
    const payload = buildPayload();
    let result: Diary;
    if (isEditMode.value && editId.value !== null) {
      result = await updateDiary(editId.value, payload);
    } else {
      result = await createDiary(payload);
    }
    router.push(`/diaries/${result.id}`);
  } catch (err) {
    submitError.value = apiErrorDetail(
      err,
      isEditMode.value ? "保存失败，请稍后再试。" : "发布失败，请稍后再试。",
    );
  } finally {
    submitting.value = false;
  }
};

const loadForEdit = async (id: number) => {
  loading.value = true;
  loadError.value = "";
  try {
    const diary = await getDiary(id);
    if (auth.user && diary.author_id !== undefined && diary.author_id !== auth.user.id) {
      loadError.value = "你不是这篇日记的作者，无法编辑。";
      return;
    }
    draft.destination_name = diary.destination_name;
    draft.title = diary.title;
    draft.content = diary.content;
    mediaUrlsRaw.value = (diary.media_urls ?? []).join("\n");
    uploadedMedia.value = [];
    generatedCoverUrl.value = "";
  } catch {
    loadError.value = "加载日记失败";
  } finally {
    loading.value = false;
  }
};

watch(
  () => draft.destination_name,
  () => {
    aiError.value = "";
  },
);

onMounted(async () => {
  if (!ensureLoggedIn()) {
    router.replace("/diaries");
    return;
  }
  await store.loadFeaturedDestinations(false);
  if (isEditMode.value && editId.value !== null) {
    await loadForEdit(editId.value);
  } else if (!draft.destination_name) {
    draft.destination_name = destinations.value[0]?.name ?? "";
  }
});
</script>

<style scoped>
.diary-editor-file-input {
  display: block;
  width: 100%;
  font-size: 13px;
  color: rgb(71 85 105);
}

.diary-editor-file-input::file-selector-button {
  margin-right: 12px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgb(226 232 240);
  background: white;
  font-size: 13px;
  color: rgb(15 23 42);
  cursor: pointer;
}

.diary-editor-file-input::file-selector-button:hover {
  background: rgb(248 250 252);
}

.diary-editor-media-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.diary-editor-media-cell {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  background: rgb(241 245 249);
}

.diary-editor-media-cell img,
.diary-editor-media-cell video {
  display: block;
  width: 100%;
  height: 110px;
  object-fit: cover;
}

.diary-editor-media-cell video {
  background: black;
}

.diary-editor-media-remove {
  position: absolute;
  top: 6px;
  right: 6px;
  padding: 2px 8px;
  border: none;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.75);
  color: white;
  font-size: 11px;
  cursor: pointer;
}

.diary-editor-media-remove:hover {
  background: rgba(15, 23, 42, 0.9);
}

.text-rose-600 {
  color: rgb(225 29 72);
}
</style>
