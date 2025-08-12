<template>
  <Teleport to="body">
    <Notification ref="successNotification" message="注册成功！" type="success" />
    <Notification ref="verifySuccessNotification" message="验证码验证成功！" type="success" />
    <Notification ref="errorNotification" :message="errorMessage" type="error" />
    <div 
      v-if="isVisible" 
      class="modal-overlay" 
      :class="{ 'fade-in': showModal }"
      @click="handleOverlayClick"
    >
      <div class="modal-container" :class="{ 'slide-in': showModal }">
        <div class="modal-card">
          <button class="close-btn" @click="closeModal">
            <i class="iconfont icon-close"></i>
          </button>
          
          <div class="modal-header">
            <div class="logo-section">
              <div class="navbar-logo-modal"></div>
              <h1 class="modal-title webfont">加入我们</h1>
              <p class="modal-subtitle">{{ subtitle }}</p>
            </div>
          </div>
          
          <div class="modal-form">
            <!-- Step 1: Email Input -->
            <form v-if="step === 1" @submit.prevent="handleSendCode">
              <div class="form-group">
                <label for="email" class="form-label">邮箱地址</label>
                <div class="input-wrapper">
                  <span class="input-icon"><i class="iconfont icon-email"></i></span>
                  <input id="email" v-model="form.email" type="email" class="form-input" placeholder="请输入您的邮箱地址" required />
                </div>
              </div>
              <button type="submit" class="btn-register" :disabled="isLoading">
                <span v-if="isLoading" class="loading-spinner"></span>
                {{ isLoading ? '发送中...' : '发送验证码' }}
              </button>
            </form>

            <!-- Step 2: Verification Code -->
            <form v-if="step === 2" @submit.prevent="handleVerifyCode">
              <div class="form-group">
                <label for="code" class="form-label">验证码</label>
                <div class="input-wrapper">
                  <span class="input-icon"><i class="iconfont icon-lock"></i></span>
                  <input id="code" v-model="form.code" type="text" class="form-input" placeholder="请输入6位验证码" required maxlength="6" />
                </div>
              </div>
              <div class="form-actions">
                <button type="button" class="btn-secondary" @click="step = 1">上一步</button>
                <button type="submit" class="btn-primary" :disabled="isLoading">
                  <span v-if="isLoading" class="loading-spinner"></span>
                  {{ isLoading ? '验证中...' : '验证' }}
                </button>
              </div>
            </form>

            <!-- Step 3: User Info -->
            <form v-if="step === 3" @submit.prevent="handleFinalRegister" class="form-grid">
              <div class="form-group">
                <label for="username" class="form-label">用户名</label>
                <input id="username" v-model="form.username" type="text" class="form-input" placeholder="请输入用户名" required />
              </div>
              <div class="form-group">
                <label for="real_name" class="form-label">真实姓名</label>
                <input id="real_name" v-model="form.real_name" type="text" class="form-input" placeholder="请输入真实姓名" required />
              </div>
              <div class="form-group">
                <label for="password" class="form-label">密码</label>
                <input id="password" v-model="form.password" type="password" class="form-input" placeholder="请输入密码" required />
              </div>
              <div class="form-group">
                <label for="confirm_password" class="form-label">确认密码</label>
                <input id="confirm_password" v-model="form.confirm_password" type="password" class="form-input" placeholder="请再次输入密码" required />
              </div>
              <div class="form-group">
                <label for="phone_number" class="form-label">手机号</label>
                <input id="phone_number" v-model="form.phone_number" type="text" class="form-input" placeholder="请输入手机号" required />
              </div>
              <div class="form-group form-group-full">
                <label for="school" class="form-label">学校</label>
                <input id="school" v-model="form.school" type="text" class="form-input" placeholder="请输入学校" required />
              </div>
              <div class="form-actions form-group-full">
                <button type="button" class="btn-secondary" @click="step = 2">上一步</button>
                <button type="submit" class="btn-primary" :disabled="isLoading">
                  <span v-if="isLoading" class="loading-spinner"></span>
                  {{ isLoading ? '注册中...' : '创建账户' }}
                </button>
              </div>
            </form>
            
            <!-- 使用弹窗通知代替内联错误消息 -->

            <div class="login-link">
              <span>已有账户？</span>
              <button @click="switchToLogin" class="login-btn">立即登录</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import apiClient from '@/api/index.js'
import Notification from './Notification.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'switch-to-login'])
const authStore = useAuthStore()

const step = ref(1)
const isLoading = ref(false)
const errorMessage = ref('')
const isVisible = ref(false)
const showModal = ref(false)
const successNotification = ref(null)
const verifySuccessNotification = ref(null)
const errorNotification = ref(null)

const form = reactive({
  email: '',
  code: '',
  username: '',
  password: '',
  confirm_password: '',
  real_name: '',
  phone_number: '',
  school: ''
})

const subtitle = computed(() => {
  switch (step.value) {
    case 1: return '第一步：输入您的邮箱地址'
    case 2: return '第二步：输入收到的验证码'
    case 3: return '第三步：完善您的个人信息'
    default: return '创建您的账户，开启学习之旅'
  }
})

const resetForm = () => {
  step.value = 1
  errorMessage.value = ''
  Object.keys(form).forEach(key => form[key] = '')
}

const openModal = () => {
  resetForm()
  isVisible.value = true
  document.body.style.overflow = 'hidden'
  setTimeout(() => {
    showModal.value = true
  }, 10)
}

const closeModal = () => {
  showModal.value = false
  document.body.style.overflow = ''
  setTimeout(() => {
    isVisible.value = false
    emit('update:modelValue', false)
  }, 300)
}

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    openModal()
  } else {
    closeModal()
  }
}, { immediate: true })

const handleSendCode = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    await apiClient.post('/auth/request-code', { email: form.email })
    step.value = 2
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '发送验证码失败，请重试。'
    errorNotification.value.show()
  } finally {
    isLoading.value = false
  }
}

const handleVerifyCode = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await apiClient.post('/auth/verify-code', { email: form.email, code: form.code })
    authStore.setSessionToken(response.data.data.session)
    verifySuccessNotification.value.show()
    // 短暂延迟后进入下一步，让用户看到成功通知
    setTimeout(() => {
      step.value = 3
    }, 800)
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '验证码无效或已过期。'
    errorNotification.value.show()
  } finally {
    isLoading.value = false
  }
}

const handleFinalRegister = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  // 验证密码是否匹配
  if (form.password !== form.confirm_password) {
    errorMessage.value = '两次输入的密码不匹配'
    errorNotification.value.show()
    isLoading.value = false
    return
  }
  
  try {
    const payload = {
      session: authStore.sessionToken,
      username: form.username,
      password: form.password,
      real_name: form.real_name,
      phone_number: form.phone_number,
      school: form.school
    }
    await apiClient.post('/auth/register', payload)
    successNotification.value.show()
    closeModal()
    switchToLogin()
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '注册失败，请检查您的信息。'
    errorNotification.value.show()
  } finally {
    isLoading.value = false
  }
}

const handleOverlayClick = (e) => {
  if (e.target === e.currentTarget) {
    closeModal()
  }
}

const switchToLogin = () => {
  emit('switch-to-login')
}
</script>

<style scoped>
/* Styles from original component, with additions for multi-step form */
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

.btn-register {
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

.btn-register:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(84, 90, 231, 0.3);
}

.btn-register:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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

.form-actions {
  display: flex;
  gap: 10px;
}

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

.error-message {
  color: #f56565;
  font-size: 14px;
  margin-top: 15px;
  text-align: center;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
  vertical-align: middle;
  margin-right: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.login-link {
  text-align: center;
  color: #718096;
  font-size: 14px;
  margin-top: 20px;
}

.login-btn {
  color: #545ae7;
  background: none;
  border: none;
  font-weight: 600;
  margin-left: 5px;
  cursor: pointer;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group-full {
  grid-column: 1 / span 2;
}

.btn-primary {
  flex: 1;
  padding: 15px;
  background: linear-gradient(135deg, #545ae7, #6b66e9);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(84, 90, 231, 0.3);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
