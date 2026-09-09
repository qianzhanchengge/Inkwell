<template>
  <el-card class="article-card" shadow="hover" :body-style="{ padding: '16px' }">
    <div v-if="article.cover_image" class="article-card__cover">
      <img :src="article.cover_image" :alt="article.title" />
    </div>
    <router-link :to="`/blog/articles/${article.id}`" class="article-card__title">
      {{ article.title }}
    </router-link>
    <p v-if="article.summary" class="article-card__summary">{{ article.summary }}</p>
    <div class="article-card__meta">
      <span v-if="article.author?.nickname" class="article-card__author">
        {{ article.author.nickname }}
      </span>
      <span>阅读 {{ article.view_count }}</span>
      <span>点赞 {{ article.like_count }}</span>
      <span v-if="article.comment_count != null">评论 {{ article.comment_count }}</span>
      <span v-if="article.published_at">{{ formatDate(article.published_at) }}</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { Article } from '@/types/article'
import { formatDate } from '@/utils/format'

defineProps<{ article: Article }>()
</script>

<style scoped lang="scss">
.article-card {
  margin-bottom: 16px;
}
.article-card__cover img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 12px;
}
.article-card__title {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  &:hover {
    color: #409eff;
  }
}
.article-card__summary {
  color: #909399;
  font-size: 13px;
  line-height: 1.6;
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.article-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: #c0c4cc;
  font-size: 12px;
}
.article-card__author {
  color: #909399;
}
</style>
