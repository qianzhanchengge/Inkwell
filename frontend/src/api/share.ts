import blogRequest from './blogRequest'

export interface ShareResult {
  url?: string
}

/**
 * 记录一次分享（需博客 token）。
 * 复制链接本身对游客可用，仅在已登录博客时调用本接口做统计。
 */
export function recordShare(articleId: number | string, platform = 'link'): Promise<ShareResult> {
  return blogRequest.post(`/articles/${articleId}/share`, { platform })
}
