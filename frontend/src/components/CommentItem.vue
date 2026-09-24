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
        <button
          type="button"
          class="blog-btn blog-btn--sm blog-btn--ghost comment-item__like"
          :class="{ 'blog-btn--active': comment.is_liked }"
          :disabled="liking"
          :aria-pressed="comment.is_liked"
          @click="onLike"
        >
          <AppIcon name="heart" :size="13" :class="{ 'is-filled': comment.is_liked }" />
          {{ comment.is_liked ? '取消赞' : '赞' }}{{ comment.like_count ? ` ${comment.like_count}` : '' }}
        </button>
        <button type="button" class="blog-btn__plain" @click="emit('reply', comment)">
          <AppIcon name="comment" :size="13" />
          回复
        </button>
        <button
          v-if="canDelete"
          type="button"
          class="blog-btn__plain comment-item__del"
          @click="emit('delete', comment)"
        >
          <AppIcon name="trash" :size="13" />
          删除
        </button>
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
import AppIcon from '@/components/AppIcon.vue'
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
  padding: 14px 0;
  border-bottom: 1px solid var(--blog-line);
}
.comment-item__avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--blog-accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
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
  font-size: 14px;
  font-weight: 600;
  color: var(--blog-ink);
}
.comment-item__replyto {
  color: var(--blog-ink-mute);
  font-size: 12px;
}
.comment-item__time {
  color: var(--blog-ink-mute);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}
.comment-item__content {
  color: var(--blog-ink-soft);
  font-size: 15px;
  line-height: 1.7;
  margin: 6px 0 8px;
  white-space: pre-wrap;
  word-break: break-word;
}
.comment-item__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 删除：悬停时用强调色而非刺眼的正红 */
.comment-item__del:hover {
  color: var(--blog-accent);
  background: var(--blog-accent-soft);
}

.is-filled {
  :deep(path) {
    fill: currentColor;
  }
}

/* 子回复：用左侧竖线形成层级，替代纯缩进 */
.comment-item__children {
  margin-top: 8px;
  padding-left: 12px;
  border-left: 2px solid var(--blog-line);
}
</style>
