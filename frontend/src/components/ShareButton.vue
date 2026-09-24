<template>
  <button
    type="button"
    class="blog-btn blog-btn--ghost share-button"
    :class="sizeClass"
    @click="onClick"
  >
    <AppIcon :name="copied ? 'link' : 'share'" :size="15" />
    {{ copied ? '已复制' : '分享' }}
  </button>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import AppIcon from '@/components/AppIcon.vue'
import { recordShare } from '@/api/share'
import { useBlogUserStore } from '@/stores/blogUser'

const props = withDefaults(
  defineProps<{
    articleId: number
    size?: 'small' | 'default' | 'large'
  }>(),
  { size: 'default' }
)

const blogUserStore = useBlogUserStore()
const copied = ref(false)
const sizeClass = computed(() => (props.size === 'small' ? 'blog-btn--sm' : ''))

let resetTimer: number | undefined

async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    // 非安全上下文回退：临时 textarea
    try {
      const ta = document.createElement('textarea')
      ta.value = text
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.select()
      const ok = document.execCommand('copy')
      document.body.removeChild(ta)
      return ok
    } catch {
      return false
    }
  }
}

async function onClick() {
  const url = window.location.href
  const ok = await copyText(url)
  if (ok) {
    copied.value = true
    window.clearTimeout(resetTimer)
    resetTimer = window.setTimeout(() => (copied.value = false), 1600)
  } else {
    ElMessage.warning('复制失败，请手动复制地址栏链接')
  }
  // 已登录博客账号时记录分享统计（静默，不阻塞）
  if (blogUserStore.token) {
    recordShare(props.articleId).catch(() => {})
  }
}

onUnmounted(() => {
  window.clearTimeout(resetTimer)
})
</script>
