<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { UserOutlined, LoginOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import request from '../utils/request';

const router = useRouter();

const user = ref({
  name: 'XX',
  avatar: null,
  username: '',
  email: ''
});

const isLoggedIn = computed(() => {
  return localStorage.getItem('access_token') !== null;
});

const API_BASE_URL = 'http://localhost:8000/api/v1/auth';

const fetchUserInfo = async () => {
  if (!isLoggedIn.value) return;
  
  try {
    const response = await request.get(`${API_BASE_URL}/me`);
    
    if (response.data.code === 200) {
      const userData = response.data.data;
      user.value = {
        name: userData.username || userData.real_name || 'XX',
        avatar: userData.avatar_url,
        username: userData.username,
        email: userData.email
      };
    }
  } catch (error) {
    console.error('Failed to fetch user info:', error);
    // 401错误会被request拦截器自动处理
  }
};

const handleLogin = () => {
  router.push('/login');
};

const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  user.value = { name: 'XX', avatar: null, username: '', email: '' };
  message.success('已退出登录');
  router.push('/login');
};

const handleMenuClick = ({ key }) => {
  if (key === '3') {
    handleLogout();
  }
};

watch(isLoggedIn, (newValue) => {
  if (newValue) {
    fetchUserInfo();
  }
});

onMounted(() => {
  if (isLoggedIn.value) {
    fetchUserInfo();
  }
});

</script>

<template>
  <div class="navbar">
    <div class="navbar-title">
      <h1>{{ '《开源项目构建与实践》 课程资源管理后台' }}</h1>
    </div>
    <div class="navbar-actions">
      <template v-if="isLoggedIn">
        <span class="welcome-text">欢迎您，{{ user.name }}</span>
        <a-dropdown placement="bottomRight" @click="handleMenuClick">
          <a-avatar class="avatar" :size="36">
            <template #icon>
              <UserOutlined v-if="!user.avatar" />
              <img v-else :src="user.avatar" alt="User avatar">
            </template>
          </a-avatar>
          <template #overlay>
            <a-menu @click="handleMenuClick">
              <a-menu-item key="1">个人设置</a-menu-item>
              <a-menu-item key="2">修改密码</a-menu-item>
              <a-menu-divider />
              <a-menu-item key="3">退出登录</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </template>
      <template v-else>
        <a-button type="primary" @click="handleLogin" class="login-btn">
          <LoginOutlined />
          登录
        </a-button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.navbar {
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #f0f2f5;
  /* Removed border-bottom */
}

.navbar-title h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.navbar-actions {
  display: flex;
  align-items: center;
}

.welcome-text {
  margin-right: 12px;
  font-size: 14px;
}

.avatar {
  cursor: pointer;
  background-color: #1890ff;
}

:deep(.ant-dropdown-menu) {
  min-width: 120px;
}

:deep(.ant-dropdown-menu-item) {
  padding: 8px 16px;
  font-size: 14px;
}

.login-btn {
  border-radius: 6px;
  font-weight: 500;
}
</style>
