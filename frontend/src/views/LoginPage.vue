<template>
  <div class="login-page">
    <div class="login-container" :class="{ 'fade-in': isVisible }">
      <div class="login-card">
        <div class="login-header">
          <div class="logo-section">
            <div class="logo-icon"></div>
            <h1 class="login-title webfont">欢迎回来</h1>
            <p class="login-subtitle">登录您的账户，继续学习之旅</p>
          </div>
        </div>
        
        <div class="login-form">
          <form @submit.prevent="handleLogin">
            <div class="form-group">
              <label for="email" class="form-label">邮箱地址</label>
              <div class="input-wrapper">
                <span class="input-icon">
                  <i class="iconfont icon-email"></i>
                </span>
                <input
                  id="email"
                  v-model="loginForm.email"
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
          
          <div class="divider">
            <span>或者使用以下方式登录</span>
          </div>
          
          <div class="social-login">
            <button class="social-btn github-btn" @click="handleSocialLogin('github')">
              <i class="iconfont icon-github"></i>
              <span>GitHub</span>
            </button>
            <button class="social-btn gitcode-btn" @click="handleSocialLogin('gitcode')">
              <i class="iconfont icon-gitcode"></i>
              <span>GitCode</span>
            </button>
            <button class="social-btn gitee-btn" @click="handleSocialLogin('gitee')">
              <i class="iconfont icon-gitee"></i>
              <span>Gitee</span>
            </button>
          </div>
          
          <div class="register-link">
            <span>还没有账户？</span>
            <router-link to="/register" class="register-btn">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
      <div class="bg-circle circle-3"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const loginForm = reactive({
  email: '',
  password: '',
  remember: false
})

const showPassword = ref(false)
const isLoading = ref(false)
const isVisible = ref(false)

// 页面加载动画
onMounted(() => {
  // 减少延迟，让动画更快开始
  setTimeout(() => {
    isVisible.value = true
  }, 50)
})

const handleLogin = async () => {
  isLoading.value = true
  
  try {
    // 这里添加实际的登录逻辑
    console.log('登录信息:', loginForm)
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 登录成功后跳转到首页
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    isLoading.value = false
  }
}

const handleSocialLogin = (provider) => {
  console.log(`使用 ${provider} 登录`)
  // 这里添加第三方登录逻辑
  switch (provider) {
    case 'github':
      // GitHub OAuth 登录
      window.location.href = '/auth/github'
      break
    case 'gitcode':
      // GitCode OAuth 登录
      window.location.href = '/auth/gitcode'
      break
    case 'gitee':
      // Gitee OAuth 登录
      window.location.href = '/auth/gitee'
      break
  }
}
</script>

<style scoped>
.login-page {
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

.login-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, transparent 0%, transparent 30%, rgba(0, 0, 0, 0.02) 60%, rgba(0, 0, 0, 0.05) 100%);
  pointer-events: none;
}

.login-container {
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 2;
  opacity: 0;
  transform: translateY(20px) scale(0.98);
  transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.login-container.fade-in {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.login-card {
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

.login-header {
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

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 8px;
}

.login-subtitle {
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
  text-decoration: none;
  font-weight: 600;
  margin-left: 5px;
  transition: color 0.3s ease;
}

.register-btn:hover {
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
  animation: float 6s ease-in-out infinite;
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
  top: 50%;
  right: -75px;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
    margin: 10px;
  }
  
  .login-title {
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
