<template>
  <svg
    class="app-icon"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
    v-html="markup"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

type IconName =
  | 'search'
  | 'chevron-left'
  | 'chevron-right'
  | 'plus'
  | 'edit'
  | 'trash'
  | 'eye'
  | 'chart'
  | 'doc'
  | 'folder'
  | 'tag'
  | 'user'
  | 'logout'
  | 'inbox'
  | 'arrow-up'
  | 'arrow-down'
  | 'heart'
  | 'bookmark'
  | 'share'
  | 'comment'
  | 'clock'
  | 'link'

/**
 * 零依赖内联 SVG 图标。
 * 统一描边风格（24 网格 / 1.75 线宽 / currentColor），避免引入图标库。
 */
const props = withDefaults(
  defineProps<{
    name: IconName
    size?: number | string
    strokeWidth?: number
  }>(),
  { size: 16, strokeWidth: 1.75 }
)

/** 每个图标仅存内联几何；内容为静态字符串，无外部输入 */
const ICONS: Record<IconName, string> = {
  search: '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5 21 21"/>',
  'chevron-left': '<path d="M15 5 8 12l7 7"/>',
  'chevron-right': '<path d="M9 5l7 7-7 7"/>',
  plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
  edit: '<path d="M4 20h4L18.5 9.5a2.12 2.12 0 0 0-3-3L5 17v3z"/><path d="M13.5 6.5 17.5 10.5"/>',
  trash: '<path d="M4 7h16"/><path d="M9 7V5h6v2"/><path d="M6.5 7 7.5 20h9L17.5 7"/>',
  eye: '<path d="M2.5 12S6.5 6 12 6s9.5 6 9.5 6-4 6-9.5 6-9.5-6-9.5-6z"/><circle cx="12" cy="12" r="2.5"/>',
  chart: '<path d="M4 20V4"/><path d="M4 20h16"/><path d="M8 17V11"/><path d="M13 17V7"/><path d="M18 17v-4"/>',
  doc: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/>',
  folder:
    '<path d="M3 7a2 2 0 0 1 2-2h3.5l2 2H19a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  tag: '<path d="M3 12.5 12 3.5h7a2 2 0 0 1 2 2v7l-9 9z"/><circle cx="16" cy="8" r="1.4"/>',
  user: '<circle cx="12" cy="8.5" r="3.5"/><path d="M5 20c1.4-3.4 4-5 7-5s5.6 1.6 7 5"/>',
  logout:
    '<path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3"/><path d="M10 8l4 4-4 4"/><path d="M14 12H4"/>',
  inbox:
    '<path d="M6 4h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><path d="M4 13h4l1.5 3h5L16 13h4"/>',
  'arrow-up': '<path d="M12 19V5"/><path d="M6 11l6-6 6 6"/>',
  'arrow-down': '<path d="M12 5v14"/><path d="M6 13l6 6 6-6"/>',
  heart:
    '<path d="M12 20s-7-4.6-7-9.5A4.5 4.5 0 0 1 12 7a4.5 4.5 0 0 1 7 3.5C19 15.4 12 20 12 20z"/>',
  bookmark: '<path d="M7 4h10a1 1 0 0 1 1 1v15l-6-4-6 4V5a1 1 0 0 1 1-1z"/>',
  share:
    '<circle cx="18" cy="6" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.2 10.8 15.8 7.2"/><path d="M8.2 13.2l7.6 3.6"/>',
  comment: '<path d="M20 12a7.5 7.5 0 0 1-10.9 6.7L4 20l1.3-4.1A7.5 7.5 0 1 1 20 12z"/>',
  clock: '<circle cx="12" cy="12" r="8"/><path d="M12 8v4.2l3 1.8"/>',
  link:
    '<path d="M10 13.5a3.5 3.5 0 0 0 5 0l3-3a3.5 3.5 0 1 0-5-5l-1 1"/><path d="M14 10.5a3.5 3.5 0 0 0-5 0l-3 3a3.5 3.5 0 1 0 5 5l1-1"/>'
}

const markup = computed(() => ICONS[props.name] ?? '')
</script>

<style scoped lang="scss">
.app-icon {
  display: inline-block;
  flex: none;
  vertical-align: -0.15em;
}
</style>
