import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserInfo } from '@/types/user'
import { getToken, setToken, removeToken } from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null)
  const token = ref<string | null>(getToken())

  function setUser(info: UserInfo | null) {
    userInfo.value = info
  }

  function setAuthToken(value: string | null) {
    token.value = value
    if (value) {
      setToken(value)
    } else {
      removeToken()
    }
  }

  function logout() {
    setUser(null)
    setAuthToken(null)
  }

  return { userInfo, token, setUser, setAuthToken, logout }
})
