<template>
  <el-button
    :type="favorited ? 'warning' : 'default'"
    :loading="loading"
    :size="size"
    plain
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
