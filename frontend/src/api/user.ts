import request from './request'
import type { UserInfo } from '@/types/user'

export interface UpdateProfileParams {
  nickname?: string
  bio?: string
  avatar?: string
}

export interface UpdatePasswordParams {
  old_password: string
  new_password: string
}

export function updateProfile(data: UpdateProfileParams): Promise<UserInfo> {
  return request.put('/users/profile', data)
}

export function updatePassword(data: UpdatePasswordParams): Promise<null> {
  return request.put('/users/password', data)
}

export function uploadAvatar(file: File): Promise<{ url: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/users/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
