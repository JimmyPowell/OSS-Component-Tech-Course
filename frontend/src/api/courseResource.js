import apiClient from './index.js';

/**
 * 课程资源API服务
 */

// 获取课程资源列表（支持分页和筛选）
export const getCourseResources = async (params = {}) => {
  try {
    const {
      skip = 0,
      limit = 10,
      name = null,
      resource_type = null,
      start_time = null,
      end_time = null
    } = params;
    
    const queryParams = new URLSearchParams();
    queryParams.append('skip', skip);
    queryParams.append('limit', limit);
    
    if (name) queryParams.append('name', name);
    if (resource_type) queryParams.append('resource_type', resource_type);
    if (start_time) queryParams.append('start_time', start_time);
    if (end_time) queryParams.append('end_time', end_time);
    
    const response = await apiClient.get(`/course-resources?${queryParams.toString()}`);
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
    console.error('获取课程资源列表失败:', error);
    return {
      success: false,
      message: error.message || '网络请求失败'
    };
  }
};

// 根据UUID获取单个课程资源详情
export const getCourseResourceByUuid = async (uuid) => {
  try {
    const response = await apiClient.get(`/course-resources/${uuid}`);
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
    console.error('获取课程资源详情失败:', error);
    return {
      success: false,
      message: error.message || '网络请求失败'
    };
  }
};

// 根据资源类型获取课程资源
export const getCourseResourcesByType = async (type, params = {}) => {
  try {
    const response = await getCourseResources({
      ...params,
      resource_type: type
    });
    return response;
  } catch (error) {
    console.error(`获取${type}类型资源失败:`, error);
    return {
      success: false,
      message: error.message || '网络请求失败'
    };
  }
};

// 获取课件资源（PPT等）
export const getPptResources = async (params = {}) => {
  return getCourseResourcesByType('ppt', params);
};

// 获取视频资源
export const getVideoResources = async (params = {}) => {
  return getCourseResourcesByType('video', params);
};

// 获取附件资源
export const getAttachmentResources = async (params = {}) => {
  return getCourseResourcesByType('attachment', params);
};

// 获取课程资源详情（包含发布者信息）
export const getCourseResourceDetail = async (uuid) => {
  try {
    const response = await apiClient.get(`/course-resources/${uuid}/detail`);
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
    console.error('获取课程资源详情失败:', error);
    return {
      success: false,
      message: error.message || '网络请求失败'
    };
  }
};

// 增加播放次数
export const incrementViewCount = async (uuid) => {
  try {
    const response = await apiClient.post(`/course-resources/${uuid}/increment-view`);
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
    console.error('增加播放次数失败:', error);
    return {
      success: false,
      message: error.message || '网络请求失败'
    };
  }
};

// 下载资源文件
export const downloadResource = async (uuid) => {
  try {
    const resourceDetail = await getCourseResourceDetail(uuid);
    if (resourceDetail.success && resourceDetail.data.resource_url) {
      // 创建一个临时链接进行下载
      const link = document.createElement('a');
      link.href = resourceDetail.data.resource_url;
      link.download = resourceDetail.data.name;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      return { success: true };
    } else {
      return {
        success: false,
        message: resourceDetail.message || '资源URL不存在'
      };
    }
  } catch (error) {
    console.error('下载资源失败:', error);
    return {
      success: false,
      message: error.message || '下载失败'
    };
  }
};