import axios from 'axios';
import { message } from 'ant-design-vue';
import router from '../router';

// 创建axios实例
const request = axios.create({
  timeout: 10000,
});

// 请求队列，用于存储被401的请求
let isRefreshing = false;
let failedQueue = [];

// 处理队列中的请求
const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  
  failedQueue = [];
};

// 刷新token
const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    throw new Error('No refresh token');
  }

  try {
    const response = await axios.post('http://localhost:8000/api/v1/auth/refresh', {
      refresh_token: refreshToken
    });

    if (response.data.code === 200) {
      const { access_token, refresh_token: newRefreshToken } = response.data.data;
      
      // 更新本地存储的token
      localStorage.setItem('access_token', access_token);
      
      // 如果返回了新的refresh_token，则更新它
      if (newRefreshToken) {
        localStorage.setItem('refresh_token', newRefreshToken);
      }
      
      return access_token;
    } else {
      throw new Error('Token refresh failed');
    }
  } catch (error) {
    // 刷新失败，清除本地存储并跳转到登录页
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/login');
    throw error;
  }
};

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // 如果是401错误且不是刷新token的请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 如果正在刷新token，将请求加入队列
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return request(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshToken();
        processQueue(null, newToken);
        
        // 重试原始请求
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return request(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        message.error('登录已过期，请重新登录');
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // 其他错误处理
    if (error.response?.status === 403) {
      message.error('权限不足');
    } else if (error.response?.status >= 500) {
      message.error('服务器错误，请稍后重试');
    }

    return Promise.reject(error);
  }
);

export default request;