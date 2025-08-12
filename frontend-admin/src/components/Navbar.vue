<script setup>
import { ref } from 'vue';
import { UserOutlined } from '@ant-design/icons-vue';

const user = ref({
  name: 'XX',
  avatar: null
});
</script>

<template>
  <div class="navbar">
    <div class="navbar-title">
      <h1>{{ '《开源项目构建与实践》 课程资源管理后台' }}</h1>
    </div>
    <div class="navbar-actions">
      <span class="welcome-text">欢迎您，{{ user.name }}</span>
      <a-dropdown placement="bottomRight">
        <a-avatar class="avatar" :size="36">
          <template #icon>
            <UserOutlined v-if="!user.avatar" />
            <img v-else :src="user.avatar" alt="User avatar">
          </template>
        </a-avatar>
        <template #overlay>
          <a-menu>
            <a-menu-item key="1">个人设置</a-menu-item>
            <a-menu-item key="2">修改密码</a-menu-item>
            <a-menu-divider />
            <a-menu-item key="3">退出登录</a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
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
</style>
