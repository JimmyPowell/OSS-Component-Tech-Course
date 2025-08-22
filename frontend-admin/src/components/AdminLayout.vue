<script setup>
import { ref } from 'vue';
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons-vue';
import Sidebar from './Sidebar.vue';
import Navbar from './Navbar.vue';

const isCollapsed = ref(false);

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};
</script>

<template>
  <div class="admin-layout">
    <div class="navbar-container">
      <Navbar />
    </div>
    <div class="main-content-wrapper">
      <div class="sidebar-container" :class="{ collapsed: isCollapsed }">
        <Sidebar :is-collapsed="isCollapsed" @toggle="toggleSidebar" />
        <div class="toggle-sidebar-btn" :class="{ collapsed: isCollapsed }" @click="toggleSidebar">
          <template v-if="isCollapsed">
            <MenuUnfoldOutlined />
          </template>
          <template v-else>
            <MenuFoldOutlined />
            <span class="btn-text">折叠侧边栏</span>
          </template>
        </div>
      </div>
      <div class="content-container">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background-color: #f0f2f5;
}

.navbar-container {
  flex: 0 0 auto;
  z-index: 10;
  background-color: #f0f2f5;
}

.main-content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar-container {
  flex: 0 0 220px;
  background-color: transparent;
  padding-top: 20px;
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
  will-change: flex-basis, width;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

.sidebar-container.collapsed {
  flex-basis: 80px;
}

.content-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: calc(100vh - 64px); /* 限制最大高度，减去导航栏高度 */
}

:deep(.user-management),
:deep(.table-section),
:deep([class*="-management"]) {
  background-color: white;
  border-radius: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.toggle-sidebar-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  height: 36px;
  background-color: #ffffff;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  color: #595959;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  z-index: 5;
  gap: 6px;
  padding: 0 12px;
  white-space: nowrap;
  width: auto;
  min-width: 36px;
}

.toggle-sidebar-btn.collapsed {
  width: 36px;
  padding: 0;
}

.toggle-sidebar-btn .btn-text {
  font-size: 12px;
  color: inherit;
}

.toggle-sidebar-btn:hover {
  background-color: #f5f5f5;
  border-color: #40a9ff;
  color: #40a9ff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}
</style>
