import { createApp } from 'vue'
import { createPinia } from 'pinia' // 引入 Pinia
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

const app = createApp(App)

// 1. 必须先注册 Pinia
const pinia = createPinia()
app.use(pinia)

// 2. 注册路由
app.use(router)

app.use(ElementPlus)
app.use(i18n)
// 3. 挂载应用（不要在这里调用 store）
app.mount('#app')

// 4. 可选：在组件内初始化 store（推荐）
// 将初始化逻辑移到 App.vue 的 onMounted 中
