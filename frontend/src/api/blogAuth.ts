import blogRequest from './blogRequest'
import type { UserInfo, LoginResult } from '@/types/user'

export interface BlogLoginParams {
  username: string
  password: string
}

export interface BlogRegisterParams {
  username: string
  email: string
  password: string
  nickname?: string
}

/** 博客登录：工作台用户与博客用户均可登录，签发博客 scope 令牌 */
export function blogLogin(data: BlogLoginParams): Promise<LoginResult> {
  return blogRequest.post('/blog/auth/login', data)
}

/** 博客注册：创建博客用户 */
export function blogRegister(data: BlogRegisterParams): Promise<UserInfo> {
  return blogRequest.post('/blog/auth/register', data)
}

export function blogLogout(): Promise<null> {
  return blogRequest.post('/blog/auth/logout')
}

export function blogRefreshToken(data: { refresh_token: string }): Promise<LoginResult> {
  return blogRequest.post('/blog/auth/refresh', data)
}

/** 获取博客当前用户（静默：失效时不弹窗，供页面加载校验登录态） */
export function getBlogMe(): Promise<UserInfo> {
  return blogRequest.get('/blog/auth/me', { skipAuthDialog: true })
}
