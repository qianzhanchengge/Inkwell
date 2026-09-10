/** 工作台与博客两套独立会话的本地存储（键名严禁共用）。 */
import type { UserInfo } from '@/types/user'

// ===== 工作台（后台）会话 =====
const TOKEN_KEY = 'workbench_token'
const REFRESH_TOKEN_KEY = 'workbench_refresh_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token)
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

// ===== 博客（前台）会话：与工作台完全隔离 =====
const BLOG_TOKEN_KEY = 'blog_token'
const BLOG_REFRESH_TOKEN_KEY = 'blog_refresh_token'
const BLOG_USER_KEY = 'blog_user_info'

export function getBlogToken(): string | null {
  return localStorage.getItem(BLOG_TOKEN_KEY)
}

export function setBlogToken(token: string): void {
  localStorage.setItem(BLOG_TOKEN_KEY, token)
}

export function getBlogRefreshToken(): string | null {
  return localStorage.getItem(BLOG_REFRESH_TOKEN_KEY)
}

export function setBlogRefreshToken(token: string): void {
  localStorage.setItem(BLOG_REFRESH_TOKEN_KEY, token)
}

export function getBlogUserInfo(): UserInfo | null {
  const raw = localStorage.getItem(BLOG_USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserInfo
  } catch {
    return null
  }
}

export function setBlogUserInfo(info: UserInfo | null): void {
  if (info) {
    localStorage.setItem(BLOG_USER_KEY, JSON.stringify(info))
  } else {
    localStorage.removeItem(BLOG_USER_KEY)
  }
}

export function removeBlogToken(): void {
  localStorage.removeItem(BLOG_TOKEN_KEY)
  localStorage.removeItem(BLOG_REFRESH_TOKEN_KEY)
  localStorage.removeItem(BLOG_USER_KEY)
}
