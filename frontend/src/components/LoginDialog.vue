<template>
  <el-dialog
    :model-value="dialogStore.visible"
    title="登录"
    width="360px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @update:model-value="onVisibleChange"
  >
    <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="onSubmit">
      <el-form-item prop="username">
        <el-input v-model="form.username" placeholder="用户名" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="密码" show-password />
      </el-form-item>
    </el-form>
    <div class="login-dialog__tip">
      还没有账号？<router-link to="/register" @click="dialogStore.cancel()">去注册</router-link>
    </div>
    <template #footer>
      <el-button @click="dialogStore.cancel()">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onSubmit">登录</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useLoginDialogStore } from '@/stores/loginDialog'
import { useUserStore } from '@/stores/user'

const dialogStore = useLoginDialogStore()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

function onVisibleChange(value: boolean) {
  // 只有关闭时才处理，避免与内部 success/cancel 重复
  if (!value) dialogStore.cancel()
}

async function onSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    await userStore.loginAction({ username: form.username, password: form.password })
    await userStore.fetchMe()
    form.password = ''
    ElMessage.success('登录成功')
    dialogStore.success()
  } catch {
    // 错误提示已由 axios 拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-dialog__tip {
  font-size: 13px;
  color: #909399;
  margin-top: -8px;
}
</style>
