<template>
  <div class="markdown-editor">
    <div class="markdown-editor__toolbar">
      <el-radio-group v-model="mode" size="small">
        <el-radio-button value="edit">编辑</el-radio-button>
        <el-radio-button value="preview">预览</el-radio-button>
      </el-radio-group>
    </div>
    <div v-show="mode === 'edit'" class="markdown-editor__edit">
      <el-input
        type="textarea"
        :model-value="modelValue"
        :rows="10"
        placeholder="请输入 Markdown 内容..."
        @update:model-value="onInput"
      />
    </div>
    <div v-show="mode === 'preview'" class="markdown-editor__preview">
      <MarkdownPreview :content="modelValue" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MarkdownPreview from './MarkdownPreview.vue'

withDefaults(defineProps<{ modelValue?: string }>(), {
  modelValue: ''
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const mode = ref<'edit' | 'preview'>('edit')

function onInput(value: string) {
  emit('update:modelValue', value)
}
</script>

<style scoped lang="scss">
.markdown-editor__toolbar {
  margin-bottom: 8px;
}
.markdown-editor__preview {
  min-height: 200px;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
</style>
