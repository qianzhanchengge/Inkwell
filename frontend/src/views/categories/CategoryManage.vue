<template>
  <div class="category-manage page-stack">
    <PageHeader title="分类管理" description="维护笔记与文章的所属分类" show-back />

    <el-card>
      <el-tabs v-model="type" @tab-change="load">
        <el-tab-pane label="笔记分类" :name="1" />
        <el-tab-pane label="文章分类" :name="2" />
      </el-tabs>

      <PageToolbar>
        <template #info>共 {{ categories.length }} 个分类</template>
        <el-button type="primary" @click="openCreate">
          <AppIcon name="plus" :size="15" />新增分类
        </el-button>
      </PageToolbar>

      <el-table :data="categories" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="sort_order" label="排序" width="100" align="right" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">
              <AppIcon name="edit" :size="14" />编辑
            </el-button>
            <el-button link type="danger" @click="onDelete(row.id)">
              <AppIcon name="trash" :size="14" />删除
            </el-button>
          </template>
        </el-table-column>

        <template #empty>
          <EmptyState description="还没有分类" hint="点击「新增分类」创建第一个" />
        </template>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingId != null ? '编辑分类' : '新增分类'"
      width="420px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="分类名称" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import PageToolbar from '@/components/PageToolbar.vue'
import EmptyState from '@/components/EmptyState.vue'
import AppIcon from '@/components/AppIcon.vue'
import { getCategoryList, createCategory, updateCategory, deleteCategory } from '@/api/category'
import type { Category } from '@/types/api'

const loading = ref(false)
const saving = ref(false)
const type = ref<1 | 2>(1)
const categories = ref<Category[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ name: '', sort_order: 0 })

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

function openCreate() {
  editingId.value = null
  form.name = ''
  form.sort_order = 0
  dialogVisible.value = true
}

function openEdit(row: Category) {
  editingId.value = row.id
  form.name = row.name
  form.sort_order = row.sort_order ?? 0
  dialogVisible.value = true
}

async function onSubmit() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  saving.value = true
  try {
    if (editingId.value != null) {
      await updateCategory(editingId.value, { name: form.name.trim(), sort_order: form.sort_order })
    } else {
      await createCategory({ name: form.name.trim(), type: type.value, sort_order: form.sort_order })
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    saving.value = false
  }
}

async function onDelete(id: number) {
  await deleteCategory(id)
  ElMessage.success('删除成功')
  load()
}

onMounted(load)
</script>
