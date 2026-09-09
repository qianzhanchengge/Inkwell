<template>
  <div class="tag-cloud">
    <router-link
      v-for="tag in tags"
      :key="tag.id"
      :to="`/blog/tags/${encodeURIComponent(tag.name)}`"
      class="tag-cloud__item"
      :style="{ fontSize: fontSize(tag.count) }"
    >
      {{ tag.name }}<span v-if="tag.count != null" class="tag-cloud__count">{{ tag.count }}</span>
    </router-link>
    <span v-if="!tags.length" class="tag-cloud__empty">暂无标签</span>
  </div>
</template>

<script setup lang="ts">
import type { TagStat } from '@/types/blog'

defineProps<{ tags: TagStat[] }>()

function fontSize(count?: number): string {
  const n = count ?? 1
  if (n >= 20) return '18px'
  if (n >= 10) return '16px'
  if (n >= 5) return '14px'
  return '13px'
}
</script>

<style scoped lang="scss">
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tag-cloud__item {
  color: #606266;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f5f7fa;
  &:hover {
    color: #409eff;
    background: #ecf5ff;
  }
}
.tag-cloud__count {
  font-size: 12px;
  color: #c0c4cc;
  margin-left: 2px;
}
.tag-cloud__empty {
  color: #c0c4cc;
  font-size: 13px;
}
</style>
