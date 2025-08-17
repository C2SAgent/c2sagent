// src/i18n/index.ts
import { createI18n } from 'vue-i18n'
import type { I18nMessages } from './types'

// 导入语言包
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'

// 创建 i18n 实例
const i18n = createI18n({
  legacy: false, // 使用 Composition API
  locale: 'zh-CN', // 默认语言
  messages: {
    'zh-CN': zhCN as unknown as I18nMessages,
    'en-US': enUS as unknown as I18nMessages
  }
})

export default i18n
