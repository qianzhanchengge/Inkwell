<template>
  <div class="profile">
    <PageHeader title="个人设置" />

    <el-card>
      <el-form :model="form" label-width="80px" style="max-width: 480px">
        <el-form-item label="用户名">
          <el-input :model-value="form.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input :model-value="form.email" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="昵称" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.bio" type="textarea" :rows="3" placeholder="个人简介" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { getMe } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const saving = ref(false)
const form = reactive({
  username: '',
  email: '',
  nickname: '',
  bio: ''
})

async function load() {
  const user = await getMe()
  form.username = user.username
  form.email = user.email
  form.nickname = user.nickname
  form.bio = user.bio
  userStore.setUser(user)
}

async function onSave() {
  saving.value = true
  try {
    ElMessage.success('保存成功（待接入更新接口）')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
