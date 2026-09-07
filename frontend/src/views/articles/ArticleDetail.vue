<template>
  <div class="article-detail">
    <el-card v-loading="loading">
      <template v-if="article">
        <h1 class="article-detail__title">{{ article.title }}</h1>
        <div class="article-detail__meta">
          <span v-if="article.published_at">发布于 {{ formatDateTime(article.published_at) }}</span>
          <span>阅读 {{ article.view_count }}</span>
          <span>点赞 {{ article.like_count }}</span>
        </div>
        <div v-if="article.summary" class="article-detail__summary">{{ article.summary }}</div>
        <div class="article-detail__content" v-html="article.content_html || article.content"></div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getArticle } from '@/api/article'
import type { Article } from '@/types/article'
import { formatDateTime } from '@/utils/format'

const route = useRoute()
const loading = ref(false)
const article = ref<Article | null>(null)

async function load() {
  loading.value = true
  try {
    article.value = await getArticle(route.params.id as string)
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.article-detail__title {
  margin: 0 0 12px;
}
.article-detail__meta {
  display: flex;
  gap: 16px;
  color: #909399;
  font-size: 13px;
  margin-bottom: 16px;
}
.article-detail__summary {
  color: #606266;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}
.article-detail__content {
  line-height: 1.8;
}
</style>
