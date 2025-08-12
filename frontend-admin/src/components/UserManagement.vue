<script setup>
import { ref } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined } from '@ant-design/icons-vue';

const users = ref([
  { 
    id: 1, 
    name: '张三', 
    number: '001', 
    email: 'zhangsan@example.com', 
    school: '北京大学',
    role: '学生'
  },
  { 
    id: 2, 
    name: '李四', 
    number: '002', 
    email: 'lisi@example.com', 
    school: '清华大学',
    role: '学生'
  },
  { 
    id: 3, 
    name: '王五', 
    number: '003', 
    email: 'wangwu@example.com', 
    school: '复旦大学',
    role: '教师'
  }
]);

const searchValue = ref('');

const addNewUser = () => {
  // Implement add user functionality
  console.log('Add new user');
};

const refreshList = () => {
  // Implement refresh functionality
  console.log('Refresh user list');
};

const configSettings = () => {
  // Implement settings functionality
  console.log('Configure settings');
};

const searchUser = () => {
  // Implement search functionality
  console.log('Search user:', searchValue.value);
};

const resetSearch = () => {
  // Reset search value and refresh list
  searchValue.value = '';
  console.log('Reset search');
  refreshList();
};

const viewUser = (userId) => {
  console.log('View user:', userId);
};

const editUser = (userId) => {
  console.log('Edit user:', userId);
};

const blockUser = (userId) => {
  console.log('Block user:', userId);
};

const deleteUser = (userId) => {
  console.log('Delete user:', userId);
};
</script>

<template>
  <div class="user-management">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <p class="page-subtitle">查看、编辑系统中的用户信息</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="addNewUser">
          <template #icon><PlusOutlined /></template>
          添加用户
        </a-button>
        <a-button class="refresh-btn" @click="refreshList">
          刷新
        </a-button>
        <a-button class="settings-btn" @click="configSettings">
          <template #icon><SettingOutlined /></template>
          列设置
        </a-button>
      </div>
      
      <div class="right-actions">
        <a-input 
          v-model:value="searchValue"
          placeholder="用户名/邮箱地址/uuid"
          class="search-input rounded-input"
          allow-clear
        />
        <a-button type="primary" class="search-btn" @click="searchUser">
          查询
        </a-button>
        <a-button class="reset-btn" @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>
    
    <a-table :dataSource="users" :pagination="false" class="user-table">
      <a-table-column key="name" title="用户名" data-index="name" />
      <a-table-column key="number" title="用户编号" data-index="number" />
      <a-table-column key="email" title="邮箱地址" data-index="email" />
      <a-table-column key="school" title="所在学校" data-index="school" />
      <a-table-column key="role" title="用户角色" data-index="role" />
      <a-table-column key="action" title="操作">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewUser(record.id)">查看</a-button>
            <a-button size="small" type="primary" @click="editUser(record.id)">编辑</a-button>
            <a-button size="small" danger @click="blockUser(record.id)">封禁</a-button>
            <a-button size="small" danger @click="deleteUser(record.id)">删除</a-button>
          </div>
        </template>
      </a-table-column>
    </a-table>
  </div>
</template>

<style scoped>
.user-management {
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* 页面标题样式 */
.page-header {
  margin-bottom: 16px;
}

.page-title {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 500;
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: #666;
}

/* 操作栏样式 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.left-actions {
  display: flex;
  gap: 8px;
}

.right-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 搜索框样式 */
.search-input {
  width: 250px;
  margin-right: 8px;
}

/* 圆角输入框 */
.rounded-input :deep(.ant-input) {
  border-radius: 8px;
}

/* 表格样式 */
.user-table {
  width: 100%;
}

/* 统一表格样式 */
:deep(.ant-table) {
  border-radius: 12px;
  font-size: 14px;
}

:deep(.ant-table-thead > tr > th) {
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  padding: 8px 8px;
  font-weight: 500;
}

:deep(.ant-table-tbody > tr > td) {
  padding: 6px 8px;
}

:deep(.ant-table-row) {
  height: 40px;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background-color: #f5f5f5;
}

:deep(.ant-table-tbody > tr > td .action-buttons) {
  display: flex;
  gap: 8px;
}

/* 统一按钮样式 */
:deep(.ant-btn-primary) {
  background: transparent;
  color: #1890ff;
  border-color: #1890ff;
  height: 30px;
  padding: 0 12px;
  box-shadow: 0 2px 4px rgba(24, 144, 255, 0.2);
}

:deep(.ant-btn-primary:hover) {
  background-color: rgba(24, 144, 255, 0.1);
  color: #1890ff;
  border-color: #1890ff;
}

:deep(.ant-btn) {
  border-radius: 6px;
  height: 28px;
  padding: 0 12px;
  font-size: 13px;
}

/* 搜索框placeholder样式 */
.search-input :deep(.ant-input::placeholder) {
  font-size: 11px;
  font-weight: 500;
  color: #bfbfbf;
}
</style>
