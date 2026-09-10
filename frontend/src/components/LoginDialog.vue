<template>
  <el-dialog
    :model-value="dialogStore.visible"
    :title="mode === 'login' ? '登录博客账号' : '注册博客账号'"
    width="400px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @update:model-value="onVisibleChange"
  >
    <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="onSubmit">
      <el-form-item prop="username">
        <el-input v-model="form.username" placeholder="用户名" />
      </el-form-item>
      <el-form-item v-if="mode === 'register'" prop="email">
        <el-input v-model="form.email" placeholder="邮箱" />
      </el-form-item>
      <el-form-item v-if="mode === 'register'" prop="nickname">
        <el-input v-model="form.nickname" placeholder="昵称（可选）" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="密码" show-password />
      </el-form-item>
      <el-form-item v-if="mode === 'register'" prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          placeholder="确认密码"
          show-password
        />
      </el-form-item>
    </el-form>
    <div class="login-dialog__tip">
      <template v-if="mode === 'login'">
        还没有博客账号？
        <el-link type="primary" :underline="false" @click="switchMode('register')">
          立即注册
        </el-link>
      </template>
      <template v-else>
        已有博客账号？
        <el-link type="primary" :underline="false" @click="switchMode('login')">去登录</el-link>
      </template>
    </div>
    <template #footer>
      <el-button @click="dialogStore.cancel()">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onSubmit">
        {{ mode === 'login' ? '登录' : '注册' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useLoginDialogStore } from '@/stores/loginDialog'
import { useBlogUserStore } from '@/stores/blogUser'

const dialogStore = useLoginDialogStore()
const blogUserStore = useBlogUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const mode = ref<'login' | 'register'>('login')
const form = reactive({
  username: '',
  email: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

const rules = computed<FormRules>(() => ({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  email:
    mode.value === 'register'
      ? [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
        ]
      : [],
  confirmPassword:
    mode.value === 'register'
      ? [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          {
            validator: (_rule, value: string, callback: (err?: Error) => void) => {
              if (value !== form.password) callback(new Error('两次输入的密码不一致'))
              else callback()
            },
            trigger: 'blur'
          }
        ]
      : []
}))

function onVisibleChange(value: boolean) {
  // 只有关闭时才处理，避免与内部 success/cancel 重复
  if (!value) dialogStore.cancel()
}

function switchMode(next: 'login' | 'register') {
  mode.value = next
  formRef.value?.clearValidate()
}

function resetForm() {
  form.username = ''
  form.email = ''
  form.nickname = ''
  form.password = ''
  form.confirmPassword = ''
  formRef.value?.clearValidate()
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
    if (mode.value === 'register') {
      await blogUserStore.registerAction({
        username: form.username,
        email: form.email,
        password: form.password,
        nickname: form.nickname || undefined
      })
      // 注册成功后自动登录，避免用户再输一次
      await blogUserStore.loginAction({ username: form.username, password: form.password })
      await blogUserStore.fetchMe()
      ElMessage.success('注册成功，已登录博客账号')
    } else {
      await blogUserStore.loginAction({ username: form.username, password: form.password })
      await blogUserStore.fetchMe()
      ElMessage.success('登录成功')
    }
    resetForm()
    mode.value = 'login'
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
