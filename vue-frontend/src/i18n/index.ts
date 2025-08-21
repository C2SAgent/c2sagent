import { createI18n } from 'vue-i18n';
import en from './locales/en-US.json';
import zh from './locales/zh-CN.json';

const getInitialLocale = () => {
  try {
    // 只在客户端环境下访问 localStorage
    if (typeof window !== 'undefined' && window.localStorage) {
      const saved = localStorage.getItem('userLanguage');
      if (saved) return saved;

      // 如果没有保存的语言，根据浏览器语言自动选择
      const browserLang = navigator.language;
      if (browserLang.startsWith('zh')) return 'zh-CN';
      if (browserLang.startsWith('en')) return 'en-US';
    }
    return 'zh-CN'; // 默认值
  } catch (e) {
    return 'zh-CN'; // 出错时返回默认值
  }
};

const i18n = createI18n({
  legacy: false,
  locale: getInitialLocale(), // 使用获取到的初始语言
  fallbackLocale: 'en-US',
  messages: {
    'en-US': en,
    'zh-CN': zh,
  },
});

export default i18n;
