<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <h2 class="auth-card__title">登录</h2>
      <el-form ref="formRef" :model="form" :rules="rules" @validate="onValidate" @submit.prevent="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" class="auth-card__submit" :loading="loading">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="auth-card__footer">
        <router-link to="/register">还没有账号？去注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuth } from '@/composables/useAuth'
import { useAutoClearValidate } from '@/composables/useAutoClearValidate'

const route = useRoute()
const router = useRouter()
const { login } = useAuth()

const formRef = ref<FormInstance>()
/** 校验未通过时，提示信息 5 秒后自动消失 */
const onValidate = useAutoClearValidate(formRef)
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
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
    await login({ username: form.username, password: form.password })
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  } catch {
    // 错误提示已由 axios 拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.auth-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.auth-card {
  width: 380px;
}
.auth-card__title {
  margin: 0 0 20px;
  text-align: center;
}
.auth-card__submit {
  width: 100%;
}
.auth-card__footer {
  text-align: center;
  font-size: 14px;
}
</style>
