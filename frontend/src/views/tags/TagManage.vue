<template>
  <div class="tag-manage">
    <PageHeader title="标签管理" show-back />

    <el-card>
      <div class="tag-manage__toolbar">
        <el-input v-model="name" placeholder="新标签名称" style="width: 240px" />
        <el-button type="primary" @click="onCreate">新增标签</el-button>
      </div>

      <el-table :data="tags" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="200" />
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
import { getTagList, createTag, deleteTag } from '@/api/tag'
import type { Tag } from '@/types/api'

const loading = ref(false)
const name = ref('')
const tags = ref<Tag[]>([])

async function load() {
  loading.value = true
  try {
    tags.value = await getTagList()
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

async function onCreate() {
  if (!name.value.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }
  await createTag({ name: name.value.trim() })
  ElMessage.success('创建成功')
  name.value = ''
  load()
}

async function onDelete(id: number) {
  await deleteTag(id)
  ElMessage.success('删除成功')
  load()
}

onMounted(load)
</script>

<style scoped lang="scss">
.tag-manage__toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
</style>
