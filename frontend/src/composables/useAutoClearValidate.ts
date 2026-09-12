import type { Ref } from 'vue'
import type { FormInstance } from 'element-plus'

/**
 * 让表单校验失败提示在指定时间后自动消失（默认 5 秒）。
 *
 * 用法：
 *   <el-form ref="formRef" :rules="rules" @validate="onValidate">
 *   const onValidate = useAutoClearValidate(formRef)
 *
 * 说明：Element Plus 的表单错误提示默认会一直保留到下次校验，
 * 用户只是点进输入框未输入也会留下红字；这里在校验未通过时
 * 延迟清除该字段的提示，避免红字长期停留。
 */
export function useAutoClearValidate(
  formRef: Ref<FormInstance | undefined>,
  delay = 5000
) {
  return (prop: string, isValid: boolean) => {
    if (isValid) return
    window.setTimeout(() => formRef.value?.clearValidate(prop), delay)
  }
}
