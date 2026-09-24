<template>
  <div class="article-editor page-stack">
    <PageHeader :title="isEdit ? '编辑文章' : '新建文章'" show-back back-to="/articles" />

    <el-card>
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="2" placeholder="请输入摘要（可选）" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" clearable style="width: 240px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <TagSelector v-model="form.tags" :tags="tagOptions" />
        </el-form-item>
        <el-form-item label="封面">
          <el-input v-model="form.cover_image" placeholder="封面图 URL（可选）" />
        </el-form-item>
        <el-form-item label="内容">
          <MarkdownEditor v-model="form.content" />
        </el-form-item>
        <el-form-item>
          <div class="editor-actions">
            <el-button @click="goBack">取消</el-button>
            <div class="editor-actions__right">
              <el-button @click="openNotePicker">
                <AppIcon name="doc" :size="15" />从笔记导入
              </el-button>
              <el-button :loading="saving" @click="onSave">保存草稿</el-button>
              <el-button type="primary" :loading="publishing" @click="onPublish">发布</el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <el-dialog v-model="noteDialogVisible" title="从笔记导入" width="560px">
      <el-input
        v-model="noteKeyword"
        placeholder="搜索笔记标题"
        clearable
        style="margin-bottom: 12px"
      />
      <div v-loading="noteLoading" class="note-pick-list">
        <div
          v-for="n in filteredNotes"
          :key="n.id"
          class="note-pick-item"
          @click="pickNote(n.id)"
        >
          <span class="note-pick-title">{{ n.title }}</span>
          <span class="note-pick-time">{{ formatTime(n.updated_at) }}</span>
        </div>
        <el-empty
          v-if="!noteLoading && !filteredNotes.length"
          description="没有可导入的笔记"
          :image-size="60"
        />
      </div>
      <template #footer>
        <el-button @click="noteDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import AppIcon from '@/components/AppIcon.vue'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import TagSelector from '@/components/TagSelector.vue'
import { createArticle, updateArticle, getArticle, publishArticle } from '@/api/article'
import { getCategoryList } from '@/api/category'
import { getTagList } from '@/api/tag'
import { getNoteList, getNote } from '@/api/note'
import type { Category, Tag } from '@/types/api'
import type { Note } from '@/types/note'

const route = useRoute()
const router = useRouter()
const saving = ref(false)
const publishing = ref(false)
const categories = ref<Category[]>([])
const tagOptions = ref<Tag[]>([])
// 从笔记导入
const noteDialogVisible = ref(false)
const noteLoading = ref(false)
const noteKeyword = ref('')
const noteList = ref<Note[]>([])
const filteredNotes = computed(() =>
  noteList.value.filter((n) => n.title.includes(noteKeyword.value.trim()))
)
const form = reactive({
  title: '',
  summary: '',
  content: '',
  cover_image: '',
  category_id: undefined as number | undefined,
  tags: [] as string[]
})

const isEdit = computed(() => !!route.params.id)

async function openNotePicker() {
  noteDialogVisible.value = true
  noteKeyword.value = ''
  if (noteList.value.length) return
  noteLoading.value = true
  try {
    const data = await getNoteList({ page: 1, page_size: 100 })
    noteList.value = data.items
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    noteLoading.value = false
  }
}

function formatTime(v: string | undefined): string {
  if (!v) return ''
  return String(v).replace('T', ' ').slice(0, 16)
}

/** 将 Markdown 粗略转为纯文本摘要 */
function toSummary(md: string, max = 100): string {
  const plain = md
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/[*_>`~-]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
  return plain.slice(0, max)
}

/** 选中笔记 → 取详情，直接填充文章表单（标题/正文/标签/自动摘要） */
async function pickNote(id: number) {
  const note = await getNote(id)
  form.title = note.title
  form.content = note.content
  if (!form.summary) {
    form.summary = toSummary(note.content)
  }
  form.tags = (note.tags || []).map((t) => t.name)
  noteDialogVisible.value = false
  ElMessage.success('已从笔记导入，可继续编辑后保存或发布')
}

async function loadMeta() {
  categories.value = await getCategoryList(2)
  tagOptions.value = await getTagList()
}

async function loadArticle() {
  if (!isEdit.value) return
  const article = await getArticle(route.params.id as string)
  form.title = article.title
  form.summary = article.summary
  form.content = article.content
  form.cover_image = article.cover_image || ''
  form.category_id = article.category?.id
  form.tags = (article.tags || []).map((t) => t.name)
}

async function onSave() {
  if (!form.title || !form.content) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await updateArticle(route.params.id as string, form)
    } else {
      await createArticle(form)
    }
    ElMessage.success('保存成功')
    router.push('/articles')
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    saving.value = false
  }
}

async function onPublish() {
  if (!form.title || !form.content) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  publishing.value = true
  try {
    let id: number
    if (isEdit.value) {
      const res = await updateArticle(route.params.id as string, form)
      id = res.id
    } else {
      const res = await createArticle(form)
      id = res.id
    }
    await publishArticle(id)
    ElMessage.success('发布成功')
    router.push('/articles')
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    publishing.value = false
  }
}

function goBack() {
  router.push('/articles')
}

onMounted(() => {
  loadMeta()
  loadArticle()
})
</script>

<style scoped>
/* 表单底部操作区：左「取消」/ 右主操作 */
.editor-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
}

.editor-actions__right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.note-pick-list {
  max-height: 360px;
  overflow-y: auto;
}
.note-pick-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.note-pick-item:hover {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.note-pick-title {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.note-pick-time {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  flex-shrink: 0;
  margin-left: 12px;
}
</style>
