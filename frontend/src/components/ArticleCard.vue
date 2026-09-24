<template>
  <article class="article-card" :class="`article-card--${variant}`">
    <router-link :to="`/blog/articles/${article.id}`" class="article-card__link">
      <div v-if="article.cover_image" class="article-card__cover">
        <img :src="article.cover_image" :alt="article.title" loading="lazy" />
      </div>
      <div class="article-card__body">
        <h3 class="article-card__title">{{ article.title }}</h3>

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
      </div>
    </router-link>
  </article>
</template>

<script setup lang="ts">
import type { Article } from '@/types/article'
import { formatDate } from '@/utils/format'

withDefaults(
  defineProps<{
    article: Article
    /** default：常规卡；compact：网格内紧凑卡；featured：首页通栏特色卡 */
    variant?: 'default' | 'compact' | 'featured'
  }>(),
  { variant: 'default' }
)
</script>

<style scoped lang="scss">
.article-card {
  position: relative;
  background: var(--blog-surface);
  border-radius: var(--blog-radius);
  box-shadow: var(--blog-shadow-sm);
  padding: 20px 22px;
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
  color: inherit;
}

/* 标题链接的伪元素覆盖整卡热区：整卡可点，同时保留标题作为可访问名称 */
.article-card__link::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--blog-radius);
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

.article-card:hover .article-card__title {
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

/* ---------- default：列表单列 ---------- */
.article-card--default {
  margin-bottom: 18px;

  .article-card__cover {
    margin-bottom: 14px;
  }
}

/* ---------- compact：网格内卡片（封面 16/9、标题 17px） ---------- */
.article-card--compact {
  padding: 18px;

  .article-card__cover {
    margin-bottom: 12px;
  }

  .article-card__cover img {
    aspect-ratio: 16 / 9;
  }

  .article-card__title {
    font-size: 17px;
    line-height: 1.45;
  }

  .article-card__summary {
    font-size: 13.5px;
    margin-bottom: 12px;
  }

  .article-card__meta {
    font-size: 12px;
  }
}

/* ---------- featured：首页通栏特色卡（横向） ---------- */
.article-card--featured {
  padding: 24px 26px;

  .article-card__link {
    display: flex;
    align-items: stretch;
    gap: 24px;
  }

  .article-card__cover {
    flex: 0 0 45%;
    min-width: 0;
  }

  .article-card__cover img {
    aspect-ratio: 16 / 10;
    height: 100%;
  }

  .article-card__body {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .article-card__title {
    font-size: 26px;
    font-weight: 700;
    line-height: 1.3;
    letter-spacing: -0.02em;
    margin-bottom: 12px;
  }

  .article-card__summary {
    font-size: 14.5px;
    -webkit-line-clamp: 3;
    margin-bottom: 18px;
  }

  .article-card__meta {
    font-size: 13px;
  }

  /* 无封面时退化为「大标题 + 摘要」文字卡，不留空框 */
  &:not(:has(.article-card__cover)) .article-card__title {
    margin-bottom: 14px;
  }
}

@media (max-width: 900px) {
  .article-card--featured {
    padding: 20px;

    .article-card__link {
      flex-direction: column;
      gap: 16px;
    }

    .article-card__cover {
      flex: none;
    }

    .article-card__cover img {
      height: auto;
    }

    .article-card__title {
      font-size: 21px;
    }
  }
}
</style>
