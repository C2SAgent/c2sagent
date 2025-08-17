// src/i18n/types.ts

// 1. 定义支持的语言类型
export type Locale = 'zh-CN' | 'en-US'

// 2. 定义语言包结构
export interface I18nMessages {
  common: {
    save: string
    cancel: string
    confirm: string
  }
  login: {
    title: string
    username: string
    password: string
  }
  errors: {
    required: string
    invalid: string
  }
}

// 3. 声明 vue-i18n 类型扩展
declare module 'vue-i18n' {
  export interface DefineLocaleMessage extends I18nMessages {}
}
