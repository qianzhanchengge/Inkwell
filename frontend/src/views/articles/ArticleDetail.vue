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
        <MarkdownPreview :content="article.content" />
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import MarkdownPreview from '@/components/MarkdownPreview.vue'
import { getArticle } from '@/api/article'
import type { Article } from '@/types/article'
import { formatDateTime } from '@/utils/format'

const route = useRoute()
const loading = ref(false)
const article = ref<Article | null>(null)
// 公开浏览与个人管理共用本页：返回目标跟随路由前缀
const backTo = computed(() => (route.path.startsWith('/p/') ? '/p/articles' : '/articles'))

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
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.3;
  color: var(--blog-ink);
}

.article-detail__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  font-size: 13px;
  color: var(--blog-ink-mute);
  font-variant-numeric: tabular-nums;
}

.article-detail__meta span + span::before {
  content: '·';
  margin-right: 10px;
  color: var(--blog-ink-mute);
}

.article-detail__summary {
  padding: 12px 14px;
  margin-bottom: 18px;
  font-size: 14px;
  color: var(--blog-ink-soft);
  background: var(--blog-accent-soft);
  border-left: 3px solid var(--blog-accent);
  border-radius: var(--blog-radius-sm);
}

.article-detail__actions {
  margin-bottom: 16px;
}

.article-detail__content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--blog-ink-soft);
}
</style>
