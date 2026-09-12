<template>
  <div class="blog-notfound">
    <p class="blog-notfound__code">404</p>
    <h1 class="blog-notfound__title">页面不存在</h1>
    <p class="blog-notfound__desc">链接可能已失效、被移动，或者地址输入有误。</p>
    <div class="blog-notfound__actions">
      <router-link to="/blog" class="blog-notfound__btn blog-notfound__btn--primary">
        返回博客首页
      </router-link>
      <router-link to="/dashboard" class="blog-notfound__btn">去工作台</router-link>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped lang="scss">
/* 自包含样式：本页可能渲染在博客布局内，也可能作为全局兜底路由单独渲染 */
.blog-notfound {
  max-width: var(--blog-reading, 720px);
  margin: 0 auto;
  padding: 80px 20px;
  text-align: center;
}

.blog-notfound__code {
  margin: 0 0 8px;
  font-size: 64px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.03em;
  color: var(--blog-line, #e9e6e1);
}

.blog-notfound__title {
  margin: 0 0 10px;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--blog-ink, #14161a);
}

.blog-notfound__desc {
  margin: 0 0 24px;
  font-size: 14px;
  color: var(--blog-ink-soft, #4a4f57);
}

.blog-notfound__actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.blog-notfound__btn {
  display: inline-flex;
  align-items: center;
  padding: 9px 18px;
  font-size: 14px;
  border-radius: var(--blog-radius-sm, 6px);
  border: 1px solid var(--blog-line, #e9e6e1);
  background: var(--blog-surface, #fff);
  color: var(--blog-ink-soft, #4a4f57);
  transition: background 0.2s, border-color 0.2s, color 0.2s, transform 0.15s;

  &:hover {
    border-color: var(--blog-accent, #b4443a);
    color: var(--blog-accent, #b4443a);
  }

  &:active {
    transform: translateY(1px);
  }
}

.blog-notfound__btn--primary {
  background: var(--blog-accent, #b4443a);
  border-color: var(--blog-accent, #b4443a);
  color: #fff;

  &:hover {
    background: var(--blog-accent-dark, #90362e);
    border-color: var(--blog-accent-dark, #90362e);
    color: #fff;
  }
}
</style>
