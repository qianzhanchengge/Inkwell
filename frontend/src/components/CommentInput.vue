<template>
  <div class="comment-input">
    <div v-if="replyTo" class="comment-input__reply">
      <span>回复 @{{ replyNickname }}</span>
      <button type="button" class="blog-btn__plain" @click="emit('cancel-reply')">取消回复</button>
    </div>
    <el-input
      v-model="content"
      type="textarea"
      :rows="3"
      maxlength="2000"
      show-word-limit
      placeholder="写下你的评论…"
    />
    <div class="comment-input__actions">
      <button
        type="button"
        class="blog-btn blog-btn--primary blog-btn--sm"
        :disabled="submitting || !content.trim()"
        @click="onSubmit"
      >
        <span v-if="submitting" class="comment-input__spinner" aria-hidden="true"></span>
        {{ submitting ? '提交中' : '发表评论' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Comment } from '@/types/comment'

const props = withDefaults(
  defineProps<{
    replyTo?: Comment | null
    submitting?: boolean
  }>(),
  { replyTo: null, submitting: false }
)

const emit = defineEmits<{
  (e: 'submit', content: string): void
  (e: 'cancel-reply'): void
}>()

const content = ref('')

const replyNickname = computed(
  () => props.replyTo?.author?.nickname || `用户${props.replyTo?.user_id ?? ''}`
)

function onSubmit() {
  const text = content.value.trim()
  if (!text) return
  emit('submit', text)
}
</script>

<style scoped lang="scss">
.comment-input {
  margin-top: 16px;

  /* 聚焦时强调色边框 + 柔和外发光 */
  :deep(.el-textarea__inner) {
    border-radius: var(--blog-radius-sm);
    font-size: 14px;
    line-height: 1.7;
    border: 1px solid var(--blog-line);
    box-shadow: none;
    transition: border-color 0.2s, box-shadow 0.2s;

    &:focus {
      border-color: var(--blog-accent);
      box-shadow: 0 0 0 3px var(--blog-accent-soft);
    }
  }

  :deep(.el-input__count) {
    color: var(--blog-ink-mute);
    background: transparent;
  }
}

.comment-input__reply {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--blog-ink-mute);
  margin-bottom: 6px;
}

.comment-input__actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.comment-input__spinner {
  width: 12px;
  height: 12px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: comment-spin 0.7s linear infinite;
}

@keyframes comment-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .comment-input__spinner {
    animation: none;
  }
}
</style>
