<template>
  <article class="article-card">
    <router-link :to="`/blog/articles/${article.id}`" class="article-card__link">
      <div v-if="article.cover_image" class="article-card__cover">
        <img :src="article.cover_image" :alt="article.title" loading="lazy" />
      </div>
      <h3 class="article-card__title">{{ article.title }}</h3>
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
  </article>
</template>

<script setup lang="ts">
import type { Article } from '@/types/article'
import { formatDate } from '@/utils/format'

defineProps<{ article: Article }>()
</script>

<style scoped lang="scss">
.article-card {
  background: var(--blog-surface);
  border-radius: var(--blog-radius);
  box-shadow: var(--blog-shadow-sm);
  padding: 20px 22px;
  margin-bottom: 18px;
  transition: box-shadow 0.25s ease, transform 0.25s ease;
}

/* 悬停与键盘聚焦都给出抬升反馈 */
.article-card:hover,
.article-card:focus-within {
  box-shadow: var(--blog-shadow-lg);
  transform: translateY(-2px);
}

.article-card__link {
  display: block;
}

.article-card__cover {
  margin-bottom: 14px;
}

.article-card__cover img {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  border-radius: var(--blog-radius-sm);
}

.article-card__title {
  margin: 0 0 8px;
  font-size: 19px;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: -0.01em;
  color: var(--blog-ink);
  transition: color 0.2s;
  text-wrap: balance;
}

.article-card__link:hover .article-card__title {
  color: var(--blog-accent);
}

.article-card__summary {
  margin: 0 0 14px;
  color: var(--blog-ink-soft);
  font-size: 14px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-card__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  color: var(--blog-ink-mute);
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}

/* 元信息之间用中点分隔，而不是靠大间距硬撑 */
.article-card__meta > span + span::before {
  content: '·';
  margin: 0 7px;
  opacity: 0.55;
}

.article-card__author {
  color: var(--blog-ink-soft);
}
</style>
