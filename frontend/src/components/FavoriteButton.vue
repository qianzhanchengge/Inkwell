<template>
  <button
    type="button"
    class="blog-btn favorite-button"
    :class="[favorited ? 'blog-btn--active' : 'blog-btn--ghost', sizeClass]"
    :disabled="loading"
    :aria-pressed="favorited"
    @click="onClick"
  >
    <span v-if="loading" class="blog-btn__spinner" aria-hidden="true"></span>
    <AppIcon v-else name="bookmark" :size="15" :class="{ 'is-filled': favorited }" />
    {{ favorited ? '已收藏' : '收藏' }}
  </button>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppIcon from '@/components/AppIcon.vue'
import { toggleFavorite } from '@/api/favorite'
import { useLogin } from '@/composables/useLogin'

const props = withDefaults(
  defineProps<{
    articleId: number
    favorited?: boolean
    size?: 'small' | 'default' | 'large'
  }>(),
  { favorited: false, size: 'default' }
)

const emit = defineEmits<{
  (e: 'change', value: { favorited: boolean }): void
}>()

const { ensureLogin } = useLogin()
const loading = ref(false)
const favorited = ref(props.favorited)

const sizeClass = computed(() => (props.size === 'small' ? 'blog-btn--sm' : ''))

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
/* 已收藏时图标填充，强化状态 */
.is-filled {
  :deep(path) {
    fill: currentColor;
  }
}

.blog-btn__spinner {
  width: 13px;
  height: 13px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: favorite-spin 0.7s linear infinite;
}

@keyframes favorite-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .blog-btn__spinner {
    animation: none;
  }
}
</style>
