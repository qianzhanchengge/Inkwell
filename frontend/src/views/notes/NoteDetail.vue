<template>
  <div class="note-detail">
    <PageHeader title="笔记详情" show-back back-to="/notes">
      <template #extra>
        <el-button @click="downloadNote">下载</el-button>
        <el-button @click="goEdit">编辑</el-button>
      </template>
    </PageHeader>

    <el-card v-loading="loading">
      <template v-if="note">
        <h2 class="note-detail__title">{{ note.title }}</h2>
        <div class="note-detail__meta">
          <el-tag v-if="note.is_pinned" type="warning" size="small">置顶</el-tag>
          <span v-if="note.category" class="note-detail__category">{{ note.category.name }}</span>
          <span class="note-detail__time">{{ formatDateTime(note.updated_at) }}</span>
        </div>
        <div v-if="note.tags?.length" class="note-detail__tags">
          <el-tag v-for="tag in note.tags" :key="tag.id" size="small">{{ tag.name }}</el-tag>
        </div>
        <div class="note-detail__content">
          <MarkdownPreview :content="note.content" />
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import MarkdownPreview from '@/components/MarkdownPreview.vue'
import { getNote } from '@/api/note'
import type { Note } from '@/types/note'
import { formatDateTime } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const note = ref<Note | null>(null)

async function load() {
  loading.value = true
  try {
    note.value = await getNote(route.params.id as string)
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

function goEdit() {
  router.push(`/notes/${route.params.id}/edit`)
}

/**
 * 下载笔记为 Markdown 文件。
 * 优先使用文件系统访问 API（可让用户选择保存位置，需 HTTPS 或 localhost）；
 * 不可用时回退到浏览器默认下载（保存位置由浏览器设置决定）。
 */
async function downloadNote() {
  if (!note.value) return
  const safeTitle = (note.value.title || '笔记').replace(/[\\/:*?"<>|]/g, '_').slice(0, 80)
  const filename = `${safeTitle}.md`
  const blob = new Blob([note.value.content || ''], {
    type: 'text/markdown;charset=utf-8'
  })

  const picker = (
    window as unknown as {
      showSaveFilePicker?: (options?: unknown) => Promise<{
        createWritable: () => Promise<{
          write: (data: Blob) => Promise<void>
          close: () => Promise<void>
        }>
      }>
    }
  ).showSaveFilePicker

  if (typeof picker === 'function') {
    try {
      const handle = await picker({
        suggestedName: filename,
        types: [{ description: 'Markdown 文件', accept: { 'text/markdown': ['.md'] } }]
      })
      const writable = await handle.createWritable()
      await writable.write(blob)
      await writable.close()
      ElMessage.success('笔记已保存')
      return
    } catch (e) {
      if ((e as { name?: string })?.name === 'AbortError') return // 用户取消选择
      // 其他异常：回退到浏览器默认下载
    }
  }

  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  ElMessage.success('已开始下载')
}

onMounted(load)
</script>

<style scoped lang="scss">
.note-detail__title {
  margin: 0 0 12px;
}
.note-detail__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 13px;
  margin-bottom: 12px;
}
.note-detail__tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.note-detail__content {
  line-height: 1.7;
}
</style>
