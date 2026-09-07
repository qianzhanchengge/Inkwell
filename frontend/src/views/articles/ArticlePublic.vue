<template>
  <div class="article-public">
    <h1 class="article-public__title">文章广场</h1>
    <el-card v-loading="loading">
      <el-table :data="articles" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="240">
          <template #default="{ row }">
            <router-link :to="`/p/articles/${row.id}`">{{ row.title }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="summary" label="摘要" min-width="280" show-overflow-tooltip />
        <el-table-column prop="view_count" label="阅读量" width="100" />
        <el-table-column label="发布时间" width="180">
          <template #default="{ row }">{{ formatDateTime(row.published_at) }}</template>
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
import Pagination from '@/components/Pagination.vue'
import { getArticleList } from '@/api/article'
import type { Article } from '@/types/article'
import { formatDateTime } from '@/utils/format'

const loading = ref(false)
const articles = ref<Article[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function load() {
  loading.value = true
  try {
    const data = await getArticleList({ page: page.value, page_size: pageSize.value })
    articles.value = data.items
    total.value = data.total
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
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
.article-public {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 16px;
}
.article-public__title {
  margin: 0 0 16px;
  font-size: 24px;
}
</style>
