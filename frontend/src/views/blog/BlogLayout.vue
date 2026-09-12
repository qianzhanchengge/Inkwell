<template>
  <div class="blog-layout">
    <header class="blog-layout__header">
      <div class="blog-layout__inner">
        <router-link to="/blog" class="blog-layout__logo">博客</router-link>
        <nav class="blog-layout__nav">
          <router-link to="/blog">首页</router-link>
          <router-link to="/blog/categories">分类</router-link>
          <router-link to="/blog/tags">标签</router-link>
          <router-link to="/blog/archive">归档</router-link>
        </nav>
        <div class="blog-layout__right">
          <template v-if="blogUserStore.token">
            <span class="blog-layout__user">
              {{ blogUserStore.userInfo?.nickname || blogUserStore.userInfo?.username || '博客用户' }}
            </span>
            <el-button link type="primary" @click="onLogout">退出</el-button>
          </template>
          <el-button v-else link type="primary" @click="openLoginDialog">登录</el-button>
          <router-link v-if="hasWorkbenchToken" to="/dashboard" class="blog-layout__wb">
            进入工作台
          </router-link>
        </div>
      </div>
    </header>

    <main class="blog-layout__main">
      <router-view />
    </main>

    <footer class="blog-layout__footer">
      工作台 · 博客系统
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useBlogUserStore } from '@/stores/blogUser'
import { useLoginDialogStore } from '@/stores/loginDialog'
import { getToken } from '@/utils/auth'

const blogUserStore = useBlogUserStore()
const dialogStore = useLoginDialogStore()

// 工作台登录态仅用于显示「进入工作台」入口，不影响博客是否已登录
const hasWorkbenchToken = computed(() => !!getToken())

function openLoginDialog() {
  dialogStore.open().catch(() => {})
}

function onLogout() {
  blogUserStore.logout()
  ElMessage.success('已退出博客账号')
}
</script>

<style scoped lang="scss">
.blog-layout {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}
.blog-layout__header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}
.blog-layout__inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 16px;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.blog-layout__logo {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}
.blog-layout__nav {
  flex: 1;
  display: flex;
  gap: 18px;
  a {
    color: #606266;
    font-size: 14px;
    &:hover {
      color: #409eff;
    }
  }
}
.blog-layout__right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.blog-layout__user {
  font-size: 14px;
  color: #606266;
}
.blog-layout__wb {
  font-size: 14px;
  color: #409eff;
}
.blog-layout__main {
  flex: 1;
  width: 100%;
}
.blog-layout__footer {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  padding: 24px 16px;
}
</style>
