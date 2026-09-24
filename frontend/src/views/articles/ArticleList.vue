<template>
  <div class="article-list page-stack">
    <PageHeader title="文章管理" description="撰写、发布与管理你的文章" />

    <el-card>
      <PageToolbar>
        <template #info>共 {{ total }} 篇文章</template>
        <el-select v-model="status" placeholder="全部状态" clearable style="width: 150px" @change="onSearch">
          <el-option
            v-for="(label, value) in ARTICLE_STATUS"
            :key="value"
            :label="label"
            :value="Number(value)"
          />
        </el-select>
        <el-button type="primary" @click="goCreate">
          <AppIcon name="plus" :size="15" />新建文章
        </el-button>
      </PageToolbar>

      <el-table :data="articles" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ ARTICLE_STATUS[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="阅读量" width="100" align="right" />
        <el-table-column prop="like_count" label="点赞" width="90" align="right" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goEdit(row.id)">
              <AppIcon name="edit" :size="14" />编辑
            </el-button>
            <el-button v-if="row.status === 0" link type="success" @click="onPublish(row.id)">
              <AppIcon name="arrow-up" :size="14" />发布
            </el-button>
            <el-button v-if="row.status === 1" link type="warning" @click="onUnpublish(row.id)">
              <AppIcon name="arrow-down" :size="14" />下架
            </el-button>
            <el-button link type="danger" @click="onDelete(row.id)">
              <AppIcon name="trash" :size="14" />删除
            </el-button>
          </template>
        </el-table-column>

        <template #empty>
          <EmptyState description="还没有文章" hint="点击「新建文章」开始写作" />
        </template>
      </el-table>

      <Pagination
        :page="page"
        :page-size="pageSize"
        :total="total"
        @update:page="onPageChange"
        @update:page-size="onSizeChange"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import PageToolbar from '@/components/PageToolbar.vue'
import Pagination from '@/components/Pagination.vue'
import EmptyState from '@/components/EmptyState.vue'
import AppIcon from '@/components/AppIcon.vue'
import { getMyArticles, deleteArticle, publishArticle, unpublishArticle } from '@/api/article'
import type { Article } from '@/types/article'
import { ARTICLE_STATUS } from '@/utils/constants'

const router = useRouter()
const loading = ref(false)
const articles = ref<Article[]>([])
const status = ref<number | undefined>(undefined)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function load() {
  loading.value = true
  try {
    const data = await getMyArticles({
      page: page.value,
      page_size: pageSize.value,
      status: normalizedStatus()
    })
    articles.value = data.items
    total.value = data.total
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

/** el-select 清空后值为 ''，统一归一化为 undefined，避免把空串传给后端 */
function normalizedStatus(): number | undefined {
  const value = status.value as number | string | undefined | null
  if (value === '' || value === undefined || value === null) return undefined
  return Number(value)
}

function onSearch() {
  page.value = 1
  load()
}

function statusTagType(value: number) {
  return value === 1 ? 'success' : value === 2 ? 'info' : 'warning'
}
function goCreate() {
  router.push('/articles/new')
}
function goEdit(id: number) {
  router.push(`/articles/${id}/edit`)
}
async function onPublish(id: number) {
  await publishArticle(id)
  ElMessage.success('发布成功')
  load()
}
async function onUnpublish(id: number) {
  await unpublishArticle(id)
  ElMessage.success('已下架')
  load()
}
async function onDelete(id: number) {
  await deleteArticle(id)
  ElMessage.success('删除成功')
  load()
}
function onPageChange(value: number) {
  page.value = value
  load()
}
function onSizeChange(value: number) {
  pageSize.value = value
  load()
}

onMounted(load)
</script>
