<script setup>
import { ref } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined } from '@ant-design/icons-vue';

const videos = ref([
  { 
    id: 1, 
    name: '第一讲：课程简介', 
    number: 'VID-001', 
    uploader: '张三', 
    uploadTime: '2024-08-12',
    cover: ''
  },
]);

const searchValue = ref('');

const addNewVideo = () => {
  console.log('Add new video');
};

const refreshList = () => {
  console.log('Refresh video list');
};

const configSettings = () => {
  console.log('Configure settings');
};

const searchVideo = () => {
  console.log('Search video:', searchValue.value);
};

const resetSearch = () => {
  searchValue.value = '';
  console.log('Reset search');
  refreshList();
};

const viewVideo = (videoId) => {
  console.log('View video:', videoId);
};

const editVideo = (videoId) => {
  console.log('Edit video:', videoId);
};

const deleteVideo = (videoId) => {
  console.log('Delete video:', videoId);
};
</script>

<template>
  <div class="video-management">
    <div class="page-header">
      <h1 class="page-title">课程视频管理</h1>
      <p class="page-subtitle">查看、编辑系统中的课程视频</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="addNewVideo">
          <template #icon><PlusOutlined /></template>
          添加视频
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
          placeholder="视频名称/uuid"
          class="search-input rounded-input"
          allow-clear
        />
        <a-button type="primary" class="search-btn" @click="searchVideo">
          查询
        </a-button>
        <a-button class="reset-btn" @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>
    
    <a-table :dataSource="videos" :pagination="false" class="video-table">
      <a-table-column key="cover" title="视频封面预览">
        <template #default="{ record }">
          <div class="cover-preview">
            <img v-if="record.cover" :src="record.cover" alt="cover" />
            <div v-else class="cover-placeholder"></div>
          </div>
        </template>
      </a-table-column>
      <a-table-column key="name" title="视频名称" data-index="name" />
      <a-table-column key="number" title="视频编号" data-index="number" />
      <a-table-column key="uploader" title="发布者" data-index="uploader" />
      <a-table-column key="uploadTime" title="发布时间" data-index="uploadTime" />
      <a-table-column key="action" title="操作">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewVideo(record.id)">查看</a-button>
            <a-button size="small" type="primary" @click="editVideo(record.id)">编辑</a-button>
            <a-button size="small" danger @click="deleteVideo(record.id)">删除</a-button>
          </div>
        </template>
      </a-table-column>
    </a-table>
  </div>
</template>

<style scoped>
.video-management {
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

.video-table {
  width: 100%;
}

.cover-preview {
  width: 256px;
  height: 144px;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background-color: #f0f0f0;
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
