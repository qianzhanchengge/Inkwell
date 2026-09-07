<template>
  <div class="note-list">
    <PageHeader title="笔记管理">
      <template #extra>
        <el-button type="primary" @click="goCreate">新建笔记</el-button>
      </template>
    </PageHeader>

    <el-card>
      <div class="note-list__filters">
        <el-input v-model="keyword" placeholder="关键词搜索" clearable class="note-list__search" />
        <el-button type="primary" @click="load">查询</el-button>
      </div>

      <el-table :data="notes" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="置顶" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_pinned" type="warning" size="small">置顶</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row.id)">查看</el-button>
            <el-button link type="primary" @click="goEdit(row.id)">编辑</el-button>
            <el-button link type="danger" @click="onDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <Pagination
        :page="page"
        :page-size="pageSize"
        :total="total"
        @update:page="onPageChange"
        @update:page-size="onSizeChange"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import Pagination from '@/components/Pagination.vue'
import { getNoteList, deleteNote } from '@/api/note'
import type { Note } from '@/types/note'
import { formatDateTime } from '@/utils/format'

const router = useRouter()
const loading = ref(false)
const notes = ref<Note[]>([])
const keyword = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function load() {
  loading.value = true
  try {
    const data = await getNoteList({ page: page.value, page_size: pageSize.value, keyword: keyword.value || undefined })
    notes.value = data.items
    total.value = data.total
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

function goCreate() {
  router.push('/notes/new')
}
function goDetail(id: number) {
  router.push(`/notes/${id}`)
}
function goEdit(id: number) {
  router.push(`/notes/${id}/edit`)
}
async function onDelete(id: number) {
  await deleteNote(id)
  ElMessage.success('删除成功')
  load()
}
function onPageChange(value: number) {
  page.value = value
  load()
}
function onSizeChange(value: number) {
  pageSize.value = value
  load()
}

onMounted(load)
</script>

<style scoped lang="scss">
.note-list__filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.note-list__search {
  width: 280px;
}
</style>
