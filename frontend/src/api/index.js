import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 存储等待执行的请求队列
const pendingRequests = [];

// 标记是否正在刷新token
let isRefreshing = false;

// 标记token最后刷新时间，用于优化刷新策略
let lastTokenRefresh = 0;

// token刷新冷却时间（毫秒），避免频繁刷新
const TOKEN_REFRESH_COOLDOWN = 10000; // 10秒

// 恢复请求队列中的所有请求
const processQueue = (error = null) => {
  pendingRequests.forEach(({ resolve, reject, config }) => {
    if (error) {
      reject(error);
    } else {
      // 使用新的访问令牌重试原始请求
      const token = localStorage.getItem('accessToken');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      resolve(config);
    }
  });

  // 清空队列
  pendingRequests.length = 0;
};

// 检查令牌是否已过期（基于JWT payload中的exp声明）
const isTokenExpired = (token) => {
  if (!token) return true;
  
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64).split('').map(c => 
        '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      ).join('')
    );
    const payload = JSON.parse(jsonPayload);
    const expiry = payload.exp * 1000; // 转换为毫秒
    return Date.now() >= expiry;
  } catch (e) {
    console.error('Token解析失败', e);
    return true;
  }
};

// 从本地存储获取token并设置请求头
const accessToken = localStorage.getItem('accessToken');
if (accessToken) {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
}

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 此处可以添加全局请求处理逻辑
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 请求拦截器增强，在发送请求前检查token是否即将到期
apiClient.interceptors.request.use(
  async (config) => {
    // 如果是刷新token的请求，跳过预处理
    if (config.url?.includes('/auth/refresh-token')) {
      return config;
    }
    
    const token = localStorage.getItem('accessToken');
    
    // 如果有token且即将过期，尝试预先刷新
    if (token && isTokenExpired(token)) {
      // 确保我们不会太频繁地刷新
      const now = Date.now();
      if (now - lastTokenRefresh > TOKEN_REFRESH_COOLDOWN && !isRefreshing) {
        try {
          isRefreshing = true;
          // 动态导入store模块避免循环依赖
          const { useAuthStore } = await import('../stores/auth');
          const authStore = useAuthStore();
          const refreshResult = await authStore.refreshAccessToken();
          
          if (refreshResult.success) {
            lastTokenRefresh = now;
            const newToken = localStorage.getItem('accessToken');
            if (newToken) {
              config.headers['Authorization'] = `Bearer ${newToken}`;
            }
          }
        } catch (error) {
          console.error('预刷新token失败:', error);
        } finally {
          isRefreshing = false;
        }
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // 处理401未授权错误 (令牌失效或过期)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // 检查刷新冷却时间
      const now = Date.now();
      if (now - lastTokenRefresh < TOKEN_REFRESH_COOLDOWN) {
        // 如果最近才刷新过，可能是token已完全失效，需要重新登录
        // 清除用户信息
        const { useAuthStore } = await import('../stores/auth');
        const authStore = useAuthStore();
        await authStore.logout();
        
        // 重定向到登录页
        if (window.location.pathname !== '/login') {
          window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        }
        return Promise.reject(new Error('会话已过期，请重新登录'));
      }
      
      // 如果正在刷新token，将请求添加到队列
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingRequests.push({ resolve, reject, config: originalRequest });
        })
          .then((config) => {
            // 刷新token成功后，重试请求
            return apiClient(config);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }
      
      // 标记正在刷新token
      isRefreshing = true;
      lastTokenRefresh = now;
      
      try {
        // 动态导入store模块，避免循环依赖
        const { useAuthStore } = await import('../stores/auth');
        const authStore = useAuthStore();
        
        // 尝试刷新token
        const refreshResult = await authStore.refreshAccessToken();
        
        if (refreshResult.success) {
          // 刷新成功，处理队列中的请求
          processQueue();
          // 更新原始请求的授权头
          const newToken = localStorage.getItem('accessToken');
          if (newToken) {
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          }
          return apiClient(originalRequest); // 重试原始请求
        } else {
          // 刷新失败，清除用户状态并重定向到登录页
          await authStore.logout();
          processQueue(new Error('会话已过期，请重新登录'));
          
          if (window.location.pathname !== '/login') {
            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
          }
          return Promise.reject(error);
        }
      } catch (refreshError) {
        // 刷新过程中出现异常，拒绝所有队列中的请求
        processQueue(refreshError);
        return Promise.reject(refreshError);
      } finally {
        // 无论成功失败，重置刷新状态
        isRefreshing = false;
      }
    }
    
    // 其他错误直接拒绝
    return Promise.reject(error);
  }
);

export default apiClient;
