<template>
  <div class="article-detail">
    <PageHeader title="文章详情" show-back :back-to="backTo" />
    <el-card v-loading="loading">
      <template v-if="article">
        <h1 class="article-detail__title">{{ article.title }}</h1>
        <div class="article-detail__meta">
          <span v-if="article.published_at">发布于 {{ formatDateTime(article.published_at) }}</span>
          <span>阅读 {{ article.view_count }}</span>
          <span>点赞 {{ article.like_count }}</span>
        </div>
        <div v-if="article.summary" class="article-detail__summary">{{ article.summary }}</div>
        <div class="article-detail__actions">
          <el-button
            :type="liked ? 'danger' : 'default'"
            :loading="liking"
            @click="onLike"
          >
            {{ liked ? '取消点赞' : '点赞' }}
          </el-button>
        </div>
        <MarkdownPreview :content="article.content" />
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import MarkdownPreview from '@/components/MarkdownPreview.vue'
import { getArticle, toggleArticleLike } from '@/api/article'
import type { Article } from '@/types/article'
import { formatDateTime } from '@/utils/format'

const route = useRoute()
const loading = ref(false)
const liking = ref(false)
const liked = ref(false)
const article = ref<Article | null>(null)
// 公开浏览与个人管理共用本页：返回目标跟随路由前缀
const backTo = computed(() => (route.path.startsWith('/p/') ? '/p/articles' : '/articles'))

async function load() {
  loading.value = true
  try {
    article.value = await getArticle(route.params.id as string)
    liked.value = article.value?.is_liked ?? false
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

async function onLike() {
  if (!article.value) return
  liking.value = true
  try {
    const res = await toggleArticleLike(article.value.id)
    article.value.like_count = res.like_count
    article.value.is_liked = res.liked
    liked.value = res.liked
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    liking.value = false
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
.article-detail__actions {
  margin-bottom: 16px;
}
.article-detail__content {
  line-height: 1.8;
}
</style>
