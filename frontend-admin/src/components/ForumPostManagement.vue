<script setup>
import { ref, onMounted, reactive, computed, watch, onUnmounted, h } from 'vue';
import { SearchOutlined, MessageOutlined, DeleteOutlined, SettingOutlined, EyeOutlined, UserOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import request from '../utils/request';

const posts = ref([]);
const loading = ref(false);
const searchValue = ref('');
const expandedRowKeys = ref([]); // 展开的行keys
const postDetails = ref({}); // 存储每个帖子的详细信息
const postReplies = ref({}); // 存储每个帖子的回复数据
const loadingDetails = ref(new Set()); // 正在加载详情的帖子UUID集合
const loadingReplies = ref(new Set()); // 正在加载回复的帖子UUID集合

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
});

// 列设置
const columnSettingsVisible = ref(false);
const availableColumns = [
  { key: 'title', title: '帖子标题', visible: true },
  { key: 'category_name', title: '分类名称', visible: true },
  { key: 'author_name', title: '发帖者', visible: true },
  { key: 'reply_count', title: '回复数', visible: true },
  { key: 'views_count', title: '浏览数', visible: true },
  { key: 'is_pinned', title: '是否置顶', visible: true },
  { key: 'created_at', title: '发帖时间', visible: true },
];
const columnSettings = reactive([...availableColumns]);

// 表格高度自适应
const tableHeight = ref(600);

const API_BASE_URL = 'http://localhost:8000/api/v1/admin/forum/posts';

const fetchPosts = async (page = 1, pageSize = 20, search = '') => {
  loading.value = true;
  try {
    const skip = (page - 1) * pageSize;
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: pageSize.toString()
    });
    
    if (search) {
      params.append('title', search);
    }

    const response = await request.get(`${API_BASE_URL}?${params}`);
    
    if (response.data.code === 200) {
      posts.value = response.data.data.items;
      pagination.total = response.data.data.total;
      pagination.current = page;
      pagination.pageSize = pageSize;
    } else {
      message.error(response.data.message || '获取帖子列表失败');
    }
  } catch (error) {
    console.error('Failed to fetch posts:', error);
    message.error('获取帖子列表失败');
  } finally {
    loading.value = false;
  }
};

const refreshList = () => {
  fetchPosts(pagination.current, pagination.pageSize, searchValue.value);
};

const searchPost = () => {
  fetchPosts(1, pagination.pageSize, searchValue.value);
};

const resetSearch = () => {
  searchValue.value = '';
  fetchPosts(1, pagination.pageSize, '');
};

const handleTableChange = (paginationInfo) => {
  fetchPosts(paginationInfo.current, paginationInfo.pageSize, searchValue.value);
};


// 加载帖子详情
const loadPostDetails = async (postUuid) => {
  if (loadingDetails.value.has(postUuid)) return;
  
  console.log('开始加载帖子详情:', postUuid);
  loadingDetails.value.add(postUuid);
  try {
    // 使用普通用户的API端点获取详情
    const response = await request.get(`http://localhost:8000/api/v1/forum/posts/${postUuid}`);
    console.log('帖子详情API响应:', response.data);
    
    if (response.data.code === 200) {
      postDetails.value[postUuid] = response.data.data;
      console.log('帖子详情加载成功:', postDetails.value[postUuid]);
    } else {
      postDetails.value[postUuid] = null;
      console.log('帖子详情API返回错误:', response.data.message);
    }
  } catch (error) {
    console.error('Failed to load post details:', error);
    postDetails.value[postUuid] = null;
  } finally {
    loadingDetails.value.delete(postUuid);
  }
};

// 加载帖子回复
const loadPostReplies = async (postUuid) => {
  if (loadingReplies.value.has(postUuid)) return;
  
  console.log('开始加载帖子回复:', postUuid);
  loadingReplies.value.add(postUuid);
  try {
    // 使用forum reply API获取帖子的回复列表
    const response = await request.get(`http://localhost:8000/api/v1/forum/replies/post/${postUuid}/tree`);
    console.log('帖子回复API响应:', response.data);
    
    if (response.data.code === 200) {
      postReplies.value[postUuid] = response.data.data;
      console.log('帖子回复加载成功:', postReplies.value[postUuid]);
    } else {
      postReplies.value[postUuid] = [];
      console.log('帖子回复API返回错误:', response.data.message);
    }
  } catch (error) {
    console.error('Failed to load post replies:', error);
    postReplies.value[postUuid] = [];
  } finally {
    loadingReplies.value.delete(postUuid);
  }
};

// 删除帖子
const deletePost = (postUuid) => {
  const post = posts.value.find(p => p.uuid === postUuid);
  
  Modal.confirm({
    title: '确认删除帖子',
    content: `确定要删除帖子"${post?.title || ''}"吗？此操作不可恢复！`,
    okType: 'danger',
    onOk: async () => {
      try {
        const response = await request.delete(`${API_BASE_URL}/${postUuid}`);
        
        if (response.data.code === 200) {
          message.success('帖子删除成功');
          refreshList();
        } else {
          message.error(response.data.message || '删除失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('删除帖子失败');
        }
      }
    }
  });
};

// 切换置顶状态
const togglePin = (postUuid) => {
  const post = posts.value.find(p => p.uuid === postUuid);
  const action = post?.is_pinned ? '取消置顶' : '设为置顶';
  
  Modal.confirm({
    title: `确认${action}`,
    content: `确定要${action}这个帖子吗？`,
    onOk: async () => {
      try {
        const response = await request.post(`${API_BASE_URL}/${postUuid}/pin?pinned=${!post?.is_pinned}`);
        
        if (response.data.code === 200) {
          message.success(`${action}成功`);
          refreshList();
        } else {
          message.error(response.data.message || `${action}失败`);
        }
      } catch (error) {
        message.error(`${action}失败`);
      }
    }
  });
};

// 删除回复
const deleteReply = (postUuid, replyUuid) => {
  Modal.confirm({
    title: '确认删除回复',
    content: '确定要删除这条回复吗？此操作不可恢复！',
    okType: 'danger',
    onOk: async () => {
      try {
        const response = await request.delete(`http://localhost:8000/api/v1/admin/forum/replies/${replyUuid}`);
        
        if (response.data.code === 200) {
          message.success('回复删除成功');
          // 重新加载该帖子的回复
          await loadPostReplies(postUuid);
          // 刷新帖子列表以更新回复数量
          refreshList();
        } else {
          message.error(response.data.message || '删除失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('删除回复失败');
        }
      }
    }
  });
};

// 表格展开行处理
const handleExpand = async (expanded, record) => {
  if (expanded) {
    // 加载详情和回复
    if (!postDetails.value[record.uuid]) {
      await loadPostDetails(record.uuid);
    }
    if (!postReplies.value[record.uuid]) {
      await loadPostReplies(record.uuid);
    }
  }
};

// 手动控制表格展开/折叠
const toggleTableExpansion = async (postUuid) => {
  const index = expandedRowKeys.value.indexOf(postUuid);
  if (index > -1) {
    // 折叠
    expandedRowKeys.value.splice(index, 1);
  } else {
    // 展开
    expandedRowKeys.value.push(postUuid);
    // 触发数据加载
    const record = posts.value.find(p => p.uuid === postUuid);
    if (record) {
      await handleExpand(true, record);
    }
  }
};

// 展开行渲染函数
const expandedRowRender = (record, index, indent, expanded) => {
  // 真正的数据在 record.record 里面！
  const actualRecord = record.record;
  const postUuid = actualRecord?.uuid;
  
  console.log('修正后的 postUuid:', postUuid);
  console.log('修正后的 actualRecord:', actualRecord);
  
  const detail = postDetails.value[postUuid];
  const replies = postReplies.value[postUuid] || [];
  const isLoadingDetails = loadingDetails.value.has(postUuid);
  const isLoadingReplies = loadingReplies.value.has(postUuid);

  console.log('展开行渲染 - postUuid:', postUuid);
  console.log('详情数据:', detail);
  console.log('回复数据:', replies);
  console.log('加载状态 - 详情:', isLoadingDetails, '回复:', isLoadingReplies);

  return h('div', { class: 'post-detail-card', style: 'padding: 20px; background: white; margin: 12px; border-radius: 8px;' }, [
    // 帖子详细信息
    h('div', { class: 'post-header' }, [
      h('h3', { style: 'margin: 0 0 12px 0; font-size: 18px;' }, detail?.title || actualRecord.title),
      h('div', { class: 'post-meta', style: 'margin-bottom: 16px;' }, [
        h('span', { style: 'margin-right: 16px;' }, `分类：${detail?.category?.name || actualRecord.category?.name || '-'}`),
        h('span', { style: 'margin-right: 16px;' }, `发帖者：${detail?.author?.username || actualRecord.author?.username || '-'}`),
        h('span', { style: 'margin-right: 16px;' }, `发帖时间：${formatTime(detail?.created_at || actualRecord.created_at)}`),
        h('span', { style: 'margin-right: 16px;' }, `浏览数：${detail?.view_count || actualRecord.view_count || 0}`),
        h('span', {}, `置顶状态：${(detail?.is_pinned ?? actualRecord.is_pinned) ? '已置顶' : '普通'}`),
      ])
    ]),
    
    // 帖子内容
    h('div', { class: 'post-content', style: 'margin-bottom: 24px;' }, [
      h('h4', { style: 'margin: 0 0 8px 0;' }, '帖子内容：'),
      isLoadingDetails 
        ? h('div', { class: 'loading-content' }, '加载内容中...')
        : h('div', { 
            class: 'content-text',
            style: 'padding: 12px; background: #f5f5f5; border-radius: 6px; white-space: pre-wrap;'
          }, detail?.content || '暂无内容')
    ]),
    
    // 回复列表
    h('div', { class: 'replies-section' }, [
      h('h4', { style: 'margin: 0 0 16px 0;' }, `回复列表 (${actualRecord.reply_count || 0})`),
      isLoadingReplies 
        ? h('div', { class: 'loading-replies' }, '加载回复中...')
        : replies.length > 0
          ? (() => {
              const flattened = flattenReplies(replies);
              console.log('原始回复数据:', replies);
              console.log('扁平化后回复数据:', flattened);
              return h('div', { class: 'replies-list' }, 
                flattened.map(reply => renderReply(reply, postUuid))
              );
            })()
          : h('div', { class: 'no-replies', style: 'padding: 20px; text-align: center; color: #999;' }, '暂无回复')
    ])
  ]);
};

// 扁平化回复数据，将无限层级转换为两层显示
const flattenReplies = (replies, level = 0, parentInfo = null) => {
  const result = [];
  
  for (const reply of replies) {
    if (level === 0) {
      // 一级回复，正常显示
      result.push({
        ...reply,
        level: 0,
        parentInfo: null
      });
      
      // 递归处理子回复
      if (reply.children && reply.children.length > 0) {
        result.push(...flattenReplies(reply.children, 1, {
          author: reply.author?.username || '-',
          uuid: reply.uuid
        }));
      }
    } else {
      // 二级及以上回复，平铺显示
      result.push({
        ...reply,
        level: 1,
        parentInfo: parentInfo
      });
      
      // 三级及以上回复继续平铺
      if (reply.children && reply.children.length > 0) {
        result.push(...flattenReplies(reply.children, 1, {
          author: reply.author?.username || '-',
          uuid: reply.uuid
        }));
      }
    }
  }
  
  return result;
};

// 渲染单个回复（支持平铺显示）
const renderReply = (reply, postUuid) => {
  const isSecondLevel = reply.level === 1;
  const baseStyle = isSecondLevel 
    ? 'padding: 10px; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #007bff; margin-bottom: 8px;'
    : 'padding: 12px; background: #fff; border-radius: 6px; border: 1px solid #e8e8e8; margin-bottom: 12px;';

  const headerContent = [
    h('div', { class: 'reply-author' }, [
      h('span', { style: 'margin-right: 8px;' }, isSecondLevel ? '↳ 👤' : '👤'),
      h('strong', {}, reply.author?.username || '-'),
      // 如果是回复某人，显示回复对象
      isSecondLevel && reply.parentInfo 
        ? h('span', { style: 'margin-left: 8px; color: #666; font-size: 12px;' }, `回复 @${reply.parentInfo.author}`)
        : null,
      h('span', { 
        class: 'reply-time', 
        style: 'margin-left: 8px; font-size: 12px; color: #999;' 
      }, formatTime(reply.created_at))
    ]),
    h('button', {
      style: 'background: none; border: none; color: red; cursor: pointer; padding: 4px;',
      onClick: () => deleteReply(postUuid, reply.uuid)
    }, '🗑️')
  ];

  return h('div', { 
    key: reply.uuid, 
    class: 'reply-item',
    style: baseStyle
  }, [
    h('div', { 
      class: 'reply-header',
      style: 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0;'
    }, headerContent),
    h('div', { 
      class: 'reply-content',
      style: 'white-space: pre-wrap; word-break: break-word; color: #333; line-height: 1.6;'
    }, reply.content)
  ]);
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
  fetchPosts();
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
  <div class="post-management">
    <div class="page-header">
      <h1 class="page-title">论坛帖子管理</h1>
      <p class="page-subtitle">管理系统中的论坛帖子和回复</p>
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
          placeholder="按帖子标题搜索"
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
    
    <div class="table-container">
      <a-table 
        :dataSource="posts" 
        :pagination="false"
        :loading="loading"
        @change="handleTableChange"
        @expand="handleExpand"
        class="post-table"
        row-key="uuid"
        :scroll="{ y: tableHeight }"
        :expandedRowKeys="expandedRowKeys"
        :expandedRowRender="expandedRowRender"
      >
        <!-- 动态显示列 -->
        <a-table-column 
          v-for="column in visibleColumns" 
          :key="column.key" 
          :title="column.title" 
          :data-index="column.key"
        >
          <template #default="{ record }">
            <template v-if="column.key === 'title'">
              <div class="title-cell">
                <a @click="toggleTableExpansion(record.uuid)">{{ record.title || '-' }}</a>
              </div>
            </template>
            <template v-else-if="column.key === 'category_name'">
              <a-tag color="blue">{{ record.category?.name || '-' }}</a-tag>
            </template>
            <template v-else-if="column.key === 'author_name'">
              <div class="author-cell">
                <UserOutlined style="margin-right: 4px;" />
                {{ record.author?.username || '-' }}
              </div>
            </template>
            <template v-else-if="column.key === 'reply_count'">
              <a-badge :count="record.reply_count || 0" />
            </template>
            <template v-else-if="column.key === 'views_count'">
              <span>{{ record.view_count || 0 }}</span>
            </template>
            <template v-else-if="column.key === 'is_pinned'">
              <a-tag :color="record.is_pinned ? 'red' : 'default'">
                {{ record.is_pinned ? '已置顶' : '普通' }}
              </a-tag>
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
              <a-button 
                size="small" 
                :type="record.is_pinned ? 'default' : 'primary'" 
                @click="togglePin(record.uuid)"
              >
                {{ record.is_pinned ? '取消置顶' : '置顶' }}
              </a-button>
              <a-button size="small" danger @click="deletePost(record.uuid)">
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

  </div>
</template>

<style scoped>
.post-management {
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

.title-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.title-cell a {
  color: #1890ff;
  text-decoration: none;
}

.title-cell a:hover {
  color: #40a9ff;
}

.author-cell {
  display: flex;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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

.post-detail {
  padding: 16px 0;
}

.detail-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.detail-section h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #666;
  font-size: 14px;
}

.post-content {
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.replies-list {
  max-height: 500px;
  overflow-y: auto;
}

.reply-item {
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  margin-bottom: 12px;
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
  line-height: 1.6;
}

.sub-replies {
  margin-top: 12px;
  margin-left: 20px;
  padding-left: 12px;
  border-left: 2px solid #e8e8e8;
}

.sub-reply-item {
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
  margin-bottom: 8px;
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

/* 展开帖子样式 */
.loading-content {
  padding: 20px;
  text-align: center;
  color: #666;
}

.post-detail-card {
  padding: 20px;
  background: white;
  margin: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.post-header h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
}

.post-content {
  margin-bottom: 24px;
}

.post-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.content-text {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.replies-section {
  border-top: 1px solid #f0f0f0;
  padding-top: 20px;
}

.replies-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.loading-replies {
  padding: 20px;
  text-align: center;
  color: #666;
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
  margin-bottom: 12px;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.reply-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reply-time {
  font-size: 12px;
  color: #999;
  margin-left: 8px;
}

.reply-content {
  white-space: pre-wrap;
  word-break: break-word;
  color: #333;
  line-height: 1.6;
}

.sub-replies {
  margin-top: 12px;
  margin-left: 20px;
  padding-left: 12px;
  border-left: 2px solid #e8e8e8;
}

.sub-reply-item {
  padding: 8px 12px;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
  margin-bottom: 8px;
}

.no-replies {
  padding: 20px;
  text-align: center;
  color: #999;
  font-style: italic;
}
</style>