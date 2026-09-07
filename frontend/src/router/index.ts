import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { getToken } from '@/utils/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/Login.vue'),
    meta: { public: true, title: '登录' }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/register/Register.vue'),
    meta: { public: true, title: '注册' }
  },
  {
    path: '/',
    component: () => import('@/views/layout/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/dashboard/Dashboard.vue'), meta: { title: '工作台' } },
      { path: 'notes', name: 'notes', component: () => import('@/views/notes/NoteList.vue'), meta: { title: '笔记管理' } },
      { path: 'notes/new', name: 'note-new', component: () => import('@/views/notes/NoteEditor.vue'), meta: { title: '新建笔记' } },
      { path: 'notes/:id', name: 'note-detail', component: () => import('@/views/notes/NoteDetail.vue'), meta: { title: '笔记详情' } },
      { path: 'notes/:id/edit', name: 'note-edit', component: () => import('@/views/notes/NoteEditor.vue'), meta: { title: '编辑笔记' } },
      { path: 'articles', name: 'articles', component: () => import('@/views/articles/ArticleList.vue'), meta: { title: '文章管理' } },
      { path: 'articles/new', name: 'article-new', component: () => import('@/views/articles/ArticleEditor.vue'), meta: { title: '新建文章' } },
      { path: 'articles/:id/edit', name: 'article-edit', component: () => import('@/views/articles/ArticleEditor.vue'), meta: { title: '编辑文章' } },
      { path: 'categories', name: 'categories', component: () => import('@/views/categories/CategoryManage.vue'), meta: { title: '分类管理' } },
      { path: 'tags', name: 'tags', component: () => import('@/views/tags/TagManage.vue'), meta: { title: '标签管理' } },
      { path: 'profile', name: 'profile', component: () => import('@/views/profile/Profile.vue'), meta: { title: '个人设置' } }
    ]
  },
  {
    path: '/p/articles',
    name: 'public-articles',
    component: () => import('@/views/articles/ArticlePublic.vue'),
    meta: { public: true, title: '文章广场' }
  },
  {
    path: '/p/articles/:id',
    name: 'public-article-detail',
    component: () => import('@/views/articles/ArticleDetail.vue'),
    meta: { public: true, title: '文章详情' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const token = getToken()
  const isPublic = to.meta.public === true
  if (!isPublic && !token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
