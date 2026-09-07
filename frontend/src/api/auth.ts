import request from './request'
import type { UserInfo, LoginResult } from '@/types/user'

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  email: string
  password: string
  nickname?: string
}

export function login(data: LoginParams): Promise<LoginResult> {
  return request.post('/auth/login', data)
}

export function register(data: RegisterParams): Promise<UserInfo> {
  return request.post('/auth/register', data)
}

export function logout(): Promise<null> {
  return request.post('/auth/logout')
}

export function refreshToken(data: { refresh_token: string }): Promise<LoginResult> {
  return request.post('/auth/refresh', data)
}

export function getMe(): Promise<UserInfo> {
  return request.get('/auth/me')
}
