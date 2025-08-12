<script setup>
import { ref } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined } from '@ant-design/icons-vue';

const posts = ref([
  { 
    id: 1, 
    title: '关于第一周作业的讨论', 
    author: '学生B', 
    createTime: '2024-08-12',
  },
]);

const searchValue = ref('');

const addNewPost = () => {
  console.log('Add new post');
};

const refreshList = () => {
  console.log('Refresh post list');
};

const configSettings = () => {
  console.log('Configure settings');
};

const searchPost = () => {
  console.log('Search post:', searchValue.value);
};

const resetSearch = () => {
  searchValue.value = '';
  console.log('Reset search');
  refreshList();
};

const viewPost = (postId) => {
  console.log('View post:', postId);
};

const editPost = (postId) => {
  console.log('Edit post:', postId);
};

const deletePost = (postId) => {
  console.log('Delete post:', postId);
};
</script>

<template>
  <div class="forum-management">
    <div class="page-header">
      <h1 class="page-title">论坛内容管理</h1>
      <p class="page-subtitle">查看、编辑系统中的论坛内容</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="addNewPost">
          <template #icon><PlusOutlined /></template>
          添加帖子
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
          placeholder="帖子标题/uuid"
          class="search-input rounded-input"
          allow-clear
        />
        <a-button type="primary" class="search-btn" @click="searchPost">
          查询
        </a-button>
        <a-button class="reset-btn" @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>
    
    <a-table :dataSource="posts" :pagination="false" class="forum-table">
      <a-table-column key="title" title="帖子标题" data-index="title" />
      <a-table-column key="author" title="作者" data-index="author" />
      <a-table-column key="createTime" title="发布时间" data-index="createTime" />
      <a-table-column key="action" title="操作">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewPost(record.id)">查看</a-button>
            <a-button size="small" type="primary" @click="editPost(record.id)">编辑</a-button>
            <a-button size="small" danger @click="deletePost(record.id)">删除</a-button>
          </div>
        </template>
      </a-table-column>
    </a-table>
  </div>
</template>

<style scoped>
.forum-management {
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

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

.search-input {
  width: 250px;
  margin-right: 8px;
}

.rounded-input :deep(.ant-input) {
  border-radius: 8px;
}

.forum-table {
  width: 100%;
}

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

.search-input :deep(.ant-input::placeholder) {
  font-size: 11px;
  font-weight: 500;
  color: #bfbfbf;
}
</style>
