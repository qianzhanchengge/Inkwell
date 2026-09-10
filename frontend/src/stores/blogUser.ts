import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserInfo } from '@/types/user'
import * as blogAuthApi from '@/api/blogAuth'
import {
  getBlogToken,
  setBlogToken,
  removeBlogToken,
  getBlogRefreshToken,
  setBlogRefreshToken,
  getBlogUserInfo,
  setBlogUserInfo
} from '@/utils/auth'

/**
 * 博客前台登录态（与工作台 `stores/user.ts` 完全独立）。
 * 登录工作台不会让本 store 进入已登录状态。
 */
export const useBlogUserStore = defineStore('blogUser', () => {
  const userInfo = ref<UserInfo | null>(getBlogUserInfo())
  const token = ref<string | null>(getBlogToken())

  function setUser(info: UserInfo | null) {
    userInfo.value = info
    setBlogUserInfo(info)
  }

  function applyTokens(access: string, refresh: string) {
    token.value = access
    setBlogToken(access)
    setBlogRefreshToken(refresh)
  }

  function clearAuth() {
    setUser(null)
    token.value = null
    removeBlogToken()
  }

  async function loginAction(params: blogAuthApi.BlogLoginParams) {
    const data = await blogAuthApi.blogLogin(params)
    applyTokens(data.access_token, data.refresh_token)
    return data
  }

  async function registerAction(params: blogAuthApi.BlogRegisterParams) {
    return blogAuthApi.blogRegister(params)
  }

  async function fetchMe() {
    const user = await blogAuthApi.getBlogMe()
    setUser(user)
    return user
  }

  function logout() {
    clearAuth()
    blogAuthApi.blogLogout().catch(() => {})
  }

  async function refreshAction() {
    const refresh = getBlogRefreshToken()
    if (!refresh) {
      throw new Error('无博客刷新令牌')
    }
    const data = await blogAuthApi.blogRefreshToken({ refresh_token: refresh })
    applyTokens(data.access_token, data.refresh_token)
    return data
  }

  return {
    userInfo,
    token,
    setUser,
    applyTokens,
    clearAuth,
    loginAction,
    registerAction,
    fetchMe,
    logout,
    refreshAction
  }
})
