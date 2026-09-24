<template>
  <div v-if="total > 0" class="pagination-wrap">
    <el-pagination
      :current-page="page"
      :page-size="pageSize"
      :total="total"
      :page-sizes="pageSizes"
      layout="total, sizes, prev, pager, next, jumper"
      @current-change="onPageChange"
      @size-change="onSizeChange"
    />
  </div>
</template>

<script setup lang="ts">
import { PAGE_SIZES } from '@/utils/constants'

withDefaults(
  defineProps<{
    page: number
    pageSize: number
    total: number
  }>(),
  {
    page: 1,
    pageSize: 10,
    total: 0
  }
)

const emit = defineEmits<{
  (e: 'update:page', value: number): void
  (e: 'update:pageSize', value: number): void
}>()

const pageSizes = PAGE_SIZES

function onPageChange(value: number) {
  emit('update:page', value)
}

function onSizeChange(value: number) {
  emit('update:pageSize', value)
}
</script>

<style scoped lang="scss">
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--blog-line);
}
</style>
