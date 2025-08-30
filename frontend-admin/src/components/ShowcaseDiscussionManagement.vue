<script setup>
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue';
import { SearchOutlined, MessageOutlined, DeleteOutlined, SettingOutlined, EyeOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import request from '../utils/request';

const discussions = ref([]);
const loading = ref(false);
const searchValue = ref('');

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
});

// 讨论详情抽屉
const discussionDetailDrawerVisible = ref(false);
const discussionDetail = ref(null);

// 列设置
const columnSettingsVisible = ref(false);
const availableColumns = [
  { key: 'showcase_name', title: '作品名称', visible: true },
  { key: 'comment_content', title: '评论内容', visible: true },
  { key: 'author_name', title: '评论者', visible: true },
  { key: 'reply_count', title: '回复数', visible: true },
  { key: 'created_at', title: '评论时间', visible: true },
];
const columnSettings = reactive([...availableColumns]);

// 表格高度自适应
const tableHeight = ref(600);

const API_BASE_URL = 'http://localhost:8000/api/v1/showcase-comments';

const fetchDiscussions = async (page = 1, pageSize = 20, search = '') => {
  loading.value = true;
  try {
    // 先获取所有作品
    const showcasesResponse = await request.get('http://localhost:8000/api/v1/admin/showcases');
    if (showcasesResponse.data.code !== 200) {
      message.error('获取作品列表失败');
      return;
    }
    
    const showcases = showcasesResponse.data.data.items;
    const allDiscussions = [];
    
    // 为每个作品获取评论
    for (const showcase of showcases) {
      try {
        const params = new URLSearchParams({
          showcase_id: showcase.id.toString(),
          skip: '0',
          limit: '100'
        });
        
        const commentsResponse = await request.get(`${API_BASE_URL}?${params}`);
        if (commentsResponse.data.code === 200) {
          const comments = commentsResponse.data.data.items.map(comment => ({
            ...comment,
            showcase_name: showcase.name,
            showcase_uuid: showcase.uuid
          }));
          allDiscussions.push(...comments);
        }
      } catch (error) {
        console.warn(`Failed to fetch comments for showcase ${showcase.name}:`, error);
      }
    }
    
    // 按时间排序
    allDiscussions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    // 应用搜索过滤
    let filteredDiscussions = allDiscussions;
    if (search) {
      filteredDiscussions = allDiscussions.filter(d => 
        d.showcase_name?.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    // 应用分页
    const skip = (page - 1) * pageSize;
    const paginatedDiscussions = filteredDiscussions.slice(skip, skip + pageSize);
    
    discussions.value = paginatedDiscussions;
    pagination.total = filteredDiscussions.length;
    pagination.current = page;
    pagination.pageSize = pageSize;
  } catch (error) {
    console.error('Failed to fetch discussions:', error);
    message.error('获取讨论列表失败');
  } finally {
    loading.value = false;
  }
};

const refreshList = () => {
  fetchDiscussions(pagination.current, pagination.pageSize, searchValue.value);
};

const searchDiscussion = () => {
  fetchDiscussions(1, pagination.pageSize, searchValue.value);
};

const resetSearch = () => {
  searchValue.value = '';
  fetchDiscussions(1, pagination.pageSize, '');
};

const handleTableChange = (paginationInfo) => {
  fetchDiscussions(paginationInfo.current, paginationInfo.pageSize, searchValue.value);
};

// 查看讨论详情
const viewDiscussion = async (commentId) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${commentId}`);
    
    if (response.data.code === 200) {
      discussionDetail.value = response.data.data;
      discussionDetailDrawerVisible.value = true;
    }
  } catch (error) {
    message.error('获取讨论详情失败');
  }
};

// 删除讨论
const deleteDiscussion = (commentId) => {
  const discussion = discussions.value.find(d => d.id === commentId);
  
  Modal.confirm({
    title: '确认删除讨论',
    content: `确定要删除这条讨论吗？此操作不可恢复！`,
    okType: 'danger',
    onOk: async () => {
      try {
        const response = await request.delete(`${API_BASE_URL}/${commentId}`);
        
        if (response.data.code === 200) {
          message.success('讨论删除成功');
          refreshList();
        } else {
          message.error(response.data.message || '删除失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('删除讨论失败');
        }
      }
    }
  });
};

// 列设置相关
const visibleColumns = computed(() => columnSettings.filter(c => c.visible));

const configSettings = () => {
  columnSettingsVisible.value = true;
};

const handleColumnSettingChange = (column) => {
  const index = columnSettings.findIndex(c => c.key === column.key);
  if (index !== -1) {
    columnSettings[index].visible = !columnSettings[index].visible;
  }
};

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return '-';
  return new Date(timeString).toLocaleString('zh-CN');
};

// 表格高度自适应
const calculateTableHeight = () => {
  const windowHeight = window.innerHeight;
  const navbarHeight = 60;
  const pageHeaderHeight = 80;
  const actionBarHeight = 70;
  const paginationHeight = 60;
  const padding = 40;
  
  const availableHeight = windowHeight - navbarHeight - pageHeaderHeight - actionBarHeight - paginationHeight - padding;
  tableHeight.value = Math.max(availableHeight, 400);
};

const resizeObserver = new ResizeObserver(calculateTableHeight);

onMounted(() => {
  fetchDiscussions();
  calculateTableHeight();
  
  window.addEventListener('resize', calculateTableHeight);
  
  const contentContainer = document.querySelector('.content-container');
  if (contentContainer) {
    resizeObserver.observe(contentContainer);
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight);
  resizeObserver.disconnect();
});
</script>

<template>
  <div class="discussion-management">
    <div class="page-header">
      <h1 class="page-title">作品讨论区管理</h1>
      <p class="page-subtitle">管理系统中的作品评论和讨论</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
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
          placeholder="按作品名称搜索"
          class="search-input rounded-input"
          allow-clear
        />
        <a-button type="primary" class="search-btn" @click="searchDiscussion">
          查询
        </a-button>
        <a-button class="reset-btn" @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>
    
    <div class="table-container">
      <a-table 
        :dataSource="discussions" 
        :pagination="false"
        :loading="loading"
        @change="handleTableChange"
        class="discussion-table"
        row-key="id"
        :scroll="{ y: tableHeight }"
      >
        <!-- 动态显示列 -->
        <a-table-column 
          v-for="column in visibleColumns" 
          :key="column.key" 
          :title="column.title" 
          :data-index="column.key"
        >
          <template #default="{ record }">
            <template v-if="column.key === 'comment_content'">
              <div class="comment-cell">
                {{ record.content || '-' }}
              </div>
            </template>
            <template v-else-if="column.key === 'showcase_name'">
              <div class="showcase-name-cell">
                {{ record.showcase_name || '-' }}
              </div>
            </template>
            <template v-else-if="column.key === 'author_name'">
              {{ record.author_name || '-' }}
            </template>
            <template v-else-if="column.key === 'reply_count'">
              <a-badge :count="record.reply_count || 0" />
            </template>
            <template v-else-if="column.key === 'created_at'">
              {{ formatTime(record.created_at) }}
            </template>
            <template v-else>
              {{ record[column.key] || '-' }}
            </template>
          </template>
        </a-table-column>
        
        <!-- 操作列 -->
        <a-table-column key="action" title="操作" width="150" fixed="right">
          <template #default="{ record }">
            <div class="action-buttons">
              <a-button size="small" @click="viewDiscussion(record.id)">
                <template #icon><EyeOutlined /></template>
                查看
              </a-button>
              <a-button size="small" danger @click="deleteDiscussion(record.id)">
                <template #icon><DeleteOutlined /></template>
                删除
              </a-button>
            </div>
          </template>
        </a-table-column>
      </a-table>
      
      <!-- 分页组件 -->
      <div class="pagination-container">
        <a-pagination
          v-model:current="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :show-size-changer="pagination.showSizeChanger"
          :show-quick-jumper="pagination.showQuickJumper"
          :show-total="pagination.showTotal"
          @change="handleTableChange"
        />
      </div>
    </div>

    <!-- 列设置抽屉 -->
    <a-drawer
      v-model:open="columnSettingsVisible"
      title="列设置"
      width="300"
      placement="right"
    >
      <div class="column-settings">
        <div v-for="column in availableColumns" :key="column.key" class="column-item">
          <a-checkbox 
            :checked="columnSettings.find(c => c.key === column.key)?.visible"
            @change="() => handleColumnSettingChange(column)"
          >
            {{ column.title }}
          </a-checkbox>
        </div>
      </div>
    </a-drawer>

    <!-- 讨论详情抽屉 -->
    <a-drawer
      v-model:open="discussionDetailDrawerVisible"
      title="讨论详情"
      width="600"
      placement="left"
      :maskClosable="true"
    >
      <div v-if="discussionDetail" class="discussion-detail">
        <div class="detail-section">
          <h4>作品信息</h4>
          <p>作品名称: {{ discussionDetail.showcase_name }}</p>
        </div>
        
        <div class="detail-section">
          <h4>评论信息</h4>
          <p>评论者: {{ discussionDetail.author_name }}</p>
          <p>评论时间: {{ formatTime(discussionDetail.created_at) }}</p>
          <p>评论内容:</p>
          <div class="comment-content">
            {{ discussionDetail.content }}
          </div>
        </div>

        <div class="detail-section" v-if="discussionDetail.replies && discussionDetail.replies.length > 0">
          <h4>回复列表 ({{ discussionDetail.replies.length }})</h4>
          <div class="replies-list">
            <div v-for="reply in discussionDetail.replies" :key="reply.id" class="reply-item">
              <div class="reply-header">
                <strong>{{ reply.author_name }}</strong>
                <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
              </div>
              <div class="reply-content">{{ reply.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </a-drawer>
  </div>
</template>

<style scoped>
.discussion-management {
  padding: 24px;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #1a1a1a;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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

.table-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.comment-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.showcase-name-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.pagination-container {
  padding: 16px;
  display: flex;
  justify-content: flex-end;
  background-color: #fafafa;
}

/* 抽屉样式 */
.column-settings {
  padding: 16px 0;
}

.column-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.column-item:last-child {
  border-bottom: none;
}

.discussion-detail {
  padding: 16px 0;
}

.detail-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.detail-section p {
  margin: 8px 0;
  color: #666;
}

.comment-content {
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  white-space: pre-wrap;
  word-break: break-word;
}

.replies-list {
  max-height: 400px;
  overflow-y: auto;
}

.reply-item {
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  margin-bottom: 8px;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.reply-time {
  font-size: 12px;
  color: #999;
}

.reply-content {
  white-space: pre-wrap;
  word-break: break-word;
  color: #333;
}

/* 表格样式 */
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
  padding: 8px 8px;
  border-bottom: 1px solid #f8f8f8;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background-color: #f5f5f5;
}
</style>