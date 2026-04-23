<template>
  <article class="helper-card">
    <h3>出行风格</h3>
    <div class="profile-grid">
      <button
        v-for="profile in travelProfiles"
        :key="profile.key"
        type="button"
        class="profile-chip"
        :class="{ active: modelValue === profile.key }"
        @click="applyProfile(profile)"
      >
        <strong>{{ profile.label }}</strong>
        <span>{{ profile.description }}</span>
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
interface TravelProfile {
  key: string;
  label: string;
  description: string;
  strategy: string;
  transportMode: string;
}

defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  "update:modelValue": [key: string];
  "profile-applied": [profile: { strategy: string; transportMode: string }];
}>();

const travelProfiles: TravelProfile[] = [
  {
    key: "balanced",
    label: "省时优先",
    description: "最快到达 + 综合交通",
    strategy: "time",
    transportMode: "mixed",
  },
  {
    key: "urgent",
    label: "赶路直达",
    description: "最短距离 + 骑行",
    strategy: "distance",
    transportMode: "bike",
  },
  {
    key: "relaxed",
    label: "轻松漫游",
    description: "打卡优先 + 步行",
    strategy: "scenic",
    transportMode: "walk",
  },
  {
    key: "stable",
    label: "避堵稳妥",
    description: "避拥堵 + 综合交通",
    strategy: "congestion",
    transportMode: "mixed",
  },
];

const applyProfile = (profile: TravelProfile) => {
  emit("update:modelValue", profile.key);
  emit("profile-applied", { strategy: profile.strategy, transportMode: profile.transportMode });
};
</script>
