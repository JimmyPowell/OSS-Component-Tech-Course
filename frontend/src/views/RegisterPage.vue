<template>
  <div class="register-page">
    <div class="register-container" :class="{ 'fade-in': isVisible }">
      <div class="register-card">
        <div class="register-header">
          <div class="logo-section">
            <div class="logo-icon"></div>
            <h1 class="register-title webfont">加入我们</h1>
            <p class="register-subtitle">创建您的账户，开启学习之旅</p>
          </div>
        </div>
        
        <div class="register-form">
          <form @submit.prevent="handleRegister">
            <div class="form-row">
              <div class="form-group half">
                <label for="firstName" class="form-label">姓</label>
                <div class="input-wrapper">
                  <span class="input-icon">
                    <i class="iconfont icon-user"></i>
                  </span>
                  <input
                    id="firstName"
                    v-model="registerForm.firstName"
                    type="text"
                    class="form-input"
                    placeholder="请输入您的姓"
                    required
                  />
                </div>
              </div>
              
              <div class="form-group half">
                <label for="lastName" class="form-label">名</label>
                <div class="input-wrapper">
                  <span class="input-icon">
                    <i class="iconfont icon-user"></i>
                  </span>
                  <input
                    id="lastName"
                    v-model="registerForm.lastName"
                    type="text"
                    class="form-input"
                    placeholder="请输入您的名"
                    required
                  />
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label for="email" class="form-label">邮箱地址</label>
              <div class="input-wrapper">
                <span class="input-icon">
                  <i class="iconfont icon-email"></i>
                </span>
                <input
                  id="email"
                  v-model="registerForm.email"
                  type="email"
                  class="form-input"
                  placeholder="请输入您的邮箱地址"
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
                  v-model="registerForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-input"
                  placeholder="请输入密码（至少8位）"
                  required
                  minlength="8"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showPassword = !showPassword"
                >
                  <i :class="showPassword ? 'iconfont icon-eye-open' : 'iconfont icon-eye-close'"></i>
                </button>
              </div>
              <div class="password-strength">
                <div class="strength-bar">
                  <div 
                    class="strength-fill" 
                    :class="passwordStrength.class"
                    :style="{ width: passwordStrength.width }"
                  ></div>
                </div>
                <span class="strength-text" :class="passwordStrength.class">
                  {{ passwordStrength.text }}
                </span>
              </div>
            </div>
            
            <div class="form-group">
              <label for="confirmPassword" class="form-label">确认密码</label>
              <div class="input-wrapper">
                <span class="input-icon">
                  <i class="iconfont icon-lock"></i>
                </span>
                <input
                  id="confirmPassword"
                  v-model="registerForm.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="form-input"
                  placeholder="请再次输入密码"
                  required
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <i :class="showConfirmPassword ? 'iconfont icon-eye-open' : 'iconfont icon-eye-close'"></i>
                </button>
              </div>
              <div v-if="registerForm.confirmPassword && !passwordsMatch" class="error-message">
                密码不匹配
              </div>
            </div>
            
            <div class="form-group">
              <label class="agreement-label">
                <input v-model="registerForm.agreeTerms" type="checkbox" required />
                <span class="checkmark"></span>
                我已阅读并同意
                <a href="#" class="link">《用户协议》</a>
                和
                <a href="#" class="link">《隐私政策》</a>
              </label>
            </div>
            
            <button type="submit" class="btn-register" :disabled="!canSubmit || isLoading">
              <span v-if="isLoading" class="loading-spinner"></span>
              {{ isLoading ? '注册中...' : '创建账户' }}
            </button>
          </form>
          
          <div class="divider">
            <span>或者使用以下方式注册</span>
          </div>
          
          <div class="social-login">
            <button class="social-btn github-btn" @click="handleSocialRegister('github')">
              <i class="iconfont icon-github"></i>
              <span>GitHub</span>
            </button>
            <button class="social-btn gitcode-btn" @click="handleSocialRegister('gitcode')">
              <i class="iconfont icon-gitcode"></i>
              <span>GitCode</span>
            </button>
            <button class="social-btn gitee-btn" @click="handleSocialRegister('gitee')">
              <i class="iconfont icon-gitee"></i>
              <span>Gitee</span>
            </button>
          </div>
          
          <div class="login-link">
            <span>已有账户？</span>
            <router-link to="/login" class="login-btn">立即登录</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
      <div class="bg-circle circle-3"></div>
      <div class="bg-circle circle-4"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const registerForm = reactive({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isLoading = ref(false)
const isVisible = ref(false)

// 页面加载动画
onMounted(() => {
  // 减少延迟，让动画更快开始
  setTimeout(() => {
    isVisible.value = true
  }, 50)
})

// 密码强度计算
const passwordStrength = computed(() => {
  const password = registerForm.password
  if (!password) return { width: '0%', class: '', text: '' }
  
  let score = 0
  if (password.length >= 8) score += 1
  if (/[a-z]/.test(password)) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[0-9]/.test(password)) score += 1
  if (/[^A-Za-z0-9]/.test(password)) score += 1
  
  if (score <= 2) {
    return { width: '33%', class: 'weak', text: '弱' }
  } else if (score <= 3) {
    return { width: '66%', class: 'medium', text: '中等' }
  } else {
    return { width: '100%', class: 'strong', text: '强' }
  }
})

// 密码匹配检查
const passwordsMatch = computed(() => {
  return registerForm.password === registerForm.confirmPassword
})

// 表单提交条件检查
const canSubmit = computed(() => {
  return registerForm.firstName &&
         registerForm.lastName &&
         registerForm.email &&
         registerForm.password &&
         registerForm.confirmPassword &&
         passwordsMatch.value &&
         registerForm.agreeTerms
})

const handleRegister = async () => {
  if (!canSubmit.value) return
  
  isLoading.value = true
  
  try {
    // 这里添加实际的注册逻辑
    console.log('注册信息:', registerForm)
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 注册成功后跳转到登录页面或首页
    router.push('/login')
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    isLoading.value = false
  }
}

const handleSocialRegister = (provider) => {
  console.log(`使用 ${provider} 注册`)
  // 这里添加第三方注册逻辑
  switch (provider) {
    case 'github':
      window.location.href = '/auth/github?action=register'
      break
    case 'gitcode':
      window.location.href = '/auth/gitcode?action=register'
      break
    case 'gitee':
      window.location.href = '/auth/gitee?action=register'
      break
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: 
    radial-gradient(circle at center, rgba(135, 206, 235, 0.05) 0%, rgba(173, 216, 230, 0.08) 40%, rgba(176, 196, 222, 0.12) 100%),
    linear-gradient(135deg, #f8fafc 0%, #e8f4f8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.register-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, transparent 0%, transparent 30%, rgba(0, 0, 0, 0.02) 60%, rgba(0, 0, 0, 0.05) 100%);
  pointer-events: none;
}

.register-container {
  width: 100%;
  max-width: 500px;
  position: relative;
  z-index: 2;
  opacity: 0;
  transform: translateY(20px) scale(0.98);
  transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.register-container.fade-in {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.register-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 
    0 0 0 1px rgba(255, 255, 255, 0.2),
    0 20px 40px rgba(0, 0, 0, 0.08),
    0 0 60px rgba(135, 206, 235, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.4);
  position: relative;
  z-index: 10;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #545ae7, #6b66e9);
  border-radius: 15px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.logo-icon::before {
  content: '';
  width: 30px;
  height: 30px;
  background: white;
  border-radius: 8px;
  opacity: 0.9;
}

.register-title {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 8px;
}

.register-subtitle {
  color: #718096;
  font-size: 16px;
  margin: 0;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group.half {
  flex: 1;
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

.password-strength {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.strength-fill.weak {
  background: #f56565;
}

.strength-fill.medium {
  background: #ed8936;
}

.strength-fill.strong {
  background: #48bb78;
}

.strength-text {
  font-size: 12px;
  font-weight: 500;
  min-width: 30px;
}

.strength-text.weak {
  color: #f56565;
}

.strength-text.medium {
  color: #ed8936;
}

.strength-text.strong {
  color: #48bb78;
}

.error-message {
  color: #f56565;
  font-size: 12px;
  margin-top: 5px;
}

.agreement-label {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  font-size: 14px;
  color: #4a5568;
  line-height: 1.5;
}

.agreement-label input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  margin-right: 8px;
  margin-top: 2px;
  position: relative;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.agreement-label input:checked + .checkmark {
  background: #545ae7;
  border-color: #545ae7;
}

.agreement-label input:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  color: white;
  font-size: 12px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.link {
  color: #545ae7;
  text-decoration: none;
  transition: color 0.3s ease;
}

.link:hover {
  color: #4c51bf;
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

.login-link {
  text-align: center;
  color: #718096;
  font-size: 14px;
}

.login-btn {
  color: #545ae7;
  text-decoration: none;
  font-weight: 600;
  margin-left: 5px;
  transition: color 0.3s ease;
}

.login-btn:hover {
  color: #4c51bf;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 1;
  filter: blur(1px);
  opacity: 0.6;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(135, 206, 235, 0.1);
  animation: float 8s ease-in-out infinite;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -150px;
  right: -150px;
  animation-delay: 2s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 30%;
  right: -75px;
  animation-delay: 4s;
}

.circle-4 {
  width: 100px;
  height: 100px;
  top: 20%;
  left: -50px;
  animation-delay: 6s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(180deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-group.half {
    flex: none;
  }
}

@media (max-width: 480px) {
  .register-card {
    padding: 30px 20px;
    margin: 10px;
  }
  
  .register-title {
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
    margin-bottom: 0;
  }
}
</style>
