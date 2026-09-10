import { useLoginDialogStore } from '@/stores/loginDialog'
import { useBlogUserStore } from '@/stores/blogUser'

/**
 * 博客登录拦截工具。
 * 用法：const ok = await ensureLogin()；ok 为 true 再执行需登录的博客操作。
 * 注意：这里只认博客 token —— 工作台已登录不代表博客已登录。
 */
export function useLogin() {
  const dialogStore = useLoginDialogStore()
  const blogUserStore = useBlogUserStore()

  function ensureLogin(): Promise<boolean> {
    if (blogUserStore.token) return Promise.resolve(true)
    return dialogStore.open()
  }

  return { ensureLogin }
}
