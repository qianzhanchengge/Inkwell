<template>
  <div class="blog-archive">
    <h2 class="blog-archive__title">归档</h2>
    <el-card v-loading="loading" shadow="never">
      <div v-if="grouped.length" class="blog-archive__list">
        <div v-for="group in grouped" :key="group.year" class="blog-archive__year">
          <h3 class="blog-archive__year-title">{{ group.year }} 年</h3>
          <div class="blog-archive__months">
            <div v-for="m in group.months" :key="m.month" class="blog-archive__month">
              {{ group.year }} 年 {{ m.month }} 月
              <span class="blog-archive__count">{{ m.count }} 篇</span>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else-if="!loading" description="暂无归档" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getBlogArchive } from '@/api/blog'
import type { ArchiveItem } from '@/types/blog'

const loading = ref(false)
const archive = ref<ArchiveItem[]>([])

interface YearGroup {
  year: number
  months: { month: number; count: number }[]
}

const grouped = computed<YearGroup[]>(() => {
  const map: Record<number, { month: number; count: number }[]> = {}
  for (const item of archive.value) {
    ;(map[item.year] ||= []).push({ month: item.month, count: item.count })
  }
  return Object.entries(map)
    .map(([year, months]) => ({
      year: Number(year),
      months: months.sort((a, b) => b.month - a.month)
    }))
    .sort((a, b) => b.year - a.year)
})

async function load() {
  loading.value = true
  try {
    archive.value = await getBlogArchive()
  } catch {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.blog-archive {
  max-width: 820px;
  margin: 0 auto;
  padding: 24px 16px;
}
.blog-archive__title {
  margin: 0 0 16px;
  font-size: 22px;
}
.blog-archive__year-title {
  margin: 12px 0;
  color: #303133;
}
.blog-archive__month {
  padding: 8px 0;
  border-bottom: 1px dashed #ebeef5;
  color: #606266;
}
.blog-archive__count {
  color: #c0c4cc;
  font-size: 12px;
  margin-left: 8px;
}
</style>
