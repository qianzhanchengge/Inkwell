<template>
  <div class="category-manage">
    <PageHeader title="分类管理" />

    <el-card>
      <el-tabs v-model="type" @tab-change="load">
        <el-tab-pane label="笔记分类" :name="1" />
        <el-tab-pane label="文章分类" :name="2" />
      </el-tabs>

      <div class="category-manage__toolbar">
        <el-input v-model="name" placeholder="新分类名称" style="width: 240px" />
        <el-button type="primary" @click="onCreate">新增分类</el-button>
      </div>

      <el-table :data="categories" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="sort_order" label="排序" width="100" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="danger" @click="onDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { getCategoryList, createCategory, deleteCategory } from '@/api/category'
import type { Category } from '@/types/api'

const loading = ref(false)
const type = ref<1 | 2>(1)
const name = ref('')
const categories = ref<Category[]>([])

async function load() {
  loading.value = true
  try {
    categories.value = await getCategoryList(type.value)
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

async function onCreate() {
  if (!name.value.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  await createCategory({ name: name.value.trim(), type: type.value })
  ElMessage.success('创建成功')
  name.value = ''
  load()
}

async function onDelete(id: number) {
  await deleteCategory(id)
  ElMessage.success('删除成功')
  load()
}

onMounted(load)
</script>

<style scoped lang="scss">
.category-manage__toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
</style>
