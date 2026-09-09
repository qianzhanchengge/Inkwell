<template>
  <el-button
    :type="liked ? 'danger' : 'default'"
    :loading="loading"
    :size="size"
    plain
    @click="onClick"
  >
    {{ liked ? '已赞' : '点赞' }}{{ likeCount > 0 ? ` ${likeCount}` : '' }}
  </el-button>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { toggleArticleLike } from '@/api/article'
import { useLogin } from '@/composables/useLogin'

const props = withDefaults(
  defineProps<{
    articleId: number
    liked?: boolean
    likeCount?: number
    size?: 'small' | 'default' | 'large'
  }>(),
  { liked: false, likeCount: 0, size: 'small' }
)

const emit = defineEmits<{
  (e: 'change', value: { liked: boolean; like_count: number }): void
}>()

const { ensureLogin } = useLogin()
const loading = ref(false)
const liked = ref(props.liked)
const likeCount = ref(props.likeCount)

watch(
  () => props.liked,
  (v) => (liked.value = v)
)
watch(
  () => props.likeCount,
  (v) => (likeCount.value = v)
)

async function onClick() {
  const ok = await ensureLogin()
  if (!ok) return
  loading.value = true
  try {
    const res = await toggleArticleLike(props.articleId)
    liked.value = res.liked
    likeCount.value = res.like_count
    emit('change', { liked: res.liked, like_count: res.like_count })
  } catch {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}
</script>
