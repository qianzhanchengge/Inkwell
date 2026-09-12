<template>
  <div class="tag-cloud">
    <router-link
      v-for="tag in tags"
      :key="tag.id"
      :to="`/blog/tags/${encodeURIComponent(tag.name)}`"
      class="tag-cloud__item"
    >
      {{ tag.name }}
      <span v-if="countOf(tag) != null" class="tag-cloud__count">{{ countOf(tag) }}</span>
    </router-link>
    <span v-if="!tags.length" class="tag-cloud__empty">暂无标签</span>
  </div>
</template>

<script setup lang="ts">
import type { TagStat } from '@/types/blog'

defineProps<{ tags: TagStat[] }>()

/** 后端 /blog/tags 返回 use_count，兼容历史字段 count */
function countOf(tag: TagStat): number | undefined {
  return tag.use_count ?? tag.count
}
</script>

<style scoped lang="scss">
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-cloud__item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 13px;
  color: var(--blog-ink-soft);
  background: var(--blog-paper);
  border: 1px solid var(--blog-line);
  border-radius: var(--blog-radius-sm);
  transition: background 0.2s, color 0.2s, border-color 0.2s, transform 0.15s;

  &:hover {
    color: var(--blog-accent);
    background: var(--blog-accent-soft);
    border-color: var(--blog-accent-soft);
  }

  &:active {
    transform: translateY(1px);
  }
}

.tag-cloud__count {
  font-size: 12px;
  color: var(--blog-ink-mute);
  font-variant-numeric: tabular-nums;
}

.tag-cloud__empty {
  color: var(--blog-ink-mute);
  font-size: 13px;
}
</style>
