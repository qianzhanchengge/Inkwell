import { ref, watch, type Ref } from 'vue'

export function useDebouncedRef<T>(initialValue: T, delay = 300) {
  const source = ref(initialValue) as Ref<T>
  const debounced = ref(initialValue) as Ref<T>
  let timer: ReturnType<typeof setTimeout> | null = null

  watch(source, (value) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      debounced.value = value
    }, delay)
  })

  return { source, debounced }
}
