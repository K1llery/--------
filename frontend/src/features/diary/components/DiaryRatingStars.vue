<template>
  <div class="diary-rating">
    <div class="diary-rating-stars" @mouseleave="hoverScore = 0">
      <button
        v-for="n in 5"
        :key="n"
        type="button"
        class="diary-rating-star"
        :class="{ 'diary-rating-star-filled': n <= displayedScore }"
        :disabled="submitting"
        :aria-label="`评 ${n} 分`"
        @mouseenter="hoverScore = n"
        @click="onClick(n)"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path
            d="M12 2.5l2.95 6.5 7.05.62-5.34 4.69 1.62 6.94L12 17.77l-6.28 3.48 1.62-6.94L2 9.62 9.05 9z"
          />
        </svg>
      </button>
    </div>
    <div class="diary-rating-meta">
      <span class="diary-rating-average">
        平均 {{ averageRating.toFixed(1) }}
      </span>
      <span class="diary-rating-count">{{ ratingCountLabel }}</span>
      <span v-if="myScoreDisplay !== null" class="diary-rating-mine">
        我的评分：{{ myScoreDisplay.toFixed(1) }}
      </span>
    </div>
    <p v-if="errorMsg" class="diary-rating-error">{{ errorMsg }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

import { useAuthStore } from "../../../stores/auth";
import { rateDiary } from "../api/diaryApi";
import type { Diary } from "../types/diary";

const props = withDefaults(
  defineProps<{
    diaryId: number;
    averageRating: number;
    ratingCount?: number | null;
    myRating?: number | null;
  }>(),
  {
    ratingCount: null,
    myRating: null,
  },
);

const emit = defineEmits<{
  (
    e: "rated",
    payload: { diary: Diary; userScore: number; ratingCount: number },
  ): void;
}>();

const auth = useAuthStore();
const hoverScore = ref(0);
const localMyScore = ref<number | null>(null);
const submitting = ref(false);
const errorMsg = ref("");

const myScoreDisplay = computed<number | null>(() => {
  if (localMyScore.value !== null) return localMyScore.value;
  if (props.myRating !== null && props.myRating !== undefined) return props.myRating;
  return null;
});

const displayedScore = computed(() => {
  if (hoverScore.value) return hoverScore.value;
  if (myScoreDisplay.value !== null) return Math.round(myScoreDisplay.value);
  return Math.round(props.averageRating);
});

const ratingCountLabel = computed(() =>
  props.ratingCount === null || props.ratingCount === undefined
    ? "暂无评分人数"
    : `${props.ratingCount} 人评分`,
);

const onClick = async (score: number) => {
  if (!auth.isLoggedIn) {
    auth.openAuthModal("login");
    return;
  }
  if (submitting.value) return;

  submitting.value = true;
  errorMsg.value = "";
  try {
    const data = await rateDiary(props.diaryId, score);
    localMyScore.value = data.user_score;
    emit("rated", {
      diary: data.diary,
      userScore: data.user_score,
      ratingCount: data.rating_count,
    });
  } catch {
    errorMsg.value = "评分失败，请稍后再试";
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.diary-rating {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.diary-rating-stars {
  display: inline-flex;
  gap: 4px;
}

.diary-rating-star {
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  color: rgb(203 213 225);
  transition: color 120ms ease, transform 120ms ease;
}

.diary-rating-star:hover {
  transform: scale(1.08);
}

.diary-rating-star:disabled {
  cursor: not-allowed;
}

.diary-rating-star-filled {
  color: rgb(250 204 21);
}

.diary-rating-star svg {
  width: 100%;
  height: 100%;
}

.diary-rating-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: rgb(100 116 139);
}

.diary-rating-average {
  font-weight: 600;
  color: rgb(15 23 42);
}

.diary-rating-mine {
  color: rgb(217 119 6);
  font-weight: 500;
}

.diary-rating-error {
  font-size: 12px;
  color: rgb(220 38 38);
}
</style>
