<template>
  <div class="notification-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="page-title">
              <i class="fas fa-bell me-2"></i>
              通知中心
            </h1>
            <p class="page-subtitle text-muted mb-0">
              查看和管理您的所有通知消息
            </p>
          </div>
          <div class="header-buttons">
            <button 
              class="btn btn-outline-secondary refresh-btn"
              @click="fetchNotifications"
              :disabled="loading"
            >
              <i class="fas fa-sync-alt me-2" :class="{ 'fa-spin': loading }"></i>
              刷新
            </button>
            <button 
              class="btn btn-primary mark-read-btn"
              @click="markAllAsRead"
              :disabled="loading || !hasUnreadNotifications"
            >
              <i class="fas fa-check-double me-2"></i>
              全部已读
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和统计 -->
    <div class="container mt-5">
      <div class="row">
        <div class="col-md-8">
          <div class="filter-tabs">
            <button 
              class="filter-btn"
              :class="{ active: currentFilter === 'all' }"
              @click="setFilter('all')"
            >
              全部 ({{ totalCount }})
            </button>
            <button 
              class="filter-btn"
              :class="{ active: currentFilter === 'unread' }"
              @click="setFilter('unread')"
            >
              未读 ({{ unreadCount }})
            </button>
            <button 
              class="filter-btn"
              :class="{ active: currentFilter === 'read' }"
              @click="setFilter('read')"
            >
              已读 ({{ readCount }})
            </button>
          </div>
        </div>
        <div class="col-md-4 text-end">
          <div class="notification-stats text-muted">
            <small>共 {{ totalCount }} 条通知</small>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知列表 -->
    <div class="container mt-4">
      <div class="notification-list">
        <!-- 加载状态 -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
          <p class="mt-2 text-muted">加载通知中...</p>
        </div>

        <!-- 空状态 -->
        <div v-else-if="filteredNotifications.length === 0" class="empty-state text-center py-5">
          <i class="fas fa-bell-slash fa-3x text-muted mb-3"></i>
          <h3 class="text-muted">{{ getEmptyMessage() }}</h3>
          <p class="text-muted">{{ getEmptyDescription() }}</p>
        </div>

        <!-- 通知项 -->
        <div v-else class="notification-items">
          <div 
            v-for="notification in filteredNotifications" 
            :key="notification.uuid"
            class="notification-item"
            :class="{ 'unread': !notification.is_read }"
            @click="handleNotificationClick(notification)"
          >
            <!-- 通知图标 -->
            <div class="notification-icon">
              <i :class="getNotificationIcon(notification.type)"></i>
            </div>

            <!-- 通知内容 -->
            <div class="notification-content">
              <div class="notification-header">
                <h5 class="notification-title">{{ notification.title }}</h5>
                <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
              </div>
              <p class="notification-text">{{ notification.content }}</p>
              <div class="notification-meta" v-if="notification.sender">
                <span class="sender-info">
                  来自: <strong>{{ notification.sender.username || notification.sender.real_name }}</strong>
                </span>
                <span class="notification-type">{{ getTypeLabel(notification.type) }}</span>
              </div>
            </div>

            <!-- 未读标记 -->
            <div class="notification-status" v-if="!notification.is_read">
              <div class="unread-dot"></div>
            </div>

            <!-- 操作按钮 -->
            <div class="notification-actions">
              <button 
                v-if="!notification.is_read"
                class="btn btn-sm btn-outline-primary"
                @click.stop="markAsRead(notification)"
                title="标记为已读"
              >
                <i class="fas fa-check"></i>
              </button>
              <div class="dropdown">
                <button 
                  class="btn btn-sm btn-outline-secondary dropdown-toggle"
                  type="button"
                  :id="`dropdown-${notification.uuid}`"
                  data-bs-toggle="dropdown"
                  @click.stop
                >
                  <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu">
                  <li v-if="!notification.is_read">
                    <a class="dropdown-item" href="#" @click.prevent="markAsRead(notification)">
                      <i class="fas fa-check me-2"></i>标记为已读
                    </a>
                  </li>
                  <li v-else>
                    <a class="dropdown-item" href="#" @click.prevent="markAsUnread(notification)">
                      <i class="fas fa-eye me-2"></i>标记为未读
                    </a>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <a class="dropdown-item text-danger" href="#" @click.prevent="deleteNotification(notification)">
                      <i class="fas fa-trash me-2"></i>删除
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载更多 -->
        <div v-if="hasMore && !loading" class="text-center mt-4">
          <button 
            class="btn btn-outline-primary"
            @click="loadMore"
            :disabled="loadingMore"
          >
            <i class="fas fa-chevron-down me-1" :class="{ 'fa-spin': loadingMore }"></i>
            {{ loadingMore ? '加载中...' : '加载更多' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { notificationApi } from '../api/notification.js';

const router = useRouter();

// 响应式数据
const notifications = ref([]);
const loading = ref(false);
const loadingMore = ref(false);
const currentFilter = ref('all');
const page = ref(1);
const pageSize = ref(20);
const hasMore = ref(true);
const totalCount = ref(0);
const unreadCount = ref(0);

// 计算属性
const readCount = computed(() => totalCount.value - unreadCount.value);

const hasUnreadNotifications = computed(() => 
  notifications.value.some(n => !n.is_read)
);

const filteredNotifications = computed(() => {
  switch (currentFilter.value) {
    case 'unread':
      return notifications.value.filter(n => !n.is_read);
    case 'read':
      return notifications.value.filter(n => n.is_read);
    default:
      return notifications.value;
  }
});

// 生命周期
onMounted(() => {
  fetchNotifications();
});

// 监听筛选变化
watch(currentFilter, () => {
  page.value = 1;
  notifications.value = [];
  hasMore.value = true;
  fetchNotifications();
});

// 方法
const fetchNotifications = async (append = false) => {
  if (!append) loading.value = true;
  else loadingMore.value = true;
  
  try {
    const params = {
      skip: append ? notifications.value.length : 0,
      limit: pageSize.value
    };
    
    const response = await notificationApi.getNotifications(params);
    if (response.data.code === 200) {
      const data = response.data.data;
      
      if (append) {
        notifications.value.push(...data.items);
      } else {
        notifications.value = data.items;
      }
      
      totalCount.value = data.total;
      unreadCount.value = data.unread_count;
      hasMore.value = data.items.length === pageSize.value;
    }
  } catch (error) {
    console.error('获取通知失败:', error);
  } finally {
    loading.value = false;
    loadingMore.value = false;
  }
};

const loadMore = () => {
  if (!loadingMore.value && hasMore.value) {
    fetchNotifications(true);
  }
};

const setFilter = (filter) => {
  currentFilter.value = filter;
};

const markAsRead = async (notification) => {
  if (notification.is_read) return;
  
  try {
    const response = await notificationApi.markAsRead(notification.uuid);
    if (response.data.code === 200) {
      notification.is_read = true;
      unreadCount.value = Math.max(0, unreadCount.value - 1);
    }
  } catch (error) {
    console.error('标记通知已读失败:', error);
  }
};

const markAsUnread = async (notification) => {
  // 注意：后端可能没有实现标记为未读的API，这里只是UI演示
  notification.is_read = false;
  unreadCount.value++;
};

const markAllAsRead = async () => {
  try {
    const response = await notificationApi.markAllAsRead();
    if (response.data.code === 200) {
      notifications.value.forEach(n => n.is_read = true);
      unreadCount.value = 0;
    }
  } catch (error) {
    console.error('标记全部已读失败:', error);
  }
};

const deleteNotification = async (notification) => {
  if (!confirm('确定要删除这条通知吗？')) return;
  
  try {
    const response = await notificationApi.deleteNotification(notification.uuid);
    if (response.data.code === 200) {
      const index = notifications.value.findIndex(n => n.uuid === notification.uuid);
      if (index > -1) {
        notifications.value.splice(index, 1);
        totalCount.value--;
        if (!notification.is_read) {
          unreadCount.value--;
        }
      }
    }
  } catch (error) {
    console.error('删除通知失败:', error);
  }
};

const handleNotificationClick = (notification) => {
  // 标记为已读
  if (!notification.is_read) {
    markAsRead(notification);
  }
  
  // 根据通知类型跳转到相应页面
  if (notification.related_uuid) {
    switch (notification.type) {
      case 'like_showcase':
      case 'comment_showcase':
      case 'showcase_approved':
      case 'showcase_rejected':
        router.push(`/showcase/${notification.related_uuid}`);
        break;
      // 可以添加更多通知类型的跳转逻辑
    }
  }
};

const getNotificationIcon = (type) => {
  const iconMap = {
    'like_showcase': 'fas fa-heart text-danger',
    'like_comment': 'fas fa-heart text-danger',
    'comment_showcase': 'fas fa-comment text-primary',
    'reply_comment': 'fas fa-reply text-info',
    'showcase_approved': 'fas fa-check-circle text-success',
    'showcase_rejected': 'fas fa-times-circle text-warning',
    'system_announcement': 'fas fa-bullhorn text-primary'
  };
  return iconMap[type] || 'fas fa-bell text-muted';
};

const getTypeLabel = (type) => {
  const typeMap = {
    'like_showcase': '作品点赞',
    'like_comment': '评论点赞',
    'comment_showcase': '作品评论',
    'reply_comment': '评论回复',
    'showcase_approved': '作品审核',
    'showcase_rejected': '作品审核',
    'system_announcement': '系统公告'
  };
  return typeMap[type] || '通知';
};

const formatTime = (timeString) => {
  const time = new Date(timeString);
  const now = new Date();
  const diff = now - time;
  
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  if (diff < 2592000000) return `${Math.floor(diff / 86400000)}天前`;
  return time.toLocaleDateString();
};

const getEmptyMessage = () => {
  switch (currentFilter.value) {
    case 'unread':
      return '没有未读通知';
    case 'read':
      return '没有已读通知';
    default:
      return '暂无通知';
  }
};

const getEmptyDescription = () => {
  switch (currentFilter.value) {
    case 'unread':
      return '所有通知都已读完了！';
    case 'read':
      return '还没有已读的通知';
    default:
      return '当有新的互动时，您会在这里收到通知';
  }
};
</script>

<style scoped>
.notification-page {
  min-height: calc(100vh - 200px);
  background-color: #f8f9fa;
  padding-top: 80px; /* 为固定导航栏留出空间 */
}

.page-header {
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  padding: 2rem 0;
  margin-bottom: 0;
}

.page-title {
  font-size: 2.8rem; /* 大幅增加标题字体 */
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.page-subtitle {
  font-size: 1.4rem; /* 大幅增加副标题字体 */
  color: #6c757d;
}

.header-buttons {
  display: flex;
  gap: 1.5rem; /* 增加按钮间距 */
}

.refresh-btn,
.mark-read-btn {
  border-radius: 25px !important; /* 强制应用圆角 */
  padding: 0.6rem 1.5rem !important; /* 增加内边距 */
  font-weight: 500;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.mark-read-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem; /* 增加底部间距 */
  padding: 1rem 0; /* 添加上下内边距 */
}

.filter-btn {
  padding: 0.75rem 1.25rem;
  border: none;
  background: #e9ecef;
  color: #6c757d;
  border-radius: 20px;
  font-size: 1.3rem; /* 大幅增加筛选按钮字体 */
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn.active {
  background: #007bff;
  color: white;
}

.filter-btn:hover {
  background: #dee2e6;
}

.filter-btn.active:hover {
  background: #0056b3;
}

.notification-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 1.25rem; /* 增大内边距 */
  border-bottom: 1px solid #e9ecef;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.notification-item:hover {
  background-color: #f8f9fa;
}

.notification-item.unread {
  background-color: #f0f8ff;
  border-left: 4px solid #007bff;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-icon {
  flex-shrink: 0;
  width: 50px; /* 增大图标容器 */
  height: 50px;
  border-radius: 50%;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.25rem; /* 增大间距 */
  font-size: 1.2rem; /* 增大图标字体 */
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.notification-title {
  font-size: 1.6rem; /* 大幅增加通知标题字体 */
  font-weight: 600;
  margin: 0;
  color: #212529;
}

.notification-time {
  font-size: 1.3rem; /* 大幅增加时间字体 */
  color: #6c757d;
  flex-shrink: 0;
  margin-left: 1rem;
}

.notification-text {
  color: #495057;
  margin: 0 0 0.75rem 0;
  font-size: 1.5rem; /* 大幅增加内容字体 */
  line-height: 1.6;
}

.notification-meta {
  display: flex;
  gap: 1rem;
  font-size: 1.2rem; /* 大幅增加元信息字体 */
  color: #6c757d;
}

.notification-status {
  display: flex;
  align-items: center;
  margin-right: 1rem;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: #007bff;
  border-radius: 50%;
}

.notification-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.notification-item:hover .notification-actions {
  opacity: 1;
}

.empty-state {
  padding: 4rem 2rem;
}

.notification-stats {
  padding: 0.5rem 0;
  font-size: 1.3rem; /* 大幅增加统计信息字体 */
}

.sender-info {
  color: #495057;
}

.notification-type {
  background: #e9ecef;
  padding: 0.3rem 0.7rem;
  border-radius: 12px;
  font-size: 1.1rem; /* 大幅增加类型标签字体 */
}

@media (max-width: 768px) {
  .page-header {
    padding: 1.5rem 0;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .notification-item {
    padding: 0.75rem;
  }
  
  .notification-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .notification-time {
    margin-left: 0;
    margin-top: 0.25rem;
  }
  
  .notification-actions {
    opacity: 1;
  }
  
  .filter-tabs {
    flex-wrap: wrap;
  }
}
</style>