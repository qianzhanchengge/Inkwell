<template>
  <div class="empty-state">
    <p class="empty-state__text">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ description?: string }>(), {
  description: '暂无数据'
})
</script>

<style scoped lang="scss">
.empty-state {
  padding: 48px 0;
  text-align: center;
  color: #909399;
}
.empty-state__text {
  margin: 0;
}
</style>
