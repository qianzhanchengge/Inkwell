import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getBlogToken, removeBlogToken } from '@/utils/auth'
import { useLoginDialogStore } from '@/stores/loginDialog'

declare module 'axios' {
  export interface AxiosRequestConfig {
    /** 静默请求：401 时只清理会话，不弹出登录弹窗（如页面加载时校验登录态） */
    skipAuthDialog?: boolean
  }
}

/**
 * 博客前台专用 axios 实例。
 * 与工作台 `request.ts` 完全独立：只携带博客 token，401 时清理博客会话并弹博客登录弹窗，
 * 绝不跳转工作台登录页（`/login`）。
 */
const blogRequest = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000
})

blogRequest.interceptors.request.use((config) => {
  const token = getBlogToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function handleUnauthorized(skipDialog?: boolean) {
  removeBlogToken()
  if (skipDialog) return
  const dialog = useLoginDialogStore()
  if (!dialog.visible) {
    // 弹窗本身返回 Promise（用户登录成功/取消后 resolve），此处不阻塞请求链
    dialog.open().catch(() => {})
  }
}

blogRequest.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 200) {
      if (res.code === 401) {
        handleUnauthorized(response.config?.skipAuthDialog)
        ElMessage.warning(res.message || '请先登录博客账号')
      } else {
        ElMessage.error(res.message || '请求失败')
      }
      return Promise.reject(new Error(res.message))
    }
    return res.data
  },
  (error) => {
    const status = error.response?.status
    const msg = error.response?.data?.message || error.message || '网络错误'
    if (status === 401) {
      handleUnauthorized(error.config?.skipAuthDialog)
    } else if (status === 403) {
      // 权限不足：可能是博客会话已失效（如账号被禁用）
      removeBlogToken()
    }
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default blogRequest
