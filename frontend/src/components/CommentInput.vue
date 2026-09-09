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

<style scoped>
.comment-input {
  margin-top: 16px;
}
.comment-input__reply {
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.comment-input__actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}
</style>
