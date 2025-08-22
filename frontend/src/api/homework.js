import apiClient from './index.js';

/**
 * 作业API服务
 */

// 获取作业列表（支持分页和筛选）
export const getHomeworkList = async (params = {}) => {
  try {
    const {
      skip = 0,
      limit = 10,
      name = null,
      start_time = null,
      end_time = null
    } = params;
    
    const queryParams = new URLSearchParams();
    queryParams.append('skip', skip);
    queryParams.append('limit', limit);
    
    if (name) queryParams.append('name', name);
    if (start_time) queryParams.append('start_time', start_time);
    if (end_time) queryParams.append('end_time', end_time);
    
    const response = await apiClient.get(`/homeworks?${queryParams.toString()}`);
    // 后端统一响应格式: { code, message, data }
    if (response.data.code === 200) {
      return {
        success: true,
        data: response.data.data,
        message: response.data.message
      };
    } else {
      return {
        success: false,
        message: response.data.message || '请求失败'
      };
    }
  } catch (error) {
    console.error('获取作业列表失败:', error);
    return {
      success: false,
      message: error.message || '网络请求失败'
    };
  }
};

// 根据UUID获取单个作业详情（含发布者信息）
export const getHomeworkDetail = async (uuid) => {
  try {
    const response = await apiClient.get(`/homeworks/${uuid}`);
    // 后端统一响应格式: { code, message, data }
    if (response.data.code === 200) {
      return {
        success: true,
        data: response.data.data,
        message: response.data.message
      };
    } else {
      return {
        success: false,
        message: response.data.message || '请求失败'
      };
    }
  } catch (error) {
    console.error('获取作业详情失败:', error);
    return {
      success: false,
      message: error.message || '网络请求失败'
    };
  }
};

// 创建作业（管理员功能）
export const createHomework = async (homeworkData) => {
  try {
    const response = await apiClient.post('/homeworks', homeworkData);
    if (response.data.code === 200) {
      return {
        success: true,
        data: response.data.data,
        message: response.data.message
      };
    } else {
      return {
        success: false,
        message: response.data.message || '创建失败'
      };
    }
  } catch (error) {
    console.error('创建作业失败:', error);
    return {
      success: false,
      message: error.message || '网络请求失败'
    };
  }
};

// 格式化持续时间（分钟转换为可读格式）
export const formatDuration = (minutes) => {
  if (!minutes) return '无限制';
  
  if (minutes < 60) {
    return `${minutes}分钟`;
  } else {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}小时${remainingMinutes}分钟` : `${hours}小时`;
  }
};

// 格式化日期
export const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};