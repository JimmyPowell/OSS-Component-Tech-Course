import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api'

// JWT解析函数
function parseJwt(token) {
  try {
    // 获取JWT的payload部分（第二部分）并解码
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    
    return JSON.parse(jsonPayload)
  } catch (e) {
    console.error('JWT解析错误:', e)
    return {}
  }
}

export const useAuthStore = defineStore('auth', () => {
  // 状态定义
  const sessionToken = ref(localStorage.getItem('sessionToken') || null)
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const refreshToken = ref(localStorage.getItem('refreshToken') || null)
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  
  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value)
  const userRole = computed(() => user.value?.role || 'user')
  const isManager = computed(() => userRole.value === 'manager' || userRole.value === 'admin')
  const isAdmin = computed(() => userRole.value === 'admin')
  
  // 会话令牌管理（用于注册流程）
  function setSessionToken(token) {
    sessionToken.value = token
    localStorage.setItem('sessionToken', token)
  }
  
  function clearSessionToken() {
    sessionToken.value = null
    localStorage.removeItem('sessionToken')
  }
  
  // 登录相关方法
  async function login(identifier, password) {
    try {
      const response = await apiClient.post('/auth/login', { identifier, password })
      const { access_token, refresh_token } = response.data.data
      
      setTokens(access_token, refresh_token)
      
      // 暂时不获取用户信息，直接使用基本信息
      console.log('登录成功，已保存Token：', { access: access_token.substring(0, 15) + '...', refresh: refresh_token.substring(0, 15) + '...' })
      
      // 解析JWT token获取用户角色
      const tokenPayload = parseJwt(access_token)
      console.log('解析的token负载:', tokenPayload)
      console.log('用户角色:', tokenPayload.role || 'user')
      console.log('用户ID:', tokenPayload.sub)
      
      // 设置基本用户信息（从解析的token中获取role）
      const basicUser = {
        username: identifier,
        email: identifier.includes('@') ? identifier : null,
        isLoggedIn: true,
        role: tokenPayload.role || 'user', // 从JWT中获取角色
        id: tokenPayload.sub // 保存用户ID
      }
      user.value = basicUser
      localStorage.setItem('user', JSON.stringify(basicUser))
      console.log('已设置基本用户信息：', basicUser)
      console.log('用户角色类型:', typeof tokenPayload.role, '值:', tokenPayload.role)
      console.log('当前用户是否为管理员:', tokenPayload.role === 'manager' || tokenPayload.role === 'admin')
      console.log('计算属性isManager值:', tokenPayload.role === 'manager' || tokenPayload.role === 'admin')
      
      return { success: true }
    } catch (error) {
      console.error('登录失败：', error)
      
      // 更详细地提取错误信息
      let errorMessage = '登录失败，请检查您的凭据。'
      
      // 尝试从不同的错误响应结构中获取消息
      if (error.response) {
        const { data } = error.response
        if (typeof data === 'string') {
          // 如果响应是字符串
          errorMessage = data
        } else if (data) {
          // 尝试从不同的属性中获取消息
          errorMessage = data.message || data.msg || data.error || 
                        (data.data && data.data.message) || errorMessage
        }
        
        // 特定的HTTP状态码处理
        if (error.response.status === 401) {
          errorMessage = errorMessage || '用户名或密码错误'
        } else if (error.response.status === 429) {
          errorMessage = '登录尝试次数过多，请稍后再试'
        }
      } else if (error.message) {
        // 网络错误或其他JS错误
        errorMessage = error.message.includes('Network') ? 
                     '网络连接错误，请检查您的互联网连接' : error.message
      }
      
      return { 
        success: false, 
        message: errorMessage,
        originalError: error
      }
    }
  }
  
  // 设置令牌
  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    
    // 设置 API 客户端默认授权头
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`
  }
  
  // 获取用户信息
  async function fetchUserInfo() {
    try {
      const response = await apiClient.get('/users/me')
      user.value = response.data.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return user.value
    } catch (error) {
      console.error('获取用户信息失败', error)
      return null
    }
  }
  
  // 刷新令牌
  async function refreshAccessToken() {
    if (!refreshToken.value) {
      return { success: false, message: '没有可用的刷新令牌' }
    }
    
    try {
      const response = await apiClient.post('/auth/refresh-token', {
        refresh_token: refreshToken.value
      })
      
      const { access_token, refresh_token } = response.data.data
      
      // 更新令牌
      setTokens(access_token, refresh_token || refreshToken.value)
      return { success: true }
    } catch (error) {
      // 刷新失败，清除用户会话
      logout()
      return { 
        success: false, 
        message: '会话已过期，请重新登录' 
      }
    }
  }
  
  // 登出
  async function logout() {
    // 尝试调用登出API
    if (refreshToken.value) {
      try {
        await apiClient.post('/auth/logout', {
          refresh_token: refreshToken.value
        })
      } catch (error) {
        console.error('登出API调用失败', error)
      }
    }
    
    // 清除状态和本地存储
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    
    // 清除API客户端头部
    delete apiClient.defaults.headers.common['Authorization']
  }
  
  return { 
    // 状态
    sessionToken, 
    accessToken, 
    refreshToken, 
    user,
    
    // 计算属性
    isAuthenticated,
    userRole,
    isManager,
    isAdmin,
    
    // 方法
    setSessionToken,
    clearSessionToken,
    login,
    logout,
    setTokens,
    fetchUserInfo,
    refreshAccessToken
  }
})
