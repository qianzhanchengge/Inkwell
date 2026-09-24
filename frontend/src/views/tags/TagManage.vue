<template>
  <div class="tag-manage page-stack">
    <PageHeader title="标签管理" description="维护笔记与文章共用的标签" show-back />

    <el-card>
      <PageToolbar>
        <template #info>共 {{ tags.length }} 个标签</template>
        <el-input
          v-model="name"
          placeholder="新标签名称"
          style="width: 220px"
          @keyup.enter="onCreate"
        />
        <el-button type="primary" :loading="creating" @click="onCreate">
          <AppIcon name="plus" :size="15" />新增标签
        </el-button>
      </PageToolbar>

      <el-table :data="tags" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" @click="onDelete(row.id)">
              <AppIcon name="trash" :size="14" />删除
            </el-button>
          </template>
        </el-table-column>

        <template #empty>
          <EmptyState description="还没有标签" hint="输入名称后点击「新增标签」" />
        </template>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import PageToolbar from '@/components/PageToolbar.vue'
import EmptyState from '@/components/EmptyState.vue'
import AppIcon from '@/components/AppIcon.vue'
import { getTagList, createTag, deleteTag } from '@/api/tag'
import type { Tag } from '@/types/api'

const loading = ref(false)
const creating = ref(false)
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
  creating.value = true
  try {
    await createTag({ name: name.value.trim() })
    ElMessage.success('创建成功')
    name.value = ''
    load()
  } catch (e) {
    // 错误提示已统一处理
  } finally {
    creating.value = false
  }
}

async function onDelete(id: number) {
  await deleteTag(id)
  ElMessage.success('删除成功')
  load()
}

onMounted(load)
</script>
