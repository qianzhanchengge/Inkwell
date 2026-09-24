<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <div class="auth-card__brand">
        <span class="auth-card__mark">工</span>
      </div>
      <h2 class="auth-card__title">注册</h2>
      <p class="auth-card__subtitle">创建工作台账号</p>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        @validate="onValidate"
        @submit.prevent="onSubmit"
      >
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名（3-50 位）" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-form-item>
        <el-form-item prop="nickname">
          <el-input v-model="form.nickname" placeholder="昵称（可选）" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码（至少 6 位）"
            show-password
          />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            class="auth-card__submit"
            size="large"
            :loading="loading"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-card__footer">
        <router-link to="/login">已有账号？去登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuth } from '@/composables/useAuth'
import { useAutoClearValidate } from '@/composables/useAutoClearValidate'

const router = useRouter()
const { register } = useAuth()

const formRef = ref<FormInstance>()
/** 校验未通过时，提示信息 5 秒后自动消失 */
const onValidate = useAutoClearValidate(formRef)
const loading = ref(false)
const form = reactive({
  username: '',
  email: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度 3-50 位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度 6-128 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
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
    await register({
      username: form.username,
      email: form.email,
      password: form.password,
      nickname: form.nickname || undefined
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
    // 错误提示已由 axios 拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background:
    radial-gradient(1000px 520px at 50% -12%, rgba(180, 68, 58, 0.07), transparent 62%),
    var(--blog-paper);
}

.auth-card {
  width: 400px;
  box-shadow: var(--blog-shadow-md);
}

.auth-card :deep(.el-card__body) {
  padding: 28px 26px 24px;
}

.auth-card__brand {
  display: flex;
  justify-content: center;
  margin-bottom: 14px;
}

.auth-card__mark {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--blog-accent);
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-card__title {
  margin: 0 0 6px;
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--blog-ink);
}

.auth-card__subtitle {
  margin: 0 0 22px;
  text-align: center;
  font-size: 13px;
  color: var(--blog-ink-mute);
}

.auth-card__submit {
  width: 100%;
}

.auth-card__footer {
  text-align: center;
  font-size: 13px;
  color: var(--blog-ink-mute);
}
</style>
