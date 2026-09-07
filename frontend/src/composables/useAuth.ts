import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

export function useAuth() {
  const userStore = useUserStore()
  const isLoggedIn = computed(() => !!userStore.token)

  return { userStore, isLoggedIn }
}
