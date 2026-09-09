<template>
  <div class="note-editor">
    <PageHeader :title="isEdit ? '编辑笔记' : '新建笔记'" />

    <el-card>
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" clearable style="width: 240px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <TagSelector v-model="form.tags" :tags="tagOptions" />
        </el-form-item>
        <el-form-item label="内容">
          <MarkdownEditor v-model="form.content" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.is_pinned">置顶</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
          <el-button @click="triggerFileInput">📄 导入本地 MD 文件</el-button>
          <el-button @click="goBack">取消</el-button>
          <input
            ref="fileInput"
            type="file"
            accept=".md,.markdown,.txt,text/markdown"
            style="display: none"
            @change="onImportFile"
          />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import TagSelector from '@/components/TagSelector.vue'
import { createNote, updateNote, getNote } from '@/api/note'
import { getCategoryList } from '@/api/category'
import { getTagList } from '@/api/tag'
import type { Category, Tag } from '@/types/api'

const route = useRoute()
const router = useRouter()
const saving = ref(false)
const categories = ref<Category[]>([])
const tagOptions = ref<Tag[]>([])
const form = reactive({
  title: '',
  content: '',
  category_id: undefined as number | undefined,
  tags: [] as string[],
  is_pinned: false
})

const isEdit = computed(() => !!route.params.id && route.path.includes('/edit'))

const fileInput = ref<HTMLInputElement | null>(null)

function triggerFileInput() {
  fileInput.value?.click()
}

/** 从 Markdown 内容提取首个一级标题作为笔记标题 */
function extractTitleFromMd(md: string): string {
  const m = md.match(/^#\s+(.+)$/m)
  return m ? m[1].trim() : ''
}

/** 导入本地 .md 文件：内容填入编辑器，标题为空时自动取首个 # 标题 */
async function onImportFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('文件过大（最大 2MB）')
    input.value = ''
    return
  }
  const text = await file.text()
  if (!text.trim()) {
    ElMessage.warning('文件内容为空')
    input.value = ''
    return
  }
  form.content = text
  if (!form.title) {
    form.title = extractTitleFromMd(text)
  }
  ElMessage.success(`已导入「${file.name}」`)
  input.value = ''
}

async function loadMeta() {
  categories.value = await getCategoryList(1)
  tagOptions.value = await getTagList()
}

async function loadNote() {
  if (!isEdit.value) return
  const note = await getNote(route.params.id as string)
  form.title = note.title
  form.content = note.content
  form.category_id = note.category?.id
  form.tags = (note.tags || []).map((t) => t.name)
  form.is_pinned = note.is_pinned
}

async function onSave() {
  saving.value = true
  try {
    if (isEdit.value) {
      await updateNote(route.params.id as string, form)
    } else {
      await createNote(form)
    }
    ElMessage.success('保存成功')
    router.push('/notes')
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push('/notes')
}

onMounted(() => {
  loadMeta()
  loadNote()
})
</script>
