<template>
  <div class="page-header">
    <div class="page-header__left">
      <el-button v-if="showBack" class="page-header__back" text @click="goBack">
        ← 返回
      </el-button>
      <h2 class="page-header__title">{{ title }}</h2>
    </div>
    <div v-if="$slots.extra" class="page-header__extra">
      <slot name="extra" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const props = withDefaults(
  defineProps<{
    title: string
    /** 是否显示返回按钮（详情/编辑/管理类子页面建议开启） */
    showBack?: boolean
    /** 无站内历史时的兜底返回路径 */
    backTo?: string
  }>(),
  { showBack: false, backTo: '/dashboard' }
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
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-header__left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.page-header__back {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
.page-header__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}
</style>
