import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import type { LoginParams, RegisterParams } from '@/api/auth'

export function useAuth() {
  const userStore = useUserStore()
  const isLoggedIn = computed(() => !!userStore.token)

  async function login(params: LoginParams) {
    const data = await userStore.loginAction(params)
    await userStore.fetchMe()
    return data
  }

  async function register(params: RegisterParams) {
    return userStore.registerAction(params)
  }

  async function logout() {
    userStore.logout()
  }

  async function fetchMe() {
    return userStore.fetchMe()
  }

  return { userStore, isLoggedIn, login, register, logout, fetchMe }
}
