import apiClient from './index.js'

export const showcaseAPI = {
  // 获取作品列表
  getShowcases(params = {}) {
    return apiClient.get('/showcases/', { params })
  },

  // 获取前端展示的作品列表（仅精品和优秀作品）
  getFrontendShowcases(params = {}) {
    return apiClient.get('/showcases/frontend', { params })
  },

  // 根据UUID获取作品详情
  getShowcaseByUuid(uuid) {
    return apiClient.get(`/showcases/${uuid}`)
  },

  // 创建作品
  createShowcase(data) {
    return apiClient.post('/showcases/', data)
  },

  // 更新作品
  updateShowcase(uuid, data) {
    return apiClient.put(`/showcases/${uuid}`, data)
  },

  // 删除作品
  deleteShowcase(uuid) {
    return apiClient.delete(`/showcases/${uuid}`)
  },

  // 获取作品评论
  getShowcaseComments(showcaseId, params = {}) {
    return apiClient.get('/showcase-comments/', { params: { showcase_id: showcaseId, ...params } })
  },

  // 创建作品评论
  createShowcaseComment(data) {
    return apiClient.post('/showcase-comments/', data)
  },

  // 更新作品评论
  updateShowcaseComment(uuid, data) {
    return apiClient.put(`/showcase-comments/${uuid}`, data)
  },

  // 删除作品评论
  deleteShowcaseComment(uuid) {
    return apiClient.delete(`/showcase-comments/${uuid}`)
  },

  // 获取评论回复
  getCommentReplies(commentId, params = {}) {
    return apiClient.get('/showcase-comment-replies/', { params: { comment_id: commentId, ...params } })
  },

  // 创建评论回复
  createCommentReply(data) {
    return apiClient.post('/showcase-comment-replies/', data)
  },

  // 更新评论回复
  updateCommentReply(uuid, data) {
    return apiClient.put(`/showcase-comment-replies/${uuid}`, data)
  },

  // 删除评论回复
  deleteCommentReply(uuid) {
    return apiClient.delete(`/showcase-comment-replies/${uuid}`)
  },

  // 点赞相关API
  toggleShowcaseLike(data) {
    return apiClient.post('/likes/showcase/', data)
  },

  getShowcaseLikeStatus(showcaseUuid) {
    return apiClient.get(`/likes/showcase/${showcaseUuid}/status`)
  },

  toggleCommentLike(data) {
    return apiClient.post('/likes/comment/', data)
  },

  getCommentLikeStatus(commentUuid) {
    return apiClient.get(`/likes/comment/${commentUuid}/status`)
  },

  toggleReplyLike(data) {
    return apiClient.post('/likes/reply/', data)
  },

  getReplyLikeStatus(replyUuid) {
    return apiClient.get(`/likes/reply/${replyUuid}/status`)
  }
}