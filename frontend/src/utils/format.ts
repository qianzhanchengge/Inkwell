import dayjs from 'dayjs'

export function formatDateTime(date: string | Date, template = 'YYYY-MM-DD HH:mm:ss'): string {
  return dayjs(date).format(template)
}

export function formatDate(date: string | Date): string {
  return dayjs(date).format('YYYY-MM-DD')
}

export function formatCount(count: number): string {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`
  }
  return String(count)
}
