<template>
  <div class="markdown-preview">
    <template v-if="!content">{{ defaultText }}</template>
    <!-- 骨架阶段直接渲染 HTML 内容；接入后端 content_html 或引入 markdown 渲染库后替换 -->
    <div v-else class="markdown-preview__content" v-html="content"></div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ content?: string; defaultText?: string }>(), {
  content: '',
  defaultText: '暂无内容'
})
</script>

<style scoped lang="scss">
.markdown-preview__content {
  line-height: 1.7;
  word-break: break-word;
}
</style>
