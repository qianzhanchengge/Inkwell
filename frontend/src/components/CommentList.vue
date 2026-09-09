<template>
  <div class="comment-list">
    <template v-if="topLevel.length">
      <CommentItem
        v-for="c in topLevel"
        :key="c.id"
        :comment="c"
        :children-map="childrenMap"
        :current-user-id="currentUserId"
        @reply="(comment) => emit('reply', comment)"
        @delete="(comment) => emit('delete', comment)"
      />
    </template>
    <el-empty v-else description="暂无评论" :image-size="60" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CommentItem from './CommentItem.vue'
import type { Comment } from '@/types/comment'

const props = defineProps<{
  comments: Comment[]
  currentUserId: number | null
}>()

const emit = defineEmits<{
  (e: 'reply', comment: Comment): void
  (e: 'delete', comment: Comment): void
}>()

const childrenMap = computed<Record<number, Comment[]>>(() => {
  const map: Record<number, Comment[]> = {}
  for (const c of props.comments) {
    if (c.parent_id != null) {
      ;(map[c.parent_id] ||= []).push(c)
    }
  }
  return map
})

const topLevel = computed(() => props.comments.filter((c) => c.parent_id == null))
</script>

<style scoped>
.comment-list {
  margin-top: 8px;
}
</style>
