import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserInfo } from '@/types/user'
import * as authApi from '@/api/auth'
import {
  getToken,
  setToken,
  removeToken,
  getRefreshToken,
  setRefreshToken
} from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null)
  const token = ref<string | null>(getToken())

  function setUser(info: UserInfo | null) {
    userInfo.value = info
  }

  function applyTokens(access: string, refresh: string) {
    token.value = access
    setToken(access)
    setRefreshToken(refresh)
  }

  function clearAuth() {
    userInfo.value = null
    token.value = null
    removeToken()
  }

  async function loginAction(params: authApi.LoginParams) {
    const data = await authApi.login(params)
    applyTokens(data.access_token, data.refresh_token)
    return data
  }

  async function registerAction(params: authApi.RegisterParams) {
    return authApi.register(params)
  }

  async function fetchMe() {
    const user = await authApi.getMe()
    setUser(user)
    return user
  }

  function logout() {
    clearAuth()
    authApi.logout().catch(() => {})
  }

  async function refreshAction() {
    const refresh = getRefreshToken()
    if (!refresh) {
      throw new Error('无刷新令牌')
    }
    const data = await authApi.refreshToken({ refresh_token: refresh })
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
