<template>
  <div class="profile">
    <PageHeader title="个人设置" show-back />

    <el-card class="profile__section">
      <template #header>基本信息</template>
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

    <el-card class="profile__section">
      <template #header>头像</template>
      <div class="profile__avatar">
        <el-avatar :size="80" :src="avatarSrc || undefined">{{ avatarFallback }}</el-avatar>
        <el-upload
          :auto-upload="false"
          :show-file-list="false"
          accept="image/png,image/jpeg,image/webp"
          :on-change="onAvatarChange"
        >
          <el-button :loading="uploading">上传头像</el-button>
        </el-upload>
      </div>
    </el-card>

    <el-card class="profile__section">
      <template #header>修改密码</template>
      <el-form
        ref="pwdFormRef"
        :model="pwdForm"
        :rules="pwdRules"
        label-width="80px"
        style="max-width: 480px"
      >
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="pwdForm.confirmPassword" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="changing" @click="onChangePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { getMe } from '@/api/auth'
import { updateProfile, updatePassword, uploadAvatar } from '@/api/user'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const saving = ref(false)
const uploading = ref(false)
const changing = ref(false)
const avatarUrl = ref('')

const form = reactive({
  username: '',
  email: '',
  nickname: '',
  bio: ''
})

const pwdFormRef = ref<FormInstance>()
const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirmPassword: ''
})

const pwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度 6-128 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== pwdForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const avatarSrc = computed(() => avatarUrl.value || userStore.userInfo?.avatar || '')
const avatarFallback = computed(
  () => userStore.userInfo?.nickname?.slice(0, 1) || userStore.userInfo?.username?.slice(0, 1) || 'U'
)

async function load() {
  const user = await getMe()
  form.username = user.username
  form.email = user.email
  form.nickname = user.nickname
  form.bio = user.bio
  avatarUrl.value = user.avatar || ''
  userStore.setUser(user)
}

async function onSave() {
  saving.value = true
  try {
    const user = await updateProfile({
      nickname: form.nickname,
      bio: form.bio
    })
    userStore.setUser(user)
    ElMessage.success('保存成功')
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    saving.value = false
  }
}

async function onAvatarChange(uploadFile: { raw?: File }) {
  const file = uploadFile.raw
  if (!file) return
  uploading.value = true
  try {
    const res = await uploadAvatar(file)
    avatarUrl.value = res.url
    if (userStore.userInfo) {
      userStore.setUser({ ...userStore.userInfo, avatar: res.url })
    }
    ElMessage.success('头像已更新')
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    uploading.value = false
  }
}

async function onChangePassword() {
  if (!pwdFormRef.value) return
  try {
    await pwdFormRef.value.validate()
  } catch {
    return
  }
  changing.value = true
  try {
    await updatePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    ElMessage.success('密码修改成功，请重新登录')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirmPassword = ''
    userStore.logout()
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    changing.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.profile__section {
  margin-bottom: 16px;
}
.profile__avatar {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
