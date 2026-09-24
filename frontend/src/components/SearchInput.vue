<template>
  <div class="search-input" :style="{ width: cssWidth }">
    <el-input
      :model-value="modelValue"
      :placeholder="placeholder"
      clearable
      @update:model-value="onInput"
      @keyup.enter="onSearch"
      @clear="onClear"
    >
      <template #prefix>
        <AppIcon name="search" :size="15" class="search-input__icon" />
      </template>
    </el-input>
    <el-button v-if="showButton" type="primary" :loading="loading" @click="onSearch">
      搜索
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from '@/components/AppIcon.vue'

/**
 * 统一搜索框：左侧图标前缀 + 可选搜索按钮。
 * 样式（圆角 / 纸色底 / 聚焦强调环）由全局 Element Plus 收敛层提供。
 */
const props = withDefaults(
  defineProps<{
    modelValue?: string
    placeholder?: string
    width?: number | string
    showButton?: boolean
    loading?: boolean
  }>(),
  { modelValue: '', placeholder: '搜索', width: 240, showButton: false, loading: false }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'search'): void
}>()

const cssWidth = computed(() =>
  typeof props.width === 'number' ? `${props.width}px` : props.width
)

function onInput(value: string) {
  emit('update:modelValue', value)
}

function onSearch() {
  emit('search')
}

function onClear() {
  emit('update:modelValue', '')
  emit('search')
}
</script>

<style scoped lang="scss">
.search-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input__icon {
  color: var(--blog-ink-mute);
}
</style>
