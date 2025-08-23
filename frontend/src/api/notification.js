import axios from './index'

export const notificationApi = {
  // 获取通知列表
  getNotifications: (params = {}) => {
    return axios.get('/notifications', { params })
  },

  // 获取未读通知数量
  getUnreadCount: () => {
    return axios.get('/notifications/unread-count')
  },

  // 获取通知详情
  getNotificationDetail: (uuid) => {
    return axios.get(`/notifications/${uuid}`)
  },

  // 标记通知为已读
  markAsRead: (uuid) => {
    return axios.put(`/notifications/${uuid}/read`)
  },

  // 标记所有通知为已读
  markAllAsRead: () => {
    return axios.put('/notifications/mark-all-read')
  },

  // 删除通知
  deleteNotification: (uuid) => {
    return axios.delete(`/notifications/${uuid}`)
  }
}

export default notificationApi