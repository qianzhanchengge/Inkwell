<template>
  <div class="page-header">
    <div class="page-header__left">
      <button v-if="showBack" type="button" class="page-header__back" @click="goBack">
        <AppIcon name="chevron-left" :size="16" />
        <span>返回</span>
      </button>

      <div class="page-header__heading">
        <h2 class="page-header__title">{{ title }}</h2>
        <p v-if="description || $slots.description" class="page-header__desc">
          <slot name="description">{{ description }}</slot>
        </p>
      </div>
    </div>

    <div v-if="$slots.extra" class="page-header__extra">
      <slot name="extra" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'

const props = withDefaults(
  defineProps<{
    title: string
    /** 是否显示返回按钮（详情/编辑/管理类子页面建议开启） */
    showBack?: boolean
    /** 无站内历史时的兜底返回路径 */
    backTo?: string
    /** 标题下方的说明文字（也可用 #description 插槽） */
    description?: string
  }>(),
  { showBack: false, backTo: '/dashboard', description: '' }
)

const router = useRouter()

function goBack() {
  // 有站内历史时返回上一页，否则（如深链接直达）跳转兜底页面
  const state = (router.options.history as unknown as { state?: { back?: unknown } }).state
  if (window.history.length > 1 && state && state.back) {
    router.back()
  } else {
    router.push(props.backTo)
  }
}
</script>

<style scoped lang="scss">
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.page-header__left {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.page-header__back {
  appearance: none;
  border: 0;
  background: transparent;
  margin-top: 1px;
  padding: 3px 8px 3px 4px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font: inherit;
  font-size: 14px;
  color: var(--blog-accent);
  cursor: pointer;
  border-radius: var(--blog-radius-sm);
  transition: background-color 0.2s, color 0.2s, transform 0.15s;

  &:hover {
    background-color: var(--blog-accent-soft);
  }

  &:active {
    transform: translateY(1px);
  }
}

.page-header__heading {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-header__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--blog-ink);
}

.page-header__desc {
  margin: 0;
  font-size: 13px;
  color: var(--blog-ink-mute);
}

.page-header__extra {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
