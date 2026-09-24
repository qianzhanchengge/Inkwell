<template>
  <div class="dashboard page-stack">
    <div class="dashboard__stats">
      <div v-for="card in cards" :key="card.label" class="dashboard__stat">
        <span class="dashboard__stat-label">{{ card.label }}</span>
        <span class="dashboard__stat-value">{{ card.value }}</span>
      </div>
    </div>

    <el-card>
      <template #header><span>快捷入口</span></template>
      <div class="dashboard__actions">
        <el-button type="primary" @click="$router.push('/notes/new')">
          <AppIcon name="plus" :size="15" />新建笔记
        </el-button>
        <el-button @click="$router.push('/articles/new')">
          <AppIcon name="edit" :size="15" />写文章
        </el-button>
      </div>
    </el-card>

    <el-card>
      <template #header><span>创作趋势（近 30 天）</span></template>
      <div ref="chartRef" class="dashboard__chart" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import AppIcon from '@/components/AppIcon.vue'
import { getStatsOverview, getStatsTrend, type TrendItem } from '@/api/stats'

interface Card {
  label: string
  value: string | number
}

const cards = ref<Card[]>([
  { label: '笔记数', value: '--' },
  { label: '文章数', value: '--' },
  { label: '总字数', value: '--' },
  { label: '总阅读量', value: '--' }
])

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

function renderChart(data: TrendItem[]) {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  chart.setOption({
    // 与全局设计 token 保持一致（印章红 + 中性灰）
    color: ['#b4443a', '#8b9099'],
    tooltip: { trigger: 'axis' },
    legend: { data: ['笔记', '文章'], textStyle: { color: '#4a4f57' } },
    grid: { left: 44, right: 24, top: 44, bottom: 32 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.map((d) => d.date.slice(5)),
      axisLine: { lineStyle: { color: '#e9e6e1' } },
      axisLabel: { color: '#8b9099' }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#f2f0ec' } },
      axisLabel: { color: '#8b9099' }
    },
    series: [
      { name: '笔记', type: 'line', smooth: true, data: data.map((d) => d.note_count) },
      { name: '文章', type: 'line', smooth: true, data: data.map((d) => d.article_count) }
    ]
  })
}

async function load() {
  try {
    const [overview, trend] = await Promise.all([getStatsOverview(), getStatsTrend(30)])
    cards.value = [
      { label: '笔记数', value: overview.note_count },
      { label: '文章数', value: overview.article_count },
      { label: '总字数', value: overview.total_words },
      { label: '总阅读量', value: overview.total_views }
    ]
    renderChart(trend)
  } catch (e) {
    // 错误已由 request 拦截器统一提示
  }
}

function handleResize() {
  chart?.resize()
}

onMounted(() => {
  load()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped lang="scss">
.dashboard__stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

@media (max-width: 900px) {
  .dashboard__stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.dashboard__stat {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 20px;
  background: var(--blog-surface);
  border-radius: var(--blog-radius);
  box-shadow: var(--blog-shadow-sm);
  transition: box-shadow 0.25s, transform 0.25s;
}

.dashboard__stat:hover {
  box-shadow: var(--blog-shadow-md);
  transform: translateY(-2px);
}

.dashboard__stat-label {
  font-size: 13px;
  color: var(--blog-ink-mute);
}

.dashboard__stat-value {
  font-size: 30px;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
  color: var(--blog-ink);
}

.dashboard__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.dashboard__chart {
  height: 300px;
}
</style>
