import { useLoginDialogStore } from '@/stores/loginDialog'
import { useUserStore } from '@/stores/user'

/**
 * 登录拦截工具。
 * 用法：const ok = await ensureLogin()；ok 为 true 再执行需登录的操作。
 */
export function useLogin() {
  const dialogStore = useLoginDialogStore()
  const userStore = useUserStore()

  function ensureLogin(): Promise<boolean> {
    if (userStore.token) return Promise.resolve(true)
    return dialogStore.open()
  }

  return { ensureLogin }
}
