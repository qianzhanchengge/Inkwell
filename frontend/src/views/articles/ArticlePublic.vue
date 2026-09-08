<template>
  <div class="article-public">
    <h1 class="article-public__title">文章广场</h1>

    <div v-loading="loading" class="article-public__grid">
      <el-card
        v-for="article in articles"
        :key="article.id"
        class="article-public__card"
        shadow="hover"
      >
        <div v-if="article.cover_image" class="article-public__cover">
          <img :src="article.cover_image" :alt="article.title" />
        </div>
        <router-link :to="`/p/articles/${article.id}`" class="article-public__link">
          {{ article.title }}
        </router-link>
        <p class="article-public__summary">{{ article.summary || '暂无摘要' }}</p>
        <div class="article-public__meta">
          <span>阅读 {{ article.view_count }}</span>
          <span>点赞 {{ article.like_count }}</span>
          <span v-if="article.published_at">{{ formatDateTime(article.published_at) }}</span>
        </div>
      </el-card>

      <el-empty v-if="!loading && articles.length === 0" description="暂无文章" />
    </div>

    <Pagination
      :page="page"
      :page-size="pageSize"
      :total="total"
      @update:page="onPageChange"
      @update:page-size="onSizeChange"
    />
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
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px 16px;
}
.article-public__title {
  margin: 0 0 16px;
  font-size: 24px;
}
.article-public__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
.article-public__card {
  display: flex;
  flex-direction: column;
}
.article-public__cover img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 12px;
}
.article-public__link {
  font-size: 17px;
  font-weight: 600;
  color: #303133;
  text-decoration: none;
  margin-bottom: 8px;
  &:hover {
    color: #409eff;
  }
}
.article-public__summary {
  color: #909399;
  font-size: 13px;
  line-height: 1.6;
  min-height: 40px;
  margin: 0 0 12px;
}
.article-public__meta {
  display: flex;
  gap: 12px;
  color: #c0c4cc;
  font-size: 12px;
}
</style>
