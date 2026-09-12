<template>
  <div class="article-card-skeleton" aria-hidden="true">
    <div class="article-card-skeleton__cover"></div>
    <div class="article-card-skeleton__line article-card-skeleton__line--title"></div>
    <div class="article-card-skeleton__line"></div>
    <div class="article-card-skeleton__line article-card-skeleton__line--short"></div>
    <div class="article-card-skeleton__meta">
      <span class="article-card-skeleton__dot"></span>
      <span class="article-card-skeleton__dot"></span>
      <span class="article-card-skeleton__dot"></span>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped lang="scss">
/* 形状与 ArticleCard 对齐，避免加载完成时布局跳动 */
.article-card-skeleton {
  background: var(--blog-surface, #fff);
  border-radius: var(--blog-radius, 10px);
  box-shadow: var(--blog-shadow-sm, 0 1px 2px rgba(28, 22, 18, 0.05));
  padding: 20px 22px;
  margin-bottom: 18px;
}

.article-card-skeleton__cover {
  width: 100%;
  aspect-ratio: 16 / 10;
  border-radius: var(--blog-radius-sm, 6px);
  margin-bottom: 14px;
}

.article-card-skeleton__line {
  height: 12px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.article-card-skeleton__line--title {
  height: 20px;
  width: 62%;
  margin-bottom: 14px;
}

.article-card-skeleton__line--short {
  width: 44%;
}

.article-card-skeleton__meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
}

.article-card-skeleton__dot {
  height: 10px;
  width: 46px;
  border-radius: 4px;
}

/* 统一脉冲动画 */
.article-card-skeleton__cover,
.article-card-skeleton__line,
.article-card-skeleton__dot {
  background: linear-gradient(90deg, #f2f0ec 0%, #e9e6e1 50%, #f2f0ec 100%);
  background-size: 200% 100%;
  animation: blog-skeleton-pulse 1.4s ease-in-out infinite;
}

@keyframes blog-skeleton-pulse {
  0% {
    background-position: 100% 50%;
  }
  100% {
    background-position: -100% 50%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .article-card-skeleton__cover,
  .article-card-skeleton__line,
  .article-card-skeleton__dot {
    animation: none;
  }
}
</style>
