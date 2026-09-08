<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col v-for="card in cards" :key="card.label" :span="6">
        <el-card class="dashboard__card" shadow="hover">
          <div class="dashboard__card-label">{{ card.label }}</div>
          <div class="dashboard__card-value">{{ card.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="dashboard__quick" shadow="never">
      <template #header><span>快捷入口</span></template>
      <el-space wrap>
        <el-button type="primary" @click="$router.push('/notes/new')">新建笔记</el-button>
        <el-button type="success" @click="$router.push('/articles/new')">写文章</el-button>
      </el-space>
    </el-card>

    <el-card class="dashboard__trend" shadow="never">
      <template #header><span>创作趋势（近 30 天）</span></template>
      <div ref="chartRef" class="dashboard__chart" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
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
    tooltip: { trigger: 'axis' },
    legend: { data: ['笔记', '文章'] },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', boundaryGap: false, data: data.map((d) => d.date.slice(5)) },
    yAxis: { type: 'value', minInterval: 1 },
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
.dashboard__card {
  text-align: center;
}
.dashboard__card-label {
  color: #909399;
  font-size: 14px;
}
.dashboard__card-value {
  margin-top: 8px;
  font-size: 28px;
  font-weight: 600;
}
.dashboard__quick {
  margin-top: 16px;
}
.dashboard__trend {
  margin-top: 16px;
}
.dashboard__chart {
  height: 300px;
}
</style>
