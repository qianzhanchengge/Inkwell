<template>
  <div class="page-header">
    <h2 class="page-header__title">{{ title }}</h2>
    <div v-if="$slots.extra" class="page-header__extra">
      <slot name="extra" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<style scoped lang="scss">
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-header__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}
</style>
