import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 全局登录弹窗状态。
 * 访客触发需登录的操作时，通过 useLogin().ensureLogin() 打开此弹窗，
 * 登录成功后 resolve true，取消则 resolve false（不跳转页面）。
 */
export const useLoginDialogStore = defineStore('loginDialog', () => {
  const visible = ref(false)
  let resolver: ((ok: boolean) => void) | null = null

  function open(): Promise<boolean> {
    visible.value = true
    return new Promise<boolean>((resolve) => {
      resolver = resolve
    })
  }

  function success() {
    visible.value = false
    if (resolver) {
      resolver(true)
      resolver = null
    }
  }

  function cancel() {
    visible.value = false
    if (resolver) {
      resolver(false)
      resolver = null
    }
  }

  return { visible, open, success, cancel }
})
