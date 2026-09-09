import request from './request'

export interface ShareResult {
  url?: string
}

export function recordShare(articleId: number | string, platform = 'link'): Promise<ShareResult> {
  return request.post(`/articles/${articleId}/share`, { platform })
}
