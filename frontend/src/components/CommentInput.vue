<template>
  <div class="comment-input">
    <div v-if="replyTo" class="comment-input__reply">
      回复 @{{ replyNickname }}
      <el-button link size="small" @click="emit('cancel-reply')">取消回复</el-button>
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
      <el-button type="primary" :loading="submitting" :disabled="!content.trim()" @click="onSubmit">
        发表评论
      </el-button>
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

  :deep(.el-button) {
    transition: color 0.2s, transform 0.15s;
  }
}
.comment-input__reply {
  font-size: 13px;
  color: var(--blog-ink-mute);
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.comment-input__actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}
</style>
