<script setup>
import { ref } from 'vue';
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
}

.sidebar-container.collapsed {
  flex-basis: 80px;
}

.content-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

:deep(.user-management),
:deep(.table-section),
:deep([class*="-management"]) {
  background-color: white;
  border-radius: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
}
</style>
