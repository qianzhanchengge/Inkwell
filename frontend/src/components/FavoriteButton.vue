<template>
  <el-button
    class="favorite-button"
    :class="{ 'is-active': favorited }"
    :loading="loading"
    :size="size"
    @click="onClick"
  >
    {{ favorited ? '已收藏' : '收藏' }}
  </el-button>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { toggleFavorite } from '@/api/favorite'
import { useLogin } from '@/composables/useLogin'

const props = withDefaults(
  defineProps<{
    articleId: number
    favorited?: boolean
    size?: 'small' | 'default' | 'large'
  }>(),
  { favorited: false, size: 'small' }
)

const emit = defineEmits<{
  (e: 'change', value: { favorited: boolean }): void
}>()

const { ensureLogin } = useLogin()
const loading = ref(false)
const favorited = ref(props.favorited)

watch(
  () => props.favorited,
  (v) => (favorited.value = v)
)
async function onClick() {
  const ok = await ensureLogin()
  if (!ok) return
  loading.value = true
  try {
    const res = await toggleFavorite(props.articleId)
    favorited.value = res.favorited
    emit('change', { favorited: res.favorited })
  } catch {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.favorite-button {
  border-radius: var(--blog-radius-sm);
  background: var(--blog-paper);
  border-color: var(--blog-line);
  color: var(--blog-ink-soft);
  transition: background 0.2s, border-color 0.2s, color 0.2s, transform 0.15s;

  &:hover {
    border-color: var(--blog-accent);
    color: var(--blog-accent);
    background: var(--blog-paper);
  }

  &:active {
    transform: translateY(1px);
  }

  &.is-active {
    background: var(--blog-accent-soft);
    border-color: var(--blog-accent-soft);
    color: var(--blog-accent);
  }
}
</style>
