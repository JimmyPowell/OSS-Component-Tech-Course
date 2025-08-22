import apiClient from './index'

// 论坛分类相关API
export const forumCategoryApi = {
  // 获取所有活跃分类
  getActiveCategories: () => apiClient.get('/forum/categories/active'),

  // 获取分类列表（分页）
  getCategories: (params = {}) => {
    const { skip = 0, limit = 20, name, is_active } = params
    return apiClient.get('/forum/categories/', {
      params: { skip, limit, name, is_active }
    })
  }
}

// 论坛帖子相关API
export const forumPostApi = {
  // 获取热门帖子
  getHotPosts: (params = {}) => {
    const { limit = 10, days = 7 } = params
    return apiClient.get('/forum/posts/hot', {
      params: { limit, days }
    })
  },

  // 获取帖子列表（分页）
  getPosts: (params = {}) => {
    const { skip = 0, limit = 20, category_id, title, start_time, end_time } = params
    return apiClient.get('/forum/posts/', {
      params: { skip, limit, category_id, title, start_time, end_time }
    })
  },

  // 获取帖子详情
  getPost: (uuid) => apiClient.get(`/forum/posts/${uuid}`),

  // 创建帖子
  createPost: (data) => apiClient.post('/forum/posts/', data),

  // 更新帖子
  updatePost: (uuid, data) => apiClient.put(`/forum/posts/${uuid}`, data),

  // 删除帖子
  deletePost: (uuid) => apiClient.delete(`/forum/posts/${uuid}`)
}

// 论坛回复相关API
export const forumReplyApi = {
  // 获取帖子的回复列表
  getRepliesByPost: (postUuid, params = {}) => {
    const { skip = 0, limit = 20, parent_id } = params
    return apiClient.get(`/forum/replies/post/${postUuid}`, {
      params: { skip, limit, parent_id }
    })
  },

  // 获取帖子的回复树结构
  getRepliesTree: (postUuid) => apiClient.get(`/forum/replies/post/${postUuid}/tree`),

  // 获取回复详情
  getReply: (uuid) => apiClient.get(`/forum/replies/${uuid}`),

  // 创建回复
  createReply: (data) => apiClient.post('/forum/replies/', data),

  // 更新回复
  updateReply: (uuid, data) => apiClient.put(`/forum/replies/${uuid}`, data),

  // 删除回复
  deleteReply: (uuid) => apiClient.delete(`/forum/replies/${uuid}`)
}

// 统一导出
export const forumApi = {
  category: forumCategoryApi,
  post: forumPostApi,
  reply: forumReplyApi
}

export default forumApi