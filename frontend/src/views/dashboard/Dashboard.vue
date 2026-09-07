<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col v-for="card in cards" :key="card.label" :span="6">
        <el-card class="dashboard__card">
          <div class="dashboard__card-label">{{ card.label }}</div>
          <div class="dashboard__card-value">{{ card.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="dashboard__trend">
      <template #header>
        <span>创作趋势</span>
      </template>
      <div class="dashboard__trend-placeholder">
        数据看板（ECharts 图表待接入后端统计接口后展示）
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const cards = ref([
  { label: '笔记数', value: '--' },
  { label: '文章数', value: '--' },
  { label: '总字数', value: '--' },
  { label: '总阅读量', value: '--' }
])
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
.dashboard__trend {
  margin-top: 16px;
}
.dashboard__trend-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}
</style>
