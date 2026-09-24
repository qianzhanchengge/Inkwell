<template>
  <div class="note-list page-stack">
    <PageHeader title="笔记管理" description="集中管理你的全部笔记" />

    <el-card>
      <PageToolbar>
        <template #info>共 {{ total }} 篇笔记</template>
        <SearchInput
          v-model="keyword"
          placeholder="搜索标题关键词"
          show-button
          :loading="loading"
          @search="onSearch"
        />
        <el-button type="primary" @click="goCreate">
          <AppIcon name="plus" :size="15" />新建笔记
        </el-button>
      </PageToolbar>

      <el-table :data="notes" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="置顶" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.is_pinned" type="warning" size="small">置顶</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row.id)">
              <AppIcon name="eye" :size="14" />查看
            </el-button>
            <el-button link type="primary" @click="goEdit(row.id)">
              <AppIcon name="edit" :size="14" />编辑
            </el-button>
            <el-button link type="danger" @click="onDelete(row.id)">
              <AppIcon name="trash" :size="14" />删除
            </el-button>
          </template>
        </el-table-column>

        <template #empty>
          <EmptyState description="还没有笔记" hint="点击「新建笔记」开始记录" />
        </template>
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
import PageToolbar from '@/components/PageToolbar.vue'
import SearchInput from '@/components/SearchInput.vue'
import Pagination from '@/components/Pagination.vue'
import EmptyState from '@/components/EmptyState.vue'
import AppIcon from '@/components/AppIcon.vue'
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
    const data = await getNoteList({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined
    })
    notes.value = data.items
    total.value = data.total
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  load()
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
