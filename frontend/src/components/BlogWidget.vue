<template>
  <section class="blog-widget">
    <h2 v-if="title" class="blog-widget__title">{{ title }}</h2>
    <slot />
  </section>
</template>

<script setup lang="ts">
defineProps<{ title?: string }>()
</script>

<style scoped lang="scss">
.blog-widget {
  background: var(--blog-surface, #fff);
  border-radius: var(--blog-radius, 10px);
  box-shadow: var(--blog-shadow-sm, 0 1px 2px rgba(28, 22, 18, 0.05));
  padding: 18px 20px 20px;
  margin-bottom: 18px;
}

/* 小标题 + 强调色竖条 */
.blog-widget__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 14px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--blog-ink-mute, #8b9099);
}

.blog-widget__title::before {
  content: '';
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: var(--blog-accent, #b4443a);
  flex-shrink: 0;
}
</style>
