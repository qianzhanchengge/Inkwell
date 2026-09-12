export const APP_TITLE = import.meta.env.VITE_APP_TITLE || '工作台'

export const NOTE_STATUS: Record<number, string> = {
  0: '已删除',
  1: '正常'
}

export const ARTICLE_STATUS: Record<number, string> = {
  0: '草稿',
  1: '已发布',
  2: '已下架'
}

export const CATEGORY_TYPE: Record<number, string> = {
  1: '笔记分类',
  2: '文章分类'
}

export const PAGE_SIZES = [10, 20, 50, 100]
