<script setup>
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined, TagOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import request from '../utils/request';

const blogs = ref([]);
const loading = ref(false);
const searchValue = ref('');
const statusFilter = ref('');
const tagFilter = ref([]);

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
});

const editDrawerVisible = ref(false);
const editingBlog = ref(null);
const editForm = reactive({
  title: '',
  content: '',
  summary: '',
  cover_url: '',
  status: 'draft',
  tag_ids: []
});

// 添加博客抽屉
const addBlogDrawerVisible = ref(false);
const addBlogForm = reactive({
  title: '',
  content: '',
  summary: '',
  cover_url: '',
  status: 'draft',
  tag_ids: []
});

// 博客详情抽屉
const blogDetailDrawerVisible = ref(false);
const blogDetail = ref(null);

// 标签管理
const tags = ref([]);
const tagModalVisible = ref(false);
const newTagName = ref('');

// 列设置
const columnSettingsVisible = ref(false);
const availableColumns = [
  { key: 'title', title: '标题', visible: true },
  { key: 'author', title: '作者', visible: true },
  { key: 'status', title: '状态', visible: true },
  { key: 'tags', title: '标签', visible: true },
  { key: 'view_count', title: '浏览量', visible: true },
  { key: 'created_at', title: '创建时间', visible: true },
  { key: 'updated_at', title: '更新时间', visible: false }
];
const columnSettings = reactive([...availableColumns]);

// 当前用户信息（用于权限控制）
const currentUser = ref(null);

// 表格高度自适应
const tableHeight = ref(600);

const API_BASE_URL = 'http://localhost:8000/api/v1/blogs';

// 状态选项
const statusOptions = [
  { label: '全部', value: '' },
  { label: '草稿', value: 'draft' },
  { label: '已发布', value: 'published' },
  { label: '已归档', value: 'archived' }
];

const fetchBlogs = async (page = 1, pageSize = 20) => {
  loading.value = true;
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      size: pageSize.toString()
    });

    if (searchValue.value) {
      params.append('keyword', searchValue.value);
    }
    if (statusFilter.value) {
      params.append('status', statusFilter.value);
    }
    if (tagFilter.value.length > 0) {
      tagFilter.value.forEach(tagId => {
        params.append('tag_ids', tagId.toString());
      });
    }

    const response = await request.get(`${API_BASE_URL}/search?${params.toString()}`);

    if (response.data.code === 200) {
      const data = response.data.data;
      blogs.value = data.items || [];
      pagination.total = data.total || 0;
      pagination.current = page;
    } else {
      message.error(response.data.message || '获取博客列表失败');
    }
  } catch (error) {
    console.error('Failed to fetch blogs:', error);
    if (error.response?.status === 403) {
      message.error('权限不足，需要管理员权限');
    } else {
      message.error('获取博客列表失败');
    }
  } finally {
    loading.value = false;
  }
};

// 获取标签列表
const fetchTags = async () => {
  try {
    const response = await request.get(`${API_BASE_URL}/tags`);
    if (response.data.code === 200) {
      tags.value = response.data.data || [];
    }
  } catch (error) {
    console.error('获取标签列表失败:', error);
  }
};

const addNewBlog = () => {
  // 重置表单
  Object.assign(addBlogForm, {
    title: '',
    content: '',
    summary: '',
    cover_url: '',
    status: 'draft',
    tag_ids: []
  });
  addBlogDrawerVisible.value = true;
};

const refreshList = () => {
  fetchBlogs(pagination.current, pagination.pageSize);
};

const configSettings = () => {
  columnSettingsVisible.value = true;
};

const searchBlog = () => {
  pagination.current = 1;
  fetchBlogs(1, pagination.pageSize);
};

const resetSearch = () => {
  searchValue.value = '';
  statusFilter.value = '';
  tagFilter.value = [];
  pagination.current = 1;
  fetchBlogs(1, pagination.pageSize);
};

const handleTableChange = (page, pageSize) => {
  pagination.current = page;
  pagination.pageSize = pageSize;
  fetchBlogs(page, pageSize);
};

const viewBlog = async (blogUuid) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${blogUuid}`);
    
    if (response.data.code === 200) {
      blogDetail.value = response.data.data;
      blogDetailDrawerVisible.value = true;
    }
  } catch (error) {
    message.error('获取博客详情失败');
  }
};

const editBlog = async (blogUuid) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${blogUuid}`);
    
    if (response.data.code === 200) {
      const blog = response.data.data;
      editingBlog.value = blog;
      editForm.title = blog.title;
      editForm.content = blog.content;
      editForm.summary = blog.summary || '';
      editForm.cover_url = blog.cover_url || '';
      editForm.status = blog.status;
      editForm.tag_ids = blog.tags ? blog.tags.map(tag => tag.id) : [];
      editDrawerVisible.value = true;
    }
  } catch (error) {
    message.error('获取博客信息失败');
  }
};

const handleEditSubmit = async () => {
  try {
    const response = await request.put(`${API_BASE_URL}/${editingBlog.value.uuid}`, editForm);
    
    if (response.data.code === 200) {
      message.success('博客更新成功');
      editDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '更新失败');
    }
  } catch (error) {
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('更新博客失败');
    }
  }
};

const deleteBlog = (blogUuid) => {
  const blog = blogs.value.find(b => b.uuid === blogUuid);
  
  Modal.confirm({
    title: '确认删除博客',
    content: `确定要删除博客 "${blog.title}" 吗？此操作不可恢复！`,
    okType: 'danger',
    onOk: async () => {
      try {
        const response = await request.delete(`${API_BASE_URL}/${blogUuid}`);
        
        if (response.data.code === 200) {
          message.success('博客删除成功');
          refreshList();
        } else {
          message.error(response.data.message || '删除失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('删除博客失败');
        }
      }
    }
  });
};

// 添加博客
const handleAddBlog = async () => {
  try {
    const response = await request.post(API_BASE_URL, {
      ...addBlogForm,
      author_id: currentUser.value?.id
    });
    
    if (response.data.code === 200) {
      message.success('博客创建成功');
      addBlogDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '创建失败');
    }
  } catch (error) {
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('创建博客失败');
    }
  }
};

// 创建标签
const createTag = async () => {
  if (!newTagName.value.trim()) {
    message.warning('请输入标签名称');
    return;
  }

  try {
    const response = await request.post(`${API_BASE_URL}/tags`, {
      name: newTagName.value.trim()
    });
    
    if (response.data.code === 200) {
      message.success('标签创建成功');
      newTagName.value = '';
      await fetchTags();
    } else {
      message.error(response.data.message || '创建标签失败');
    }
  } catch (error) {
    console.error('创建标签失败:', error);
    message.error('创建标签失败');
  }
};

// 打开标签管理
const openTagManagement = () => {
  tagModalVisible.value = true;
};

// 获取当前用户信息
const fetchCurrentUser = async () => {
  try {
    const response = await request.get('http://localhost:8000/api/v1/auth/me');
    
    if (response.data.code === 200) {
      currentUser.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to fetch current user:', error);
  }
};

// 应用列设置
const applyColumnSettings = () => {
  columnSettingsVisible.value = false;
  message.success('列设置已应用');
};

// 重置列设置
const resetColumnSettings = () => {
  columnSettings.splice(0, columnSettings.length, ...availableColumns.map(col => ({ ...col })));
};

// 计算可见列
const visibleColumns = computed(() => {
  return columnSettings.filter(col => col.visible);
});

// 格式化显示值
const formatColumnValue = (record, column) => {
  if (column.key === 'status') {
    const statusMap = {
      draft: '草稿',
      published: '已发布',
      archived: '已归档'
    };
    return statusMap[record.status] || record.status;
  } else if (column.key === 'author') {
    return record.author?.real_name || record.author?.username || '未知';
  } else if (column.key === 'tags') {
    return record.tags && record.tags.length > 0 ? record.tags.map(tag => tag.name).join(', ') : '无标签';
  } else if (column.key === 'created_at' || column.key === 'updated_at') {
    return new Date(record[column.key]).toLocaleString('zh-CN');
  } else {
    return record[column.key] || '-';
  }
};

// 计算表格高度 - 使用CSS flex布局自动填满剩余高度
const calculateTableHeight = () => {
  // 让CSS处理高度，这里只需要设置一个合理的最小值
  tableHeight.value = 'auto';
};

// 监听窗口大小变化和数据变化
const resizeObserver = new ResizeObserver(calculateTableHeight);

onMounted(() => {
  fetchBlogs();
  fetchTags();
  fetchCurrentUser();
  calculateTableHeight();
  
  // 监听窗口大小变化
  window.addEventListener('resize', calculateTableHeight);
  
  // 监听侧边栏容器的大小变化
  const contentContainer = document.querySelector('.content-container');
  if (contentContainer) {
    resizeObserver.observe(contentContainer);
  }
});

// 清理事件监听
onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight);
  resizeObserver.disconnect();
});
</script>

<template>
  <div class="blog-management">
    <div class="page-header">
      <h1 class="page-title">博客管理</h1>
      <p class="page-subtitle">管理系统中的所有博客文章，包括创建、编辑、发布和删除操作</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="addNewBlog">
          <template #icon><PlusOutlined /></template>
          新建博客
        </a-button>
        <a-button class="refresh-btn" @click="refreshList">
          刷新
        </a-button>
        <a-button class="settings-btn" @click="configSettings">
          <template #icon><SettingOutlined /></template>
          列设置
        </a-button>
        <a-button class="tag-btn" @click="openTagManagement">
          <template #icon><TagOutlined /></template>
          标签管理
        </a-button>
      </div>
      
      <div class="right-actions">
        <a-input 
          v-model:value="searchValue"
          placeholder="搜索博客标题或摘要"
          class="search-input rounded-input"
          allow-clear
        />
        <a-select
          v-model:value="statusFilter"
          placeholder="状态筛选"
          class="status-select"
          allow-clear
        >
          <a-select-option
            v-for="option in statusOptions.slice(1)"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </a-select-option>
        </a-select>
        <a-select
          v-model:value="tagFilter"
          mode="multiple"
          placeholder="标签筛选"
          class="tag-select"
          :options="tags.map(tag => ({ label: tag.name, value: tag.id }))"
        />
        <a-button type="primary" class="search-btn" @click="searchBlog">
          查询
        </a-button>
        <a-button class="reset-btn" @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>
    
    <div class="table-container">
      <a-table 
        :dataSource="blogs" 
        :pagination="false"
        :loading="loading"
        @change="handleTableChange"
        class="blog-table"
        row-key="id"
        :scroll="{ y: tableHeight }"
      >
      <!-- 动态显示列 -->
      <a-table-column 
        v-for="column in visibleColumns" 
        :key="column.key" 
        :title="column.title" 
        :data-index="column.key"
        :width="column.key === 'title' ? 200 : column.key === 'content' ? 300 : undefined"
      >
        <template #default="{ record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'published' ? 'green' : record.status === 'draft' ? 'orange' : 'gray'">
              {{ formatColumnValue(record, column) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'tags'">
            <div v-if="record.tags && record.tags.length > 0">
              <a-tag v-for="tag in record.tags.slice(0, 2)" :key="tag.id" size="small">
                {{ tag.name }}
              </a-tag>
              <span v-if="record.tags.length > 2">...</span>
            </div>
            <span v-else>无标签</span>
          </template>
          <template v-else-if="column.key === 'title'">
            <div style="max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" :title="record.title">
              {{ record.title }}
            </div>
          </template>
          <template v-else-if="column.key === 'created_at' || column.key === 'updated_at'">
            {{ new Date(record[column.key]).toLocaleString('zh-CN') }}
          </template>
          <template v-else>
            {{ formatColumnValue(record, column) }}
          </template>
        </template>
      </a-table-column>
      
      <!-- 操作列 -->
      <a-table-column key="action" title="操作" width="200" fixed="right">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewBlog(record.uuid)">查看</a-button>
            <a-button size="small" type="primary" @click="editBlog(record.uuid)">编辑</a-button>
            <a-button 
              size="small" 
              danger 
              @click="deleteBlog(record.uuid)"
            >
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
        @showSizeChange="handleTableChange"
      />
    </div>
  </div>

    <!-- 编辑博客抽屉 -->
    <a-drawer
      v-model:open="editDrawerVisible"
      title="编辑博客"
      width="800"
      placement="left"
      @close="editDrawerVisible = false"
      :maskClosable="true"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="标题" required>
          <a-input v-model:value="editForm.title" placeholder="请输入博客标题" />
        </a-form-item>
        <a-form-item label="摘要">
          <a-textarea 
            v-model:value="editForm.summary" 
            placeholder="请输入博客摘要"
            :rows="3"
          />
        </a-form-item>
        <a-form-item label="封面图片">
          <a-input v-model:value="editForm.cover_url" placeholder="请输入封面图片URL" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="editForm.status">
            <a-select-option value="draft">草稿</a-select-option>
            <a-select-option value="published">已发布</a-select-option>
            <a-select-option value="archived">已归档</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="标签">
          <a-select
            v-model:value="editForm.tag_ids"
            mode="multiple"
            placeholder="选择标签"
            :options="tags.map(tag => ({ label: tag.name, value: tag.id }))"
          />
        </a-form-item>
        <a-form-item label="内容" required>
          <a-textarea 
            v-model:value="editForm.content" 
            placeholder="请输入博客内容"
            :rows="15"
          />
        </a-form-item>
      </a-form>
      
      <template #footer>
        <div style="text-align: right;">
          <a-button @click="editDrawerVisible = false" style="margin-right: 8px;">
            取消
          </a-button>
          <a-button type="primary" @click="handleEditSubmit">
            确定
          </a-button>
        </div>
      </template>
    </a-drawer>

    <!-- 添加博客抽屉 -->
    <a-drawer
      v-model:open="addBlogDrawerVisible"
      title="新建博客"
      width="800"
      placement="left"
      @close="addBlogDrawerVisible = false"
      :maskClosable="true"
    >
      <a-form :model="addBlogForm" layout="vertical">
        <a-form-item label="标题" required>
          <a-input v-model:value="addBlogForm.title" placeholder="请输入博客标题" />
        </a-form-item>
        <a-form-item label="摘要">
          <a-textarea 
            v-model:value="addBlogForm.summary" 
            placeholder="请输入博客摘要"
            :rows="3"
          />
        </a-form-item>
        <a-form-item label="封面图片">
          <a-input v-model:value="addBlogForm.cover_url" placeholder="请输入封面图片URL" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="addBlogForm.status">
            <a-select-option value="draft">草稿</a-select-option>
            <a-select-option value="published">已发布</a-select-option>
            <a-select-option value="archived">已归档</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="标签">
          <a-select
            v-model:value="addBlogForm.tag_ids"
            mode="multiple"
            placeholder="选择标签"
            :options="tags.map(tag => ({ label: tag.name, value: tag.id }))"
          />
        </a-form-item>
        <a-form-item label="内容" required>
          <a-textarea 
            v-model:value="addBlogForm.content" 
            placeholder="请输入博客内容"
            :rows="15"
          />
        </a-form-item>
      </a-form>
      
      <template #footer>
        <div style="text-align: right;">
          <a-button @click="addBlogDrawerVisible = false" style="margin-right: 8px;">
            取消
          </a-button>
          <a-button type="primary" @click="handleAddBlog">
            确定
          </a-button>
        </div>
      </template>
    </a-drawer>

    <!-- 博客详情抽屉 -->
    <a-drawer
      v-model:open="blogDetailDrawerVisible"
      title="博客详情"
      width="800"
      placement="left"
      :maskClosable="true"
    >
      <div v-if="blogDetail" class="blog-detail">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="标题">
            {{ blogDetail.title }}
          </a-descriptions-item>
          <a-descriptions-item label="作者">
            {{ blogDetail.author?.real_name || blogDetail.author?.username || '未知' }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="blogDetail.status === 'published' ? 'green' : blogDetail.status === 'draft' ? 'orange' : 'gray'">
              {{ blogDetail.status === 'published' ? '已发布' : blogDetail.status === 'draft' ? '草稿' : '归档' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="浏览量">
            {{ blogDetail.view_count || 0 }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ new Date(blogDetail.created_at).toLocaleString('zh-CN') }}
          </a-descriptions-item>
          <a-descriptions-item label="标签">
            <a-tag v-for="tag in blogDetail.tags" :key="tag.id" size="small">
              {{ tag.name }}
            </a-tag>
            <span v-if="!blogDetail.tags || blogDetail.tags.length === 0">无标签</span>
          </a-descriptions-item>
          <a-descriptions-item label="摘要">
            {{ blogDetail.summary || '无摘要' }}
          </a-descriptions-item>
          <a-descriptions-item label="内容">
            <div style="max-height: 400px; overflow-y: auto; white-space: pre-wrap; background: #f5f5f5; padding: 12px; border-radius: 4px;">
              {{ blogDetail.content }}
            </div>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-drawer>

    <!-- 标签管理模态框 -->
    <a-modal
      v-model:open="tagModalVisible"
      title="标签管理"
      width="600"
    >
      <div class="tag-management">
        <div class="add-tag-section" style="margin-bottom: 16px;">
          <a-input-group compact>
            <a-input
              v-model:value="newTagName"
              placeholder="输入新标签名称"
              style="width: calc(100% - 80px)"
              @press-enter="createTag"
            />
            <a-button type="primary" @click="createTag">添加</a-button>
          </a-input-group>
        </div>
        
        <div class="existing-tags">
          <h4>现有标签</h4>
          <div style="max-height: 300px; overflow-y: auto;">
            <a-tag
              v-for="tag in tags"
              :key="tag.id"
              closable
              style="margin: 4px;"
              @close="deleteTag(tag.id)"
            >
              {{ tag.name }}
            </a-tag>
          </div>
        </div>
      </div>

      <template #footer>
        <a-button @click="tagModalVisible = false">关闭</a-button>
      </template>
    </a-modal>

    <!-- 列设置对话框 -->
    <a-modal
      v-model:open="columnSettingsVisible"
      title="列设置"
      @ok="applyColumnSettings"
      width="400px"
    >
      <div class="column-settings">
        <p style="margin-bottom: 16px; color: #666;">选择要显示的列：</p>
        <div v-for="column in columnSettings" :key="column.key" style="margin-bottom: 8px;">
          <a-checkbox v-model:checked="column.visible">
            {{ column.title }}
          </a-checkbox>
        </div>
      </div>
      
      <template #footer>
        <a-button @click="resetColumnSettings" style="margin-right: 8px;">
          重置
        </a-button>
        <a-button @click="columnSettingsVisible = false" style="margin-right: 8px;">
          取消
        </a-button>
        <a-button type="primary" @click="applyColumnSettings">
          确定
        </a-button>
      </template>
    </a-modal>
  </div>
</template>

<style scoped>
.blog-management {
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  height: calc(100vh - 120px); /* 减去导航栏高度和额外间距，增加更多显示空间 */
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
  width: 200px;
}

.status-select {
  width: 120px;
}

.tag-select {
  width: 160px;
}

/* 圆角输入框 */
.rounded-input :deep(.ant-input) {
  border-radius: 8px;
}

/* 表格样式 */
.blog-table {
  width: 100%;
  flex: 1;
  overflow: hidden;
}

/* 让表格容器填满剩余高度 */
:deep(.ant-table-wrapper) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.ant-table) {
  flex: 1;
}

:deep(.ant-table-container) {
  flex: 1;
  overflow: auto;
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
  vertical-align: middle;
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

.tag-management .add-tag-section {
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}

.existing-tags h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}
</style>