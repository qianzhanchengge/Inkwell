<template>
  <div class="blog-layout">
    <a class="blog-layout__skip" href="#blog-main">跳到正文</a>

    <header class="blog-layout__header">
      <div class="blog-layout__inner">
        <router-link to="/blog" class="blog-layout__logo">
          <span class="blog-layout__logo-mark">博</span>
          <span class="blog-layout__logo-text">博客</span>
        </router-link>

        <nav class="blog-layout__nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="blog-layout__nav-link"
            :class="{ 'is-active': isActive(item.path) }"
          >
            {{ item.label }}
          </router-link>
        </nav>

        <div class="blog-layout__right">
          <template v-if="blogUserStore.token">
            <span class="blog-layout__user">
              {{ blogUserStore.userInfo?.nickname || blogUserStore.userInfo?.username || '博客用户' }}
            </span>
            <button type="button" class="blog-layout__link" @click="onLogout">退出</button>
          </template>
          <button v-else type="button" class="blog-layout__link" @click="openLoginDialog">
            登录
          </button>
          <router-link v-if="hasWorkbenchToken" to="/dashboard" class="blog-layout__wb">
            进入工作台
          </router-link>
        </div>
      </div>
    </header>

    <main id="blog-main" class="blog-layout__main">
      <router-view />
    </main>

    <footer class="blog-layout__footer">
      <div class="blog-layout__footer-inner">
        <span class="blog-layout__footer-brand">工作台 · 博客系统</span>
        <nav class="blog-layout__footer-links">
          <router-link to="/blog/archive">归档</router-link>
          <router-link to="/blog/tags">标签</router-link>
          <router-link to="/dashboard">进入工作台</router-link>
        </nav>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useBlogUserStore } from '@/stores/blogUser'
import { useLoginDialogStore } from '@/stores/loginDialog'
import { getToken } from '@/utils/auth'

const route = useRoute()
const blogUserStore = useBlogUserStore()
const dialogStore = useLoginDialogStore()

const navItems = [
  { path: '/blog', label: '首页' },
  { path: '/blog/categories', label: '分类' },
  { path: '/blog/tags', label: '标签' },
  { path: '/blog/archive', label: '归档' }
]

/**
 * 当前栏目高亮。
 * 首页必须精确匹配：`/blog` 是所有子路由的祖先，用 router-link-active 会处处命中。
 */
function isActive(path: string): boolean {
  return path === '/blog' ? route.path === '/blog' : route.path.startsWith(path)
}

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
  /*
   * 设计 token（品牌色板 / 阴影 / 圆角 / Element 主题覆盖）已提升为全局，
   * 见 src/assets/styles/index.scss；此处仅保留博客特有项，避免两处定义漂移。
   */
  /* 博客正文基准字号 15px（工作台为 14px）：保持博客阅读排版不变 */
  --el-font-size-base: 15px;

  min-height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--blog-paper);
  color: var(--blog-ink);
  font-family: 'Inter var', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'HarmonyOS Sans SC', 'Source Han Sans SC', 'Noto Sans CJK SC', 'Hiragino Sans GB',
    'Microsoft YaHei', sans-serif;
  font-feature-settings: 'kern' 1;
  -webkit-font-smoothing: antialiased;

  /* 焦点可见（跨组件生效） */
  :deep(a:focus-visible),
  :deep(button:focus-visible),
  :deep(input:focus-visible),
  :deep(textarea:focus-visible) {
    outline: 2px solid var(--blog-accent);
    outline-offset: 2px;
    border-radius: 4px;
  }
}

/* 跳到正文：默认视觉隐藏，聚焦时显示 */
.blog-layout__skip {
  position: absolute;
  left: -9999px;
  top: 0;
  z-index: 30;
  padding: 8px 14px;
  background: var(--blog-accent);
  color: #fff;
  font-size: 13px;
  border-radius: 0 0 var(--blog-radius-sm) 0;

  &:focus {
    left: 0;
  }
}

.blog-layout__header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--blog-line);
}

.blog-layout__inner {
  max-width: var(--blog-container);
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 28px;
}

.blog-layout__logo {
  display: flex;
  align-items: center;
  gap: 9px;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.85;
  }
}

.blog-layout__logo-mark {
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
  letter-spacing: 0;
}

.blog-layout__logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--blog-ink);
  letter-spacing: -0.01em;
}

.blog-layout__nav {
  flex: 1;
  display: flex;
  gap: 22px;
}

.blog-layout__nav-link {
  position: relative;
  font-size: 14px;
  color: var(--blog-ink-soft);
  padding: 4px 2px;
  transition: color 0.2s, transform 0.15s;

  &::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    bottom: -3px;
    height: 2px;
    background: var(--blog-accent);
    border-radius: 1px;
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.25s ease;
  }

  &:hover {
    color: var(--blog-ink);
  }

  &:active {
    transform: translateY(1px);
  }

  &.is-active {
    color: var(--blog-accent);
    font-weight: 500;

    &::after {
      transform: scaleX(1);
    }
  }
}

.blog-layout__right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.blog-layout__user {
  font-size: 14px;
  color: var(--blog-ink-soft);
}

.blog-layout__link {
  appearance: none;
  border: 0;
  background: transparent;
  padding: 0;
  font: inherit;
  font-size: 14px;
  color: var(--blog-ink-soft);
  cursor: pointer;
  transition: color 0.2s, transform 0.15s;

  &:hover {
    color: var(--blog-accent);
  }

  &:active {
    transform: translateY(1px);
  }
}

.blog-layout__wb {
  font-size: 14px;
  color: var(--blog-accent);
  transition: color 0.2s;

  &:hover {
    color: var(--blog-accent-dark);
  }
}

.blog-layout__main {
  flex: 1;
  width: 100%;
}

.blog-layout__footer {
  border-top: 1px solid var(--blog-line);
  padding: 32px 20px 40px;
  margin-top: 24px;
}

.blog-layout__footer-inner {
  max-width: var(--blog-container);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 13px;
  color: var(--blog-ink-mute);
}

.blog-layout__footer-brand {
  letter-spacing: 0.02em;
}

.blog-layout__footer-links {
  display: flex;
  gap: 20px;

  a {
    color: var(--blog-ink-mute);
    transition: color 0.2s;

    &:hover {
      color: var(--blog-accent);
    }
  }
}
</style>
