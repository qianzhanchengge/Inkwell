<template>
  <MdPreview v-if="content" :model-value="content" />
  <div v-else class="markdown-preview__empty">{{ defaultText || '暂无内容' }}</div>
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3'

withDefaults(defineProps<{ content?: string; defaultText?: string }>(), {
  content: '',
  defaultText: ''
})
</script>

<style scoped>
.markdown-preview__empty {
  color: #909399;
  text-align: center;
  padding: 24px 0;
}
</style>
