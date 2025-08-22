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
import LoginModal from './LoginModal.vue';
import RegisterModal from './RegisterModal.vue';

const route = useRoute();
const authStore = useAuthStore();
const isScrolled = ref(false);
const showLoginModal = ref(false);
const showRegisterModal = ref(false);
const showUserMenu = ref(false);

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

const navLinks = ref([
  { name: '首页', path: '/' },
  { name: '课程资源', path: '/resources' },
  { name: '作业墙', path: '/homework' }, // Placeholder
  { name: '作品展示', path: '/showcase' }, // Placeholder
  { name: '开源社区', path: '/community' }, // Placeholder
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
  
  // 检查和输出用户登录状态
  console.log('导航栏加载 - 用户登录状态:', isUserLoggedIn.value);
  if (isUserLoggedIn.value) {
    console.log('用户信息:', user.value);
  }
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('click', closeUserMenu);
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
</style>
