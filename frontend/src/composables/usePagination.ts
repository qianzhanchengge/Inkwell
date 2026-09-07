import { ref, computed } from 'vue'

export function usePagination(initialPage = 1, initialPageSize = 10) {
  const page = ref(initialPage)
  const pageSize = ref(initialPageSize)
  const total = ref(0)

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  function reset() {
    page.value = 1
    total.value = 0
  }

  return { page, pageSize, total, totalPages, reset }
}
