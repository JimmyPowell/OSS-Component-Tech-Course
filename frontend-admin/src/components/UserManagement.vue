<script setup>
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import request from '../utils/request';
import axios from 'axios';

const users = ref([]);
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

const editDrawerVisible = ref(false);
const editingUser = ref(null);
const editForm = reactive({
  username: '',
  email: '',
  real_name: '',
  phone_number: '',
  school: '',
  role: '',
  is_active: true
});

// 添加用户抽屉
const addUserDrawerVisible = ref(false);
const addUserForm = reactive({
  username: '',
  email: '',
  password: '',
  real_name: '',
  phone_number: '',
  school: '',
  role: 'user'
});

// 用户详情抽屉
const userDetailDrawerVisible = ref(false);
const userDetail = ref(null);

// 列设置
const columnSettingsVisible = ref(false);
const availableColumns = [
  { key: 'username', title: '用户名', visible: true },
  { key: 'real_name', title: '真实姓名', visible: true },
  { key: 'email', title: '邮箱地址', visible: true },
  { key: 'phone_number', title: '手机号', visible: false },
  { key: 'school', title: '所在学校', visible: true },
  { key: 'role', title: '用户角色', visible: true },
  { key: 'is_active', title: '状态', visible: true },
  { key: 'uuid', title: 'UUID', visible: false },
  { key: 'created_at', title: '创建时间', visible: false },
  { key: 'updated_at', title: '更新时间', visible: false }
];
const columnSettings = reactive([...availableColumns]);

// 当前用户信息（用于权限控制）
const currentUser = ref(null);

// 表格高度自适应
const tableHeight = ref(600);

const API_BASE_URL = 'http://localhost:8000/api/v1/users';

const fetchUsers = async (page = 1, pageSize = 20, search = '') => {
  loading.value = true;
  try {
    const skip = (page - 1) * pageSize;
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: pageSize.toString()
    });
    
    if (search) {
      params.append('search', search);
    }

    const response = await request.get(`${API_BASE_URL}?${params}`);

    if (response.data.code === 200) {
      const data = response.data.data;
      users.value = data.items;
      pagination.total = data.total;
      pagination.current = page;
    } else {
      message.error(response.data.message || '获取用户列表失败');
    }
  } catch (error) {
    console.error('Failed to fetch users:', error);
    if (error.response?.status === 403) {
      message.error('权限不足，需要管理员权限');
    } else {
      message.error('获取用户列表失败');
    }
  } finally {
    loading.value = false;
  }
};

const addNewUser = () => {
  // 重置表单
  Object.assign(addUserForm, {
    username: '',
    email: '',
    password: '',
    real_name: '',
    phone_number: '',
    school: '',
    role: 'user'
  });
  addUserDrawerVisible.value = true;
};

const refreshList = () => {
  fetchUsers(pagination.current, pagination.pageSize, searchValue.value);
};

const configSettings = () => {
  columnSettingsVisible.value = true;
};

const searchUser = () => {
  pagination.current = 1;
  fetchUsers(1, pagination.pageSize, searchValue.value);
};

const resetSearch = () => {
  searchValue.value = '';
  pagination.current = 1;
  fetchUsers(1, pagination.pageSize, '');
};

const handleTableChange = (page, pageSize) => {
  pagination.current = page;
  pagination.pageSize = pageSize;
  fetchUsers(page, pageSize, searchValue.value);
};

const viewUser = async (userId) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${userId}`);
    
    if (response.data.code === 200) {
      userDetail.value = response.data.data;
      userDetailDrawerVisible.value = true;
    }
  } catch (error) {
    message.error('获取用户详情失败');
  }
};

const editUser = async (userId) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${userId}`);
    
    if (response.data.code === 200) {
      const user = response.data.data;
      editingUser.value = user;
      editForm.username = user.username;
      editForm.email = user.email;
      editForm.real_name = user.real_name || '';
      editForm.phone_number = user.phone_number || '';
      editForm.school = user.school || '';
      editForm.role = user.role;
      editForm.is_active = user.is_active;
      editDrawerVisible.value = true;
    }
  } catch (error) {
    message.error('获取用户信息失败');
  }
};

const handleEditSubmit = async () => {
  try {
    const response = await request.put(`${API_BASE_URL}/${editingUser.value.id}`, editForm);
    
    if (response.data.code === 200) {
      message.success('用户信息更新成功');
      editDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '更新失败');
    }
  } catch (error) {
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('更新用户信息失败');
    }
  }
};

const blockUser = (userId) => {
  const user = users.value.find(u => u.id === userId);
  
  // 检查是否是当前用户
  if (currentUser.value && userId === currentUser.value.id) {
    message.error('不能封禁自己');
    return;
  }
  
  const action = user.is_active ? '封禁' : '解封';
  
  Modal.confirm({
    title: `确认${action}用户`,
    content: `确定要${action}用户 ${user.username} 吗？`,
    onOk: async () => {
      try {
        const endpoint = user.is_active ? 'ban' : 'unban';
        const response = await request.post(`${API_BASE_URL}/${userId}/${endpoint}`, {});
        
        if (response.data.code === 200) {
          message.success(`用户${action}成功`);
          refreshList();
        } else {
          message.error(response.data.message || `${action}失败`);
        }
      } catch (error) {
        message.error(`${action}用户失败`);
      }
    }
  });
};

const deleteUser = (userId) => {
  const user = users.value.find(u => u.id === userId);
  
  // 检查是否是当前用户
  if (currentUser.value && userId === currentUser.value.id) {
    message.error('不能删除自己');
    return;
  }
  
  Modal.confirm({
    title: '确认删除用户',
    content: `确定要删除用户 ${user.username} 吗？此操作不可恢复！`,
    okType: 'danger',
    onOk: async () => {
      try {
        const response = await request.delete(`${API_BASE_URL}/${userId}`);
        
        if (response.data.code === 200) {
          message.success('用户删除成功');
          refreshList();
        } else {
          message.error(response.data.message || '删除失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('删除用户失败');
        }
      }
    }
  });
};

// 添加用户
const handleAddUser = async () => {
  try {
    const response = await request.post(API_BASE_URL, addUserForm);
    
    if (response.data.code === 201) {
      message.success('用户创建成功');
      addUserDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '创建失败');
    }
  } catch (error) {
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('创建用户失败');
    }
  }
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
  if (column.key === 'is_active') {
    return record.is_active ? '正常' : '已封禁';
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
  fetchUsers();
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

// 高度只需要监听窗口变化，不需要监听数据变化

// 清理事件监听
onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight);
  resizeObserver.disconnect();
});
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
    
    <div class="table-container">
      <a-table 
        :dataSource="users" 
        :pagination="false"
        :loading="loading"
        @change="handleTableChange"
        class="user-table"
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
          <template v-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'green' : 'red'">
              {{ record.is_active ? '正常' : '已封禁' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'created_at' || column.key === 'updated_at'">
            {{ new Date(record[column.key]).toLocaleString('zh-CN') }}
          </template>
          <template v-else>
            {{ record[column.key] || '-' }}
          </template>
        </template>
      </a-table-column>
      
      <!-- 操作列 -->
      <a-table-column key="action" title="操作" width="200" fixed="right">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewUser(record.id)">查看</a-button>
            <a-button size="small" type="primary" @click="editUser(record.id)">编辑</a-button>
            <a-button 
              size="small" 
              :type="record.is_active ? 'default' : 'primary'"
              @click="blockUser(record.id)"
              :disabled="currentUser && record.id === currentUser.id"
            >
              {{ record.is_active ? '封禁' : '解封' }}
            </a-button>
            <a-button 
              size="small" 
              danger 
              @click="deleteUser(record.id)"
              :disabled="currentUser && record.id === currentUser.id"
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

    <!-- 编辑用户抽屉 -->
    <a-drawer
      v-model:open="editDrawerVisible"
      title="编辑用户信息"
      width="480"
      placement="left"
      @close="editDrawerVisible = false"
      :maskClosable="true"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="用户名" required>
          <a-input v-model:value="editForm.username" />
        </a-form-item>
        <a-form-item label="邮箱" required>
          <a-input v-model:value="editForm.email" />
        </a-form-item>
        <a-form-item label="真实姓名">
          <a-input v-model:value="editForm.real_name" />
        </a-form-item>
        <a-form-item label="手机号">
          <a-input v-model:value="editForm.phone_number" />
        </a-form-item>
        <a-form-item label="学校">
          <a-input v-model:value="editForm.school" />
        </a-form-item>
        <a-form-item label="角色">
          <a-select v-model:value="editForm.role">
            <a-select-option value="user">普通用户</a-select-option>
            <a-select-option value="manager">管理员</a-select-option>
            <a-select-option value="teacher">教师</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="账号状态">
          <a-switch 
            v-model:checked="editForm.is_active"
            checked-children="正常"
            un-checked-children="封禁"
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

    <!-- 添加用户抽屉 -->
    <a-drawer
      v-model:open="addUserDrawerVisible"
      title="添加用户"
      width="480"
      placement="left"
      @close="addUserDrawerVisible = false"
      :maskClosable="true"
    >
      <a-form :model="addUserForm" layout="vertical">
        <a-form-item label="用户名" required>
          <a-input v-model:value="addUserForm.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="邮箱" required>
          <a-input v-model:value="addUserForm.email" placeholder="请输入邮箱地址" />
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password v-model:value="addUserForm.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item label="真实姓名" required>
          <a-input v-model:value="addUserForm.real_name" placeholder="请输入真实姓名" />
        </a-form-item>
        <a-form-item label="手机号" required>
          <a-input v-model:value="addUserForm.phone_number" placeholder="请输入手机号" />
        </a-form-item>
        <a-form-item label="学校">
          <a-input v-model:value="addUserForm.school" placeholder="请输入学校名称" />
        </a-form-item>
        <a-form-item label="角色">
          <a-select v-model:value="addUserForm.role">
            <a-select-option value="user">普通用户</a-select-option>
            <a-select-option value="manager">管理员</a-select-option>
            <a-select-option value="teacher">教师</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
      
      <template #footer>
        <div style="text-align: right;">
          <a-button @click="addUserDrawerVisible = false" style="margin-right: 8px;">
            取消
          </a-button>
          <a-button type="primary" @click="handleAddUser">
            确定
          </a-button>
        </div>
      </template>
    </a-drawer>

    <!-- 用户详情抽屉 -->
    <a-drawer
      v-model:open="userDetailDrawerVisible"
      title="用户详情"
      width="480"
      placement="left"
      :maskClosable="true"
    >
      <div v-if="userDetail" class="user-detail">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="用户名">
            {{ userDetail.username }}
          </a-descriptions-item>
          <a-descriptions-item label="真实姓名">
            {{ userDetail.real_name || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="邮箱">
            {{ userDetail.email }}
          </a-descriptions-item>
          <a-descriptions-item label="手机号">
            {{ userDetail.phone_number || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="学校">
            {{ userDetail.school || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="角色">
            {{ userDetail.role }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="userDetail.is_active ? 'green' : 'red'">
              {{ userDetail.is_active ? '正常' : '已封禁' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="UUID">
            {{ userDetail.uuid }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ new Date(userDetail.created_at).toLocaleString('zh-CN') }}
          </a-descriptions-item>
          <a-descriptions-item label="更新时间">
            {{ new Date(userDetail.updated_at).toLocaleString('zh-CN') }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-drawer>

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
.user-management {
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
</style>
