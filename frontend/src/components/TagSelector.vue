<template>
  <el-select
    v-model="model"
    multiple
    filterable
    allow-create
    default-first-option
    :placeholder="placeholder"
    class="tag-selector"
  >
    <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.name" />
  </el-select>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Tag } from '@/types/api'

const props = withDefaults(
  defineProps<{
    modelValue?: string[]
    tags?: Tag[]
    placeholder?: string
  }>(),
  {
    modelValue: () => [],
    tags: () => [],
    placeholder: '选择或输入标签'
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()

const model = computed({
  get: () => props.modelValue,
  set: (value: string[]) => emit('update:modelValue', value)
})
</script>

<style scoped lang="scss">
.tag-selector {
  width: 100%;
}
</style>
