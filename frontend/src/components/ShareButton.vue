<template>
  <el-button class="share-button" :size="size" @click="onClick">分享</el-button>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { recordShare } from '@/api/share'
import { useBlogUserStore } from '@/stores/blogUser'

const props = withDefaults(
  defineProps<{
    articleId: number
    size?: 'small' | 'default' | 'large'
  }>(),
  { size: 'small' }
)

const blogUserStore = useBlogUserStore()

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
    ElMessage.success('文章链接已复制')
  } else {
    ElMessage.warning('复制失败，请手动复制地址栏链接')
  }
  // 已登录博客账号时记录分享统计（静默，不阻塞）
  if (blogUserStore.token) {
    recordShare(props.articleId).catch(() => {})
  }
}
</script>

<style scoped lang="scss">
.share-button {
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
}
</style>
