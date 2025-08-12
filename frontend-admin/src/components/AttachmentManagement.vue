<script setup>
import { ref } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined } from '@ant-design/icons-vue';

const attachments = ref([
  { 
    id: 1, 
    name: '课程大纲', 
    number: 'ATT-001', 
    uploader: '张三', 
    uploadTime: '2024-08-12',
    type: 'PDF'
  },
]);

const searchValue = ref('');

const addNewAttachment = () => {
  console.log('Add new attachment');
};

const refreshList = () => {
  console.log('Refresh attachment list');
};

const configSettings = () => {
  console.log('Configure settings');
};

const searchAttachment = () => {
  console.log('Search attachment:', searchValue.value);
};

const resetSearch = () => {
  searchValue.value = '';
  console.log('Reset search');
  refreshList();
};

const viewAttachment = (attachmentId) => {
  console.log('View attachment:', attachmentId);
};

const editAttachment = (attachmentId) => {
  console.log('Edit attachment:', attachmentId);
};

const deleteAttachment = (attachmentId) => {
  console.log('Delete attachment:', attachmentId);
};
</script>

<template>
  <div class="attachment-management">
    <div class="page-header">
      <h1 class="page-title">课程附件管理</h1>
      <p class="page-subtitle">查看、编辑系统中的课程附件</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="addNewAttachment">
          <template #icon><PlusOutlined /></template>
          添加附件
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
          placeholder="附件名称/uuid"
          class="search-input rounded-input"
          allow-clear
        />
        <a-button type="primary" class="search-btn" @click="searchAttachment">
          查询
        </a-button>
        <a-button class="reset-btn" @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>
    
    <a-table :dataSource="attachments" :pagination="false" class="attachment-table">
      <a-table-column key="name" title="附件名称" data-index="name" />
      <a-table-column key="number" title="附件编号" data-index="number" />
      <a-table-column key="type" title="附件类型" data-index="type" />
      <a-table-column key="uploader" title="发布者" data-index="uploader" />
      <a-table-column key="uploadTime" title="发布时间" data-index="uploadTime" />
      <a-table-column key="action" title="操作">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewAttachment(record.id)">查看</a-button>
            <a-button size="small" type="primary" @click="editAttachment(record.id)">编辑</a-button>
            <a-button size="small" danger @click="deleteAttachment(record.id)">删除</a-button>
          </div>
        </template>
      </a-table-column>
    </a-table>
  </div>
</template>

<style scoped>
.attachment-management {
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

.attachment-table {
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
