<template>
  <MdEditor v-model="model" class="markdown-editor" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MdEditor } from 'md-editor-v3'

const props = withDefaults(defineProps<{ modelValue?: string }>(), {
  modelValue: ''
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const model = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value)
})
</script>

<style scoped>
.markdown-editor {
  width: 100%;
}
</style>
