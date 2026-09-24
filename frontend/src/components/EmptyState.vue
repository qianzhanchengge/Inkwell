<template>
  <div class="empty-state">
    <span class="empty-state__icon">
      <AppIcon name="inbox" :size="22" />
    </span>
    <p class="empty-state__text">{{ description }}</p>
    <p v-if="hint" class="empty-state__hint">{{ hint }}</p>
    <div v-if="$slots.default" class="empty-state__action">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import AppIcon from '@/components/AppIcon.vue'

withDefaults(
  defineProps<{
    description?: string
    hint?: string
  }>(),
  { description: '暂无数据', hint: '' }
)
</script>

<style scoped lang="scss">
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 48px 16px;
  text-align: center;
}

.empty-state__icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--blog-accent-soft);
  color: var(--blog-accent);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state__text {
  margin: 0;
  font-size: 14px;
  color: var(--blog-ink-soft);
}

.empty-state__hint {
  margin: 0;
  font-size: 13px;
  color: var(--blog-ink-mute);
}

.empty-state__action {
  margin-top: 4px;
}
</style>
