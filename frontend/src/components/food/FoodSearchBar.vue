<template>
  <input
    :value="keyword"
    class="soft-control text-sm text-slate-700 flex-[1_1_22rem]"
    placeholder="搜餐厅 / 菜系 / 食堂 / 窗口，例如：烤鸭、麻辣香锅、学五"
    @compositionstart="handleCompositionStart"
    @compositionend="handleCompositionEnd"
    @input="handleInput"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";

defineProps<{
  keyword: string;
}>();

const emit = defineEmits<{
  "update:keyword": [value: string];
}>();

const isComposing = ref(false);

const emitInputValue = (event: Event) => {
  emit("update:keyword", (event.target as HTMLInputElement).value);
};

const handleCompositionStart = () => {
  isComposing.value = true;
};

const handleCompositionEnd = (event: Event) => {
  isComposing.value = false;
  emitInputValue(event);
};

const handleInput = (event: Event) => {
  if (isComposing.value || (event as InputEvent).isComposing) return;
  emitInputValue(event);
};
</script>
