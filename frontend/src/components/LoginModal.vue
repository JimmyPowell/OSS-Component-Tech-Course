<template>
  <Teleport to="body">
    <div 
      v-if="isVisible" 
      class="modal-overlay" 
      :class="{ 'fade-in': showModal }"
      @click="handleOverlayClick"
    >
      <div class="modal-container" :class="{ 'slide-in': showModal }">
        <div class="modal-card">
          <!-- 关闭按钮 -->
          <button class="close-btn" @click="closeModal">
            <i class="iconfont icon-close"></i>
          </button>
          
          <div class="modal-header">
            <div class="logo-section">
              <div class="navbar-logo-modal"></div>
              <h1 class="modal-title webfont">欢迎回来</h1>
              <p class="modal-subtitle">登录您的账户，继续学习之旅</p>
            </div>
          </div>
          
          <div class="modal-form">
            <!-- 错误和成功通知组件 -->
            <Notification
              ref="errorNotification"
              :message="errorMessage"
              type="error"
              :duration="3000"
            />
            <Notification
              ref="successNotification"
              :message="successMessage"
              type="success"
              :duration="3000"
            />
            <form @submit.prevent="handleLogin">
              <div class="form-group">
                <label for="username" class="form-label">邮箱/用户名</label>
                <div class="input-wrapper">
                  <span class="input-icon">
                    <i class="iconfont icon-email"></i>
                  </span>
                  <input
                    id="username"
                    v-model="loginForm.identifier"
                    type="text"
                    class="form-input"
                    placeholder="请输入您的邮箱或用户名"
                    required
                  />
                </div>
              </div>
              
              <div class="form-group">
                <label for="password" class="form-label">密码</label>
                <div class="input-wrapper">
                  <span class="input-icon">
                    <i class="iconfont icon-lock"></i>
                  </span>
                  <input
                    id="password"
                    v-model="loginForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-input"
                    placeholder="请输入您的密码"
                    required
                  />
                  <button
                    type="button"
                    class="password-toggle"
                    @click="showPassword = !showPassword"
                  >
                    <i :class="showPassword ? 'iconfont icon-eye-open' : 'iconfont icon-eye-close'"></i>
                  </button>
                </div>
              </div>
              
              <div class="form-options">
                <label class="remember-me">
                  <input v-model="loginForm.remember" type="checkbox" />
                  <span class="checkmark"></span>
                  记住我
                </label>
                <a href="#" class="forgot-password">忘记密码？</a>
              </div>
              
              <button type="submit" class="btn-login" :disabled="isLoading">
                <span v-if="isLoading" class="loading-spinner"></span>
                {{ isLoading ? '登录中...' : '登录' }}
              </button>
            </form>
            

            
            <div class="register-link">
              <span>还没有账户？</span>
              <button @click="switchToRegister" class="register-btn">立即注册</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import Notification from './Notification.vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'switch-to-register'])

const loginForm = reactive({
  identifier: '',
  password: '',
  remember: false
})

const showPassword = ref(false)
const isLoading = ref(false)
const isVisible = ref(false)
const showModal = ref(false)
const errorMessage = ref('')
const successMessage = ref('登录成功！正在为您跳转...')

// 通知组件引用
const errorNotification = ref(null)
const successNotification = ref(null)

// 先定义函数
const openModal = () => {
  isVisible.value = true
  // 防止背景页面滚动
  document.body.style.overflow = 'hidden'
  // 延迟显示动画，确保DOM已渲染
  setTimeout(() => {
    showModal.value = true
  }, 10)
}

const closeModal = () => {
  showModal.value = false
  // 恢复背景页面滚动
  document.body.style.overflow = ''
  // 等待动画完成后隐藏
  setTimeout(() => {
    isVisible.value = false
    emit('update:modelValue', false)
  }, 300)
}

// 监听props变化
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    openModal()
  } else {
    closeModal()
  }
}, { immediate: true })

const handleOverlayClick = (e) => {
  if (e.target === e.currentTarget) {
    closeModal()
  }
}

const switchToRegister = () => {
  emit('switch-to-register')
}

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    // 调用Pinia store中的登录方法
    const result = await authStore.login(loginForm.identifier, loginForm.password)
    
    if (result.success) {
      // 登录成功显示通知
      successNotification.value.show()
      
      // 如果记住登录状态，可以设置本地存储标记
      if (loginForm.remember) {
        localStorage.setItem('rememberLogin', 'true')
      } else {
        localStorage.removeItem('rememberLogin')
      }
      
      // 延迟关闭模态框和跳转到首页或其他页面
      setTimeout(() => {
        closeModal()
        router.push('/')
      }, 1200)
    } else {
      // 登录失败显示错误通知
      errorMessage.value = result.message
      errorNotification.value.show()
      
      // 登录失败处理（如清空密码字段）
      loginForm.password = ''
      
      // 如果出现401错误（用户名/密码错误），聚焦用户名字段
      if (result.originalError?.response?.status === 401) {
        setTimeout(() => {
          document.getElementById('username').focus()
        }, 100)
      }
    }
  } catch (error) {
    console.error('登录失败:', error)
    errorMessage.value = '登录过程中发生错误，请稍后重试'
    errorNotification.value.show()
    loginForm.password = '' // 清空密码字段
  } finally {
    isLoading.value = false
  }
}

// 社交登录功能已移除，保留此函数作为扩展示例
const handleSocialLogin = (provider) => {
  console.log(`社交登录功能已移除: ${provider}`)
}

// ESC键关闭
const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.modelValue) {
    closeModal()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// 加载已存储的用户名（如果启用了记住我）
onMounted(() => {
  if (localStorage.getItem('rememberLogin') === 'true') {
    const savedUser = JSON.parse(localStorage.getItem('user'))
    if (savedUser?.username || savedUser?.email) {
      loginForm.identifier = savedUser.username || savedUser.email
      loginForm.remember = true
    }
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1000;
  opacity: 0;
  transition: all 0.3s ease;
}

.modal-overlay.fade-in {
  opacity: 1;
}

.modal-container {
  width: 100%;
  max-width: 500px;
  position: relative;
  transform: translateY(30px) scale(0.95);
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-container.slide-in {
  transform: translateY(0) scale(1);
}

.modal-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 
    0 0 0 1px rgba(255, 255, 255, 0.2),
    0 20px 40px rgba(0, 0, 0, 0.15),
    0 0 60px rgba(135, 206, 235, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.4);
  position: relative;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #666;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.2);
  color: #333;
}

.modal-header {
  text-align: center;
  margin-bottom: 30px;
}

.navbar-logo-modal {
  width: 120px;
  height: 60px;
  background-repeat: no-repeat;
  background-position: center;
  background-image: url('/images/logo.png');
  background-size: contain;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-title {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 8px;
}

.modal-subtitle {
  color: #718096;
  font-size: 16px;
  margin: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2d3748;
  font-size: 14px;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0aec0;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 15px 15px 15px 45px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #545ae7;
  box-shadow: 0 0 0 3px rgba(84, 90, 231, 0.1);
}

.password-toggle {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  padding: 5px;
  transition: color 0.3s ease;
}

.password-toggle:hover {
  color: #545ae7;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.remember-me {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #4a5568;
}

.remember-me input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  margin-right: 8px;
  position: relative;
  transition: all 0.3s ease;
}

.remember-me input:checked + .checkmark {
  background: #545ae7;
  border-color: #545ae7;
}

.remember-me input:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  color: white;
  font-size: 12px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.forgot-password {
  color: #545ae7;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #4c51bf;
}

.btn-login {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #545ae7, #6b66e9);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(84, 90, 231, 0.3);
}

.btn-login:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Consistent styles for secondary button (used in register modal) */
.btn-secondary {
  flex: 1;
  padding: 15px;
  background: #e2e8f0;
  color: #2d3748;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #cbd5e0;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.divider {
  text-align: center;
  margin: 30px 0;
  position: relative;
  color: #a0aec0;
  font-size: 14px;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e2e8f0;
  z-index: 0;
}

.divider span {
  background: rgba(255, 255, 255, 0.95);
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.social-login {
  display: flex;
  gap: 12px;
  margin-bottom: 25px;
}

.social-btn {
  flex: 1;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
}

.social-btn i {
  font-size: 20px;
}

.github-btn:hover {
  border-color: #333;
  color: #333;
  transform: translateY(-2px);
}

.gitcode-btn:hover {
  border-color: #ff6b35;
  color: #ff6b35;
  transform: translateY(-2px);
}

.gitee-btn:hover {
  border-color: #c71d23;
  color: #c71d23;
  transform: translateY(-2px);
}

.register-link {
  text-align: center;
  color: #718096;
  font-size: 14px;
}

.register-btn {
  color: #545ae7;
  background: none;
  border: none;
  font-weight: 600;
  margin-left: 5px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.register-btn:hover {
  color: #4c51bf;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .modal-card {
    padding: 30px 20px;
    margin: 10px;
  }
  
  .modal-title {
    font-size: 24px;
  }
  
  .social-login {
    flex-direction: column;
  }
  
  .social-btn {
    flex-direction: row;
    justify-content: center;
  }
  
  .social-btn i {
    margin-right: 8px;
    font-size: 18px;
    display: inline-block;
    vertical-align: middle;
  }
}
</style>
