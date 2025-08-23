<template>
  <nav class="navbar navbar-default navbar-fixed-top" :class="{ 'navbar-index': isHome, active: isNavbarActive }">
    <div class="container">
      <!-- 左侧logo和菜单 -->
      <div class="navbar-header">
        <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
          <span class="iconfont icon-menu"></span>
        </button>
        <a class="navbar-logo" href="index.html"></a>
      </div>
      
      <div id="navbar" class="navbar--collapse navbar-content">
        <div class="navbar-col">
          <ul class="nav navbar-nav" id="nav">
            <li v-for="link in navLinks" :key="link.path" :class="{ active: route.path === link.path }">
              <router-link :to="link.path">{{ link.name }}</router-link>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- 右侧用户控件 -->
      <div class="link-group">
        <!-- 根据登录状态显示不同内容 -->
        <template v-if="isUserLoggedIn">
          <!-- 通知图标 -->
          <div class="notification-icon" @click="toggleNotificationMenu">
            <BellOutlined :style="{ fontSize: '20px', color: '#666' }" />
            <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
            
            <!-- 通知下拉菜单 -->
            <div class="notification-menu" v-if="showNotificationMenu">
              <div class="notification-header">
                <span>通知</span>
                <button v-if="unreadCount > 0" @click="markAllAsRead" class="mark-all-read">全部已读</button>
              </div>
              <div class="notification-list" v-if="notifications.length > 0">
                <div 
                  v-for="notification in notifications" 
                  :key="notification.uuid"
                  class="notification-item"
                  :class="{ unread: !notification.is_read }"
                  @click="handleNotificationClick(notification)"
                >
                  <div class="notification-content">
                    <div class="notification-title">{{ notification.title }}</div>
                    <div class="notification-text">{{ notification.content }}</div>
                    <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
                  </div>
                  <div v-if="!notification.is_read" class="unread-dot"></div>
                </div>
              </div>
              <div v-else class="notification-empty">暂无通知</div>
              <div class="notification-footer">
                <router-link to="/notifications" class="view-all">查看全部</router-link>
              </div>
            </div>
          </div>
          
          <div class="user-avatar" @click="toggleUserMenu">
            <div class="avatar-circle">
              <img v-if="user?.avatar_url" :src="user.avatar_url" :alt="user.username" class="avatar-image" />
              <span v-else class="avatar-initial">{{ userInitial }}</span>
            </div>
            <!-- 用户菜单 -->
            <div class="user-menu" v-if="showUserMenu">
              <div class="user-menu-header">
                <div class="username">{{ displayName }}</div>
                <div class="role-info">{{ userRoleDisplay }}</div>
              </div>
              <div class="user-menu-item" @click="goToProfile">个人资料</div>
              <div class="user-menu-item" @click="goToMyHomework">我的作业</div>
              <div class="user-menu-item" @click="goToMyShowcase">我的作品</div>
              <div class="user-menu-item" @click="goToSettings">设置</div>
              <div class="user-menu-divider"></div>
              <div class="user-menu-item logout" @click="handleLogout">退出登录</div>
            </div>
          </div>
        </template>
        <template v-else>
          <button @click="showLoginModal = true" class="btn btn-login">登录</button><button @click="showRegisterModal = true" class="btn btn-register">注册</button>
        </template>
      </div>
      <!--/.nav-collapse -->
    </div>
    
    <!-- 登录和注册弹窗 -->
    <LoginModal 
      v-model="showLoginModal" 
      @switch-to-register="switchToRegister"
    />
    <RegisterModal 
      v-model="showRegisterModal" 
      @switch-to-login="switchToLogin"
    />
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { BellOutlined } from '@ant-design/icons-vue';
import { notificationApi } from '../api/notification';
import LoginModal from './LoginModal.vue';
import RegisterModal from './RegisterModal.vue';

const route = useRoute();
const authStore = useAuthStore();
const isScrolled = ref(false);
const showLoginModal = ref(false);
const showRegisterModal = ref(false);
const showUserMenu = ref(false);

// 通知相关状态
const showNotificationMenu = ref(false);
const notifications = ref([]);
const unreadCount = ref(0);

// 获取用户登录状态和信息
const isUserLoggedIn = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

// 计算用户角色显示
const userRoleDisplay = computed(() => {
  const role = user.value?.role || 'user'
  switch(role) {
    case 'admin': return '超级管理员'
    case 'manager': return '管理员'
    case 'teacher': return '教师'
    default: return '学生'
  }
})

// 监听auth store的登录弹窗状态
watch(() => authStore.shouldShowLoginModal, (shouldShow) => {
  showLoginModal.value = shouldShow
})

// 监听本地登录弹窗状态变化，同步到auth store
watch(showLoginModal, (show) => {
  if (!show && authStore.shouldShowLoginModal) {
    authStore.hideLoginModal()
  }
})

// 计算用户显示名称
const displayName = computed(() => {
  const userInfo = user.value;
  if (!userInfo) return '用户';
  
  // 优先显示真实姓名，如果没有则显示用户名
  if (userInfo.real_name && userInfo.real_name.trim()) {
    return userInfo.real_name;
  }
  
  return userInfo.username || '用户';
});

// 计算用户头像初始字母
const userInitial = computed(() => {
  const username = displayName.value;
  return username ? username.charAt(0).toUpperCase() : '?';
})

// 切换用户菜单显示/隐藏
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
  console.log('切换用户菜单显示状态:', showUserMenu.value);
};

// 点击页面其他地方关闭用户菜单
const closeUserMenu = (event) => {
  // 检查点击是否在用户头像之外
  const avatarEl = document.querySelector('.user-avatar');
  if (avatarEl && !avatarEl.contains(event.target)) {
    showUserMenu.value = false;
  }
};

// 处理退出登录
const handleLogout = async () => {
  await authStore.logout();
  console.log('用户已退出登录');
  showUserMenu.value = false;
};

// 导航到个人资料页面
const goToProfile = () => {
  showUserMenu.value = false;
  // TODO: 实现个人资料页面
  console.log('导航到个人资料页面');
};

// 导航到我的作业页面
const goToMyHomework = () => {
  showUserMenu.value = false;
  // TODO: 实现我的作业页面或在作业页面筛选用户作业
  console.log('导航到我的作业页面');
};

// 导航到我的作品页面
const goToMyShowcase = () => {
  showUserMenu.value = false;
  // TODO: 实现我的作品页面或在作品展示页面筛选用户作品
  console.log('导航到我的作品页面');
};

// 导航到设置页面
const goToSettings = () => {
  showUserMenu.value = false;
  // TODO: 实现设置页面
  console.log('导航到设置页面');
};

// 通知相关函数
const toggleNotificationMenu = () => {
  showNotificationMenu.value = !showNotificationMenu.value;
  if (showNotificationMenu.value) {
    fetchNotifications();
  }
};

const fetchNotifications = async () => {
  if (!isUserLoggedIn.value) return;
  
  try {
    const response = await notificationApi.getNotifications({ limit: 10 });
    if (response.data.code === 200) {
      notifications.value = response.data.data.items;
    }
  } catch (error) {
    console.error('获取通知失败:', error);
  }
};

const fetchUnreadCount = async () => {
  if (!isUserLoggedIn.value) return;
  
  try {
    const response = await notificationApi.getUnreadCount();
    if (response.data.code === 200) {
      unreadCount.value = response.data.data.unread_count;
    }
  } catch (error) {
    console.error('获取未读通知数量失败:', error);
  }
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

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    try {
      await notificationApi.markAsRead(notification.uuid);
      notification.is_read = true;
      unreadCount.value = Math.max(0, unreadCount.value - 1);
    } catch (error) {
      console.error('标记通知已读失败:', error);
    }
  }
  
  // 根据通知类型跳转到相应页面
  if (notification.related_uuid) {
    // TODO: 根据通知类型跳转到相应页面
    console.log('跳转到相关页面:', notification);
  }
  
  showNotificationMenu.value = false;
};

const formatTime = (timeString) => {
  const time = new Date(timeString);
  const now = new Date();
  const diff = now - time;
  
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  return `${Math.floor(diff / 86400000)}天前`;
};

// 点击页面其他地方关闭通知菜单
const closeNotificationMenu = (event) => {
  const notificationEl = document.querySelector('.notification-icon');
  if (notificationEl && !notificationEl.contains(event.target)) {
    showNotificationMenu.value = false;
  }
};

const navLinks = ref([
  { name: '首页', path: '/' },
  { name: '课程资源', path: '/resources' },
  { name: '作业墙', path: '/homework' },
  { name: '作品展示', path: '/showcase' },
  { name: '开源社区', path: '/community' },
  { name: '技术博客', path: '/blogs' },
]);

// Check if the current route is the homepage
const isHome = computed(() => route.path === '/');

// Determine if the navbar should have the 'active' class
const isNavbarActive = computed(() => {
  if (!isHome.value) {
    return true; // Always active on non-home pages
  }
  return isScrolled.value; // On home page, depends on scroll position
});

const handleScroll = () => {
  if (isHome.value) {
    isScrolled.value = window.scrollY > 50;
  }
};

onMounted(() => {
  // Initial check for non-home pages
  if (!isHome.value) {
    isScrolled.value = true;
  }
  window.addEventListener('scroll', handleScroll);
  window.addEventListener('click', closeUserMenu);
  window.addEventListener('click', closeNotificationMenu);
  
  // 检查和输出用户登录状态
  console.log('导航栏加载 - 用户登录状态:', isUserLoggedIn.value);
  if (isUserLoggedIn.value) {
    console.log('用户信息:', user.value);
    // 获取未读通知数量
    fetchUnreadCount();
    // 每隔30秒检查一次未读通知数量
    setInterval(fetchUnreadCount, 30000);
  }
});

// 监听登录状态变化
watch(isUserLoggedIn, (newValue) => {
  if (newValue) {
    fetchUnreadCount();
  } else {
    unreadCount.value = 0;
    notifications.value = [];
    showNotificationMenu.value = false;
  }
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('click', closeUserMenu);
  window.removeEventListener('click', closeNotificationMenu);
});

// 处理弹窗切换
const switchToRegister = () => {
  showLoginModal.value = false;
  showRegisterModal.value = true;
};

const switchToLogin = () => {
  showRegisterModal.value = false;
  showLoginModal.value = true;
};
</script>

<style scoped>
/* 容器布局 - 使用flex布局使元素更紧凑 */
.container {
  display: flex;
  align-items: center;
  justify-content: flex-start; /* 改为左对齐，使元素更紧凑 */
  flex-wrap: nowrap; /* 防止换行 */
  gap: 5px; /* 组件间的间距 */
}

/* 调整导航内容区域 */
.navbar-content {
  flex-grow: 1;
  margin: 0 10px; /* 进一步减少左右间距 */
}

/* 确保按钮继承原有的样式 */
.btn {
  display: inline-block;
  padding: 8px 20px;
  margin: 0 5px;
  border: 2px solid;
  border-radius: 40px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
  background: none;
}

.btn-login {
  color: #545ae7;
  border-color: #545ae7;
  background-color: transparent;
}

.btn-login:hover {
  background-color: #545ae7;
  color: white;
}

.btn-register {
  color: white;
  border-color: #545ae7;
  background-color: #545ae7;
}

.btn-register:hover {
  background-color: transparent;
  color: #545ae7;
}

/* 用户头像样式 */
.user-avatar {
  position: relative;
  cursor: pointer;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #545ae7;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

.avatar-initial {
  text-transform: uppercase;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

/* 用户菜单样式 */
.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 140px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-top: 8px;
  z-index: 1000;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.user-menu-header {
  background: linear-gradient(135deg, #545ae7 0%, #6c5ce7 100%);
  color: white;
  padding: 12px;
}

.user-menu-header .username {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 2px;
}

.user-menu-header .role-info {
  font-size: 12px;
  opacity: 0.9;
}

.user-menu-divider {
  height: 1px;
  background-color: #e5e7eb;
  margin: 4px 0;
}

.user-menu-item {
  padding: 8px 12px;
  font-size: 13px;
  color: #374151;
  transition: all 0.2s ease;
  cursor: pointer;
}

.user-menu-item:hover {
  background-color: #f9fafb;
  color: #545ae7;
}

.user-menu-item.logout {
  color: #dc2626;
}

.user-menu-item.logout:hover {
  background-color: #fef2f2;
  color: #dc2626;
}

/* 通知相关样式 */
.notification-icon {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin-right: 15px;
  border-radius: 50%;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.notification-icon:hover {
  background-color: rgba(84, 90, 231, 0.1);
}

.notification-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: #dc2626;
  color: white;
  font-size: 10px;
  font-weight: 600;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.notification-menu {
  position: absolute;
  top: 50px;
  right: 0;
  width: 320px;
  max-height: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  border: 1px solid #e3e5e8;
  overflow: hidden;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e3e5e8;
  background-color: #f9fafb;
}

.notification-header span {
  font-weight: 600;
  color: #2c2f33;
  font-size: 14px;
}

.mark-all-read {
  background: none;
  border: none;
  color: #545ae7;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.mark-all-read:hover {
  background-color: rgba(84, 90, 231, 0.1);
}

.notification-list {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f3f4;
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
}

.notification-item:hover {
  background-color: #f9fafb;
}

.notification-item.unread {
  background-color: #f8f9ff;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-content {
  flex: 1;
  margin-right: 8px;
}

.notification-title {
  font-weight: 600;
  color: #2c2f33;
  font-size: 13px;
  line-height: 1.3;
  margin-bottom: 4px;
}

.notification-text {
  color: #72767d;
  font-size: 12px;
  line-height: 1.4;
  margin-bottom: 6px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.notification-time {
  color: #99aab5;
  font-size: 11px;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background-color: #545ae7;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.notification-empty {
  padding: 40px 16px;
  text-align: center;
  color: #72767d;
  font-size: 14px;
}

.notification-footer {
  padding: 12px 16px;
  border-top: 1px solid #e3e5e8;
  background-color: #f9fafb;
  text-align: center;
}

.view-all {
  color: #545ae7;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
}

.view-all:hover {
  color: #4c51bf;
  text-decoration: underline;
}
</style>
