import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

// Import Ant Design Vue
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

const app = createApp(App)

// Use Ant Design Vue
app.use(Antd)
app.use(router)

app.mount('#app')
