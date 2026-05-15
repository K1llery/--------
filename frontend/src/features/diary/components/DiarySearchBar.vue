<template>
  <form class="search-workbench" @submit.prevent="onSubmit">
    <div class="flex items-stretch gap-3">
      <div class="search-input-shell flex-1 min-w-0">
        <div class="relative">
          <input
            :value="modelValue"
            class="soft-control search-input-control w-full pr-10"
            :placeholder="placeholder"
            @input="onInput"
            @focus="showDropdown = true"
            @blur="onBlur"
          />
          <button
            v-if="modelValue"
            type="button"
            class="search-input-clear"
            @click="onClear"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div
          v-if="showDropdown && (historyItems.length || suggestionItems.length)"
          class="search-dropdown"
        >
          <div v-if="historyItems.length" class="px-4 py-3">
            <p class="search-dropdown-kicker">历史记录</p>
            <div class="flex flex-wrap gap-2 mt-2">
              <button
                v-for="item in historyItems"
                :key="item"
                type="button"
                class="destination-tag-pill"
                @mousedown.prevent="onApplyHistory(item)"
              >
                {{ item }}
              </button>
            </div>
          </div>
          <div
            v-if="suggestionItems.length"
            class="px-4 py-3 border-t border-slate-100"
          >
            <p class="search-dropdown-kicker">关键词联想</p>
            <div class="flex flex-wrap gap-2 mt-2">
              <button
                v-for="item in suggestionItems"
                :key="item"
                type="button"
                class="search-suggestion-pill"
                @mousedown.prevent="onApplySuggestion(item)"
              >
                {{ item }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <button class="btn-soft-primary text-sm min-w-[120px]" type="submit">
        {{ searching ? "搜索中..." : submitLabel }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref } from "vue";

const props = withDefaults(
  defineProps<{
    modelValue: string;
    historyItems?: string[];
    suggestionItems?: string[];
    searching?: boolean;
    placeholder?: string;
    submitLabel?: string;
  }>(),
  {
    historyItems: () => [],
    suggestionItems: () => [],
    searching: false,
    placeholder: "输入目的地、标题关键词或旅行主题",
    submitLabel: "搜索日记",
  },
);

const emit = defineEmits<{
  (e: "update:modelValue", value: string): void;
  (e: "submit", value: string): void;
  (e: "clear"): void;
  (e: "apply-history", value: string): void;
  (e: "apply-suggestion", value: string): void;
}>();

const showDropdown = ref(false);

const onInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit("update:modelValue", target.value);
  showDropdown.value = true;
};

const onBlur = () => {
  setTimeout(() => {
    showDropdown.value = false;
  }, 150);
};

const onClear = () => {
  emit("update:modelValue", "");
  emit("clear");
};

const onSubmit = () => {
  emit("submit", props.modelValue);
};

const onApplyHistory = (value: string) => {
  showDropdown.value = false;
  emit("apply-history", value);
};

const onApplySuggestion = (value: string) => {
  showDropdown.value = false;
  emit("apply-suggestion", value);
};
</script>
