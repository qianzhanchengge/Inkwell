<template>
  <div class="article-editor">
    <PageHeader :title="isEdit ? '编辑文章' : '新建文章'" />

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
          <el-button type="primary" :loading="saving" @click="onSave">保存草稿</el-button>
          <el-button type="success" :loading="publishing" @click="onPublish">发布</el-button>
          <el-button @click="goBack">取消</el-button>
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
import { createArticle, updateArticle, getArticle, publishArticle } from '@/api/article'
import { getCategoryList } from '@/api/category'
import { getTagList } from '@/api/tag'
import type { Category, Tag } from '@/types/api'

const route = useRoute()
const router = useRouter()
const saving = ref(false)
const publishing = ref(false)
const categories = ref<Category[]>([])
const tagOptions = ref<Tag[]>([])
const form = reactive({
  title: '',
  summary: '',
  content: '',
  cover_image: '',
  category_id: undefined as number | undefined,
  tags: [] as string[]
})

const isEdit = computed(() => !!route.params.id)

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
