import apiClient from './index.js'

export const blogApi = {
  // 获取博客列表
  getBlogs(params = {}) {
    return apiClient.get('/blogs/', { params })
  },

  // 根据UUID获取博客详情
  getBlogByUuid(uuid) {
    return apiClient.get(`/blogs/${uuid}`)
  },

  // 搜索博客
  searchBlogs(params = {}) {
    return apiClient.get('/blogs/search', { params })
  },

  // 获取博客标签
  getTags(params = {}) {
    return apiClient.get('/blogs/tags', { params })
  },

  // 获取热门标签
  getPopularTags(params = {}) {
    return apiClient.get('/blogs/tags/popular', { params })
  },

  // 根据作者获取博客
  getBlogsByAuthor(authorId, params = {}) {
    return apiClient.get(`/blogs/author/${authorId}`, { params })
  },

  // 增加博客浏览次数
  incrementViewCount(uuid, increment = 1) {
    return apiClient.put(`/blogs/${uuid}/view`, { increment })
  }
}

// 博客工具函数
export const blogUtils = {
  // 获取最新博客
  async getLatestBlogs(limit = 10) {
    return blogApi.getBlogs({ limit, skip: 0 })
  },

  // 格式化博客时间
  formatBlogTime(dateString) {
    if (!dateString) return ''
    const date = new Date(dateString)
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (days === 0) {
      const hours = Math.floor(diff / (1000 * 60 * 60))
      if (hours === 0) {
        const minutes = Math.floor(diff / (1000 * 60))
        return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
      }
      return `${hours}小时前`
    } else if (days < 7) {
      return `${days}天前`
    } else {
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }
  },

  // 截取摘要文本
  truncateText(text, maxLength = 120) {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }
}