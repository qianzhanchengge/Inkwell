<template>
  <button
    type="button"
    class="blog-btn like-button"
    :class="[liked ? 'blog-btn--active' : 'blog-btn--ghost', sizeClass]"
    :disabled="loading"
    :aria-pressed="liked"
    @click="onClick"
  >
    <span v-if="loading" class="blog-btn__spinner" aria-hidden="true"></span>
    <AppIcon v-else name="heart" :size="15" :class="{ 'is-filled': liked }" />
    {{ liked ? '已赞' : '点赞' }}{{ likeCount > 0 ? ` ${likeCount}` : '' }}
  </button>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppIcon from '@/components/AppIcon.vue'
import { toggleBlogArticleLike } from '@/api/blogArticle'
import { useLogin } from '@/composables/useLogin'

const props = withDefaults(
  defineProps<{
    articleId: number
    liked?: boolean
    likeCount?: number
    size?: 'small' | 'default' | 'large'
  }>(),
  { liked: false, likeCount: 0, size: 'default' }
)

const emit = defineEmits<{
  (e: 'change', value: { liked: boolean; like_count: number }): void
}>()

const { ensureLogin } = useLogin()
const loading = ref(false)
const liked = ref(props.liked)
const likeCount = ref(props.likeCount)

const sizeClass = computed(() => (props.size === 'small' ? 'blog-btn--sm' : ''))

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
    const res = await toggleBlogArticleLike(props.articleId)
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

<style scoped lang="scss">
/* 已赞时图标填充，强化状态 */
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
  animation: like-spin 0.7s linear infinite;
}

@keyframes like-spin {
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
