<template>
  <div class="article-list">
    <PageHeader title="文章管理">
      <template #extra>
        <el-button type="primary" @click="goCreate">新建文章</el-button>
      </template>
    </PageHeader>

    <el-card>
      <div class="article-list__filters">
        <el-select v-model="status" placeholder="状态筛选" clearable style="width: 160px">
          <el-option v-for="(label, value) in ARTICLE_STATUS" :key="value" :label="label" :value="Number(value)" />
        </el-select>
        <el-button type="primary" @click="load">查询</el-button>
      </div>

      <el-table :data="articles" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ ARTICLE_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="阅读量" width="100" />
        <el-table-column prop="like_count" label="点赞" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goEdit(row.id)">编辑</el-button>
            <el-button v-if="row.status === 0" link type="success" @click="onPublish(row.id)">发布</el-button>
            <el-button v-if="row.status === 1" link type="warning" @click="onUnpublish(row.id)">下架</el-button>
            <el-button link type="danger" @click="onDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
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
import Pagination from '@/components/Pagination.vue'
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
    const data = await getMyArticles({ page: page.value, page_size: pageSize.value, status: status.value })
    articles.value = data.items
    total.value = data.total
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
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

<style scoped lang="scss">
.article-list__filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
</style>
