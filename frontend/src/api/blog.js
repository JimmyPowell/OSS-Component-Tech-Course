import api from './index'

// Blog标签相关API
export const blogTagApi = {
  // 获取所有标签
  getAllTags(params = {}) {
    return api.get('/blogs/tags', { params })
  },

  // 获取热门标签
  getPopularTags(limit = 10) {
    return api.get('/blogs/tags/popular', { params: { limit } })
  },

  // 创建标签（管理员权限）
  createTag(tagData) {
    return api.post('/blogs/tags', tagData)
  }
}

// Blog文章相关API
export const blogApi = {
  // 获取Blog列表（仅已发布）
  getBlogs(params = {}) {
    const { skip = 0, limit = 10 } = params
    return api.get('/blogs/', { params: { skip, limit } })
  },

  // 搜索Blog文章
  searchBlogs(searchParams = {}) {
    const {
      keyword,
      tag_ids = [],
      author_id,
      status = 'published',
      page = 1,
      size = 10
    } = searchParams
    
    const params = { page, size, status }
    if (keyword) params.keyword = keyword
    if (tag_ids.length > 0) params.tag_ids = tag_ids
    if (author_id) params.author_id = author_id
    
    return api.get('/blogs/search', { params })
  },

  // 根据UUID获取Blog详情
  getBlogDetail(blogUuid) {
    return api.get(`/blogs/${blogUuid}`)
  },

  // 获取指定作者的Blog列表
  getBlogsByAuthor(authorId, params = {}) {
    const { skip = 0, limit = 10 } = params
    return api.get(`/blogs/author/${authorId}`, { params: { skip, limit } })
  },

  // 增加Blog浏览次数
  incrementViewCount(blogUuid, increment = 1) {
    return api.put(`/blogs/${blogUuid}/view`, { increment })
  },

  // 创建Blog文章（管理员权限）
  createBlog(blogData) {
    return api.post('/blogs/', blogData)
  },

  // 更新Blog文章（管理员权限或作者本人）
  updateBlog(blogUuid, blogData) {
    return api.put(`/blogs/${blogUuid}`, blogData)
  },

  // 删除Blog文章（管理员权限或作者本人）
  deleteBlog(blogUuid) {
    return api.delete(`/blogs/${blogUuid}`)
  }
}

// 便捷方法
export const blogUtils = {
  // 获取最新的几篇Blog（用于主页显示）
  getLatestBlogs(limit = 3) {
    return blogApi.getBlogs({ skip: 0, limit })
  },

  // 根据标签搜索Blog
  getBlogsByTags(tagIds, limit = 10) {
    return blogApi.searchBlogs({ tag_ids: tagIds, size: limit })
  },

  // 根据关键词搜索Blog
  searchBlogsByKeyword(keyword, limit = 10) {
    return blogApi.searchBlogs({ keyword, size: limit })
  }
}

export default {
  ...blogApi,
  tags: blogTagApi,
  utils: blogUtils
}