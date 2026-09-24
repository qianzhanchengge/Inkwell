<template>
  <div class="page-toolbar">
    <div class="page-toolbar__info">
      <slot name="info">{{ info }}</slot>
    </div>
    <div class="page-toolbar__actions">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 页面工具条：左侧为说明/统计文字，右侧为搜索、筛选与主操作。
 * 布局样式来自全局 `.page-toolbar`，保证各页面节奏一致。
 */
defineProps<{ info?: string }>()
</script>
