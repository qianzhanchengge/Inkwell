<template>
  <div class="comment-item">
    <div class="comment-item__avatar">{{ avatarText }}</div>
    <div class="comment-item__body">
      <div class="comment-item__head">
        <span class="comment-item__nick">{{ nickname }}</span>
        <span v-if="comment.reply_to_author?.nickname" class="comment-item__replyto">
          回复 @{{ comment.reply_to_author.nickname }}
        </span>
        <span class="comment-item__time">{{ formatDateTime(comment.created_at) }}</span>
      </div>
      <div class="comment-item__content">{{ comment.content }}</div>
      <div class="comment-item__actions">
        <el-button link size="small" :loading="liking" @click="onLike">
          {{ comment.is_liked ? '取消赞' : '赞' }}{{ comment.like_count ? ` ${comment.like_count}` : '' }}
        </el-button>
        <el-button link size="small" @click="emit('reply', comment)">回复</el-button>
        <el-button
          v-if="canDelete"
          link
          size="small"
          type="danger"
          @click="emit('delete', comment)"
        >
          删除
        </el-button>
      </div>
      <div v-if="children.length" class="comment-item__children">
        <CommentItem
          v-for="child in children"
          :key="child.id"
          :comment="child"
          :children-map="childrenMap"
          :current-user-id="currentUserId"
          @reply="(c) => emit('reply', c)"
          @delete="(c) => emit('delete', c)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { toggleCommentLike } from '@/api/comment'
import { useLogin } from '@/composables/useLogin'
import type { Comment } from '@/types/comment'
import { formatDateTime } from '@/utils/format'

const props = defineProps<{
  comment: Comment
  childrenMap: Record<number, Comment[]>
  currentUserId: number | null
}>()

const emit = defineEmits<{
  (e: 'reply', comment: Comment): void
  (e: 'delete', comment: Comment): void
}>()

const { ensureLogin } = useLogin()
const liking = ref(false)

const children = computed(() => props.childrenMap[props.comment.id] || [])

const nickname = computed(() => props.comment.author?.nickname || `用户${props.comment.user_id}`)
const avatarText = computed(() => (nickname.value || 'U').slice(0, 1).toUpperCase())
const canDelete = computed(
  () => props.currentUserId != null && props.comment.user_id === props.currentUserId
)

async function onLike() {
  const ok = await ensureLogin()
  if (!ok) return
  liking.value = true
  try {
    const res = await toggleCommentLike(props.comment.id)
    props.comment.is_liked = res.liked
    props.comment.like_count = res.like_count
  } catch {
    // 错误提示已统一处理
  } finally {
    liking.value = false
  }
}
</script>

<style scoped lang="scss">
.comment-item {
  display: flex;
  gap: 10px;
  padding: 12px 0;
}
.comment-item__avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.comment-item__body {
  flex: 1;
  min-width: 0;
}
.comment-item__head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.comment-item__nick {
  font-weight: 500;
  color: #303133;
}
.comment-item__replyto {
  color: #909399;
  font-size: 12px;
}
.comment-item__time {
  color: #c0c4cc;
  font-size: 12px;
}
.comment-item__content {
  color: #303133;
  margin: 6px 0;
  white-space: pre-wrap;
  word-break: break-word;
}
.comment-item__actions {
  display: flex;
  gap: 4px;
}
.comment-item__children {
  margin-top: 8px;
  padding-left: 12px;
  border-left: 2px solid #f0f2f5;
}
</style>
