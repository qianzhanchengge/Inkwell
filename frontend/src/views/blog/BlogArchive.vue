<template>
  <div class="blog-archive">
    <header class="blog-archive__head">
      <h2 class="blog-archive__title">归档</h2>
      <span class="blog-archive__stat">共 {{ archive.length }} 个月份</span>
    </header>

    <div v-if="loading" class="blog-archive__skeleton">
      <div v-for="i in 4" :key="i" class="blog-archive__skeleton-row"></div>
    </div>

    <div v-else-if="grouped.length" class="blog-archive__timeline">
      <section v-for="group in grouped" :key="group.year" class="blog-archive__year">
        <span class="blog-archive__year-label">{{ group.year }}</span>
        <div class="blog-archive__months">
          <div v-for="m in group.months" :key="m.month" class="blog-archive__month">
            <span class="blog-archive__month-name">{{ m.month }} 月</span>
            <span class="blog-archive__count">{{ m.count }} 篇</span>
          </div>
        </div>
      </section>
    </div>

    <el-empty v-else description="暂无归档" />
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
  max-width: var(--blog-reading);
  margin: 0 auto;
  padding: 40px 20px 56px;
}

.blog-archive__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--blog-line);
}

.blog-archive__title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--blog-ink);
  text-wrap: balance;
}

.blog-archive__title::before {
  content: '';
  width: 3px;
  height: 20px;
  border-radius: 2px;
  background: var(--blog-accent);
  flex: none;
}

.blog-archive__stat {
  font-size: 13px;
  color: var(--blog-ink-mute);
  font-variant-numeric: tabular-nums;
}

/* 时间轴：左侧 1px 竖轴 */
.blog-archive__timeline {
  position: relative;
  padding-left: 20px;
  border-left: 1px solid var(--blog-line);
}

.blog-archive__year {
  position: relative;
  padding-bottom: 26px;

  &:last-child {
    padding-bottom: 0;
  }
}

/* 年份：accent 小标签，压在竖轴上 */
.blog-archive__year-label {
  display: inline-flex;
  align-items: center;
  position: relative;
  left: -20px;
  margin-bottom: 10px;
  padding: 3px 10px;
  border-radius: var(--blog-radius-sm);
  background: var(--blog-accent-soft);
  color: var(--blog-accent);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
  font-variant-numeric: tabular-nums;
}

.blog-archive__months {
  display: flex;
  flex-direction: column;
}

.blog-archive__month {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 9px 10px;
  margin-left: -10px;
  border-radius: var(--blog-radius-sm);
  color: var(--blog-ink-soft);
  font-size: 14px;
  font-variant-numeric: tabular-nums;
  transition: color 0.2s, background-color 0.2s, transform 0.2s;

  &:hover {
    color: var(--blog-accent);
    background: var(--blog-accent-soft);
    transform: translateX(2px);
  }

  &:active {
    transform: translateX(2px) translateY(1px);
  }
}

.blog-archive__count {
  color: var(--blog-ink-mute);
  font-size: 12px;
  flex-shrink: 0;
}

/* 加载态：与时间轴形状接近的占位条 */
.blog-archive__skeleton {
  padding-left: 20px;
  border-left: 1px solid var(--blog-line);
}

.blog-archive__skeleton-row {
  height: 34px;
  margin-bottom: 12px;
  border-radius: var(--blog-radius-sm);
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
  .blog-archive__skeleton-row {
    animation: none;
  }
}

@media (max-width: 900px) {
  .blog-archive {
    padding: 28px 16px 48px;
  }

  .blog-archive__title {
    font-size: 21px;
  }
}
</style>
