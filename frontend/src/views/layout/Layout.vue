<template>
  <el-container class="layout">
    <el-aside :width="isCollapsed ? '64px' : '200px'" class="layout__aside">
      <div class="layout__logo">{{ isCollapsed ? '工' : '工作台' }}</div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :collapse-transition="false"
        router
        class="layout__menu"
      >
        <el-menu-item index="/dashboard"><span>工作台</span></el-menu-item>
        <el-menu-item index="/notes"><span>笔记管理</span></el-menu-item>
        <el-menu-item index="/articles"><span>文章管理</span></el-menu-item>
        <el-menu-item index="/categories"><span>分类管理</span></el-menu-item>
        <el-menu-item index="/tags"><span>标签管理</span></el-menu-item>
        <el-menu-item index="/profile"><span>个人设置</span></el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="layout__body">
      <el-header class="layout__header">
        <span class="layout__collapse-btn" @click="toggleSidebar">
          {{ isCollapsed ? '展开' : '收起' }}
        </span>
        <span class="layout__title">{{ pageTitle }}</span>
        <el-dropdown @command="onCommand">
          <span class="layout__user">{{ userName || '未登录' }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人设置</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="layout__main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const isCollapsed = computed(() => appStore.sidebarCollapsed)
const activeMenu = computed(() => route.path)
const pageTitle = computed(() => (route.meta.title as string) || '工作台')
const userName = computed(() => userStore.userInfo?.nickname || userStore.userInfo?.username || '')

function toggleSidebar() {
  appStore.toggleSidebar()
}

function onCommand(command: string) {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped lang="scss">
.layout {
  height: 100vh;
}
.layout__aside {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  transition: width 0.2s;
  overflow: hidden;
}
.layout__logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  border-bottom: 1px solid #e4e7ed;
}
.layout__menu {
  border-right: none;
}
.layout__body {
  display: flex;
  flex-direction: column;
}
.layout__header {
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}
.layout__collapse-btn {
  cursor: pointer;
  color: #909399;
  user-select: none;
}
.layout__title {
  font-size: 16px;
  font-weight: 500;
  flex: 1;
}
.layout__user {
  cursor: pointer;
  color: #303133;
}
.layout__main {
  background: #f5f7fa;
}
</style>
