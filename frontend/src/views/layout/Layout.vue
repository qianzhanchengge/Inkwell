<template>
  <el-container class="layout">
    <el-aside :width="isCollapsed ? '64px' : '208px'" class="layout__aside">
      <div class="layout__logo">
        <span class="layout__logo-mark">工</span>
        <span v-show="!isCollapsed" class="layout__logo-text">工作台</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :collapse-transition="false"
        router
        class="layout__menu"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <AppIcon :name="item.icon" :size="17" class="layout__menu-icon" />
          <template #title>
            <span class="layout__menu-text">{{ item.label }}</span>
          </template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="layout__body">
      <el-header class="layout__header">
        <button
          type="button"
          class="layout__icon-btn"
          :title="isCollapsed ? '展开侧栏' : '收起侧栏'"
          :aria-label="isCollapsed ? '展开侧栏' : '收起侧栏'"
          @click="toggleSidebar"
        >
          <AppIcon :name="isCollapsed ? 'chevron-right' : 'chevron-left'" :size="18" />
        </button>

        <span class="layout__title">{{ pageTitle }}</span>

        <el-dropdown @command="onCommand">
          <div class="layout__user" tabindex="0">
            <span class="layout__user-avatar">{{ userInitial }}</span>
            <span class="layout__user-name">{{ userName || '未登录' }}</span>
            <AppIcon name="chevron-right" :size="14" class="layout__user-caret" />
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <AppIcon name="user" :size="15" class="layout__dd-icon" />个人设置
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <AppIcon name="logout" :size="15" class="layout__dd-icon" />退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="layout__main">
        <div class="layout__main-inner">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import AppIcon from '@/components/AppIcon.vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const isCollapsed = computed(() => appStore.sidebarCollapsed)
const activeMenu = computed(() => route.path)
const pageTitle = computed(() => (route.meta.title as string) || '工作台')
const userName = computed(() => userStore.userInfo?.nickname || userStore.userInfo?.username || '')
const userInitial = computed(() => userName.value.slice(0, 1) || '工')

const menuItems = [
  { path: '/dashboard', label: '工作台', icon: 'chart' as const },
  { path: '/notes', label: '笔记管理', icon: 'doc' as const },
  { path: '/articles', label: '文章管理', icon: 'edit' as const },
  { path: '/categories', label: '分类管理', icon: 'folder' as const },
  { path: '/tags', label: '标签管理', icon: 'tag' as const },
  { path: '/profile', label: '个人设置', icon: 'user' as const }
]

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

/* —— 侧边栏 —— */
.layout__aside {
  background: var(--blog-surface);
  border-right: 1px solid var(--blog-line);
  transition: width 0.2s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.layout__logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  border-bottom: 1px solid var(--blog-line);
  flex: none;
}

.layout__logo-mark {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: var(--blog-accent);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: none;
}

.layout__logo-text {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--blog-ink);
  white-space: nowrap;
}

.layout__menu {
  border-right: none;
  padding: 8px 0;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;

  :deep(.el-menu-item) {
    height: 40px;
    line-height: 40px;
    margin: 2px 8px;
    padding-left: 12px !important;
    border-radius: 8px;
    font-size: 14px;
    color: var(--blog-ink-soft);
    position: relative;
    transition: background-color 0.2s, color 0.2s;

    &:hover {
      background-color: var(--blog-paper);
      color: var(--blog-ink);
    }

    &.is-active {
      background-color: var(--blog-accent-soft);
      color: var(--blog-accent);
      font-weight: 500;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 10px;
        bottom: 10px;
        width: 3px;
        border-radius: 0 3px 3px 0;
        background: var(--blog-accent);
      }
    }
  }

  /* 收起状态：仅图标，居中（.el-menu--collapse 添加在本元素上）*/
  &.el-menu--collapse {
    :deep(.el-menu-item) {
      padding-left: 0 !important;
      justify-content: center;
    }

    .layout__menu-icon {
      margin-right: 0;
    }
  }
}

.layout__menu-icon {
  margin-right: 10px;
}

/* —— 顶栏 —— */
.layout__body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.layout__header {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--blog-line);
}

.layout__icon-btn {
  appearance: none;
  border: 0;
  background: transparent;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--blog-radius-sm);
  color: var(--blog-ink-mute);
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s, transform 0.15s;

  &:hover {
    background: var(--blog-accent-soft);
    color: var(--blog-accent);
  }

  &:active {
    transform: translateY(1px);
  }
}

.layout__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--blog-ink);
  flex: 1;
  letter-spacing: -0.01em;
}

.layout__user {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px 4px 4px;
  border-radius: 999px;
  cursor: pointer;
  outline: none;
  transition: background-color 0.2s;

  &:hover,
  &:focus-visible {
    background: var(--blog-accent-soft);
  }
}

.layout__user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: var(--blog-accent);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: none;
}

.layout__user-name {
  font-size: 14px;
  color: var(--blog-ink);
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.layout__user-caret {
  color: var(--blog-ink-mute);
  transform: rotate(90deg);
}

.layout__dd-icon {
  margin-right: 8px;
}

/* —— 主区 —— */
.layout__main {
  background: var(--blog-paper);
  padding: 24px 28px;
  overflow: auto;
}

.layout__main-inner {
  max-width: var(--blog-page-max);
  margin: 0 auto;
  width: 100%;
}
</style>
