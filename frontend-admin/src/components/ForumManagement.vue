<script setup>
import { ref, onMounted, reactive, computed } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined, EditOutlined, DeleteOutlined, TagOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import request from '../utils/request';

const categories = ref([]);
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

// 添加分类表单
const addCategoryModalVisible = ref(false);
const addCategoryForm = reactive({
  name: '',
  description: '',
  icon: '',
  color: '#1890ff',
  sort_order: 0,
  is_active: true
});

// 编辑分类表单
const editCategoryModalVisible = ref(false);
const editCategoryForm = reactive({
  uuid: '',
  name: '',
  description: '',
  icon: '',
  color: '#1890ff',
  sort_order: 0,
  is_active: true
});

// 预设图标选项
const iconOptions = [
  { value: '💬', label: '💬 一般讨论' },
  { value: '❓', label: '❓ 问答' },
  { value: '💻', label: '💻 技术' },
  { value: '📚', label: '📚 学习' },
  { value: '🎯', label: '🎯 项目' },
  { value: '🔥', label: '🔥 热门' },
  { value: '📢', label: '📢 通知' },
  { value: '🎉', label: '🎉 活动' },
  { value: '🤔', label: '🤔 思考' },
  { value: '💡', label: '💡 想法' },
];

// 预设颜色选项
const colorOptions = [
  '#1890ff', '#52c41a', '#faad14', '#f5222d', 
  '#722ed1', '#eb2f96', '#13c2c2', '#fa8c16',
  '#a0d911', '#1890ff'
];

const API_BASE_URL = '/admin/forum/categories';

// 获取分类列表
const fetchCategories = async (page = 1, pageSize = 20, search = '') => {
  loading.value = true;
  try {
    const skip = (page - 1) * pageSize;
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: pageSize.toString()
    });
    
    if (search) {
      params.append('name', search);
    }

    const response = await request.get(`${API_BASE_URL}?${params}`);

    if (response.data.code === 200) {
      const data = response.data.data;
      categories.value = data.items;
      pagination.total = data.total;
      pagination.current = page;
    } else {
      message.error(response.data.message || '获取分类列表失败');
    }
  } catch (error) {
    console.error('Failed to fetch categories:', error);
    message.error('获取分类列表失败');
  } finally {
    loading.value = false;
  }
};

// 添加分类
const handleAddCategory = async () => {
  try {
    if (!addCategoryForm.name.trim()) {
      message.error('请输入分类名称');
      return;
    }

    const response = await request.post(API_BASE_URL, addCategoryForm);
    
    if (response.data.code === 200) {
      message.success('分类添加成功');
      addCategoryModalVisible.value = false;
      resetAddForm();
      refreshList();
    } else {
      message.error(response.data.message || '分类添加失败');
    }
  } catch (error) {
    console.error('Add category failed:', error);
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('分类添加失败');
    }
  }
};

// 编辑分类
const editCategory = (record) => {
  Object.assign(editCategoryForm, {
    uuid: record.uuid,
    name: record.name,
    description: record.description || '',
    icon: record.icon || '',
    color: record.color || '#1890ff',
    sort_order: record.sort_order || 0,
    is_active: record.is_active !== false
  });
  editCategoryModalVisible.value = true;
};

// 更新分类
const handleEditCategory = async () => {
  try {
    if (!editCategoryForm.name.trim()) {
      message.error('请输入分类名称');
      return;
    }

    const { uuid, ...updateData } = editCategoryForm;
    const response = await request.put(`${API_BASE_URL}/${uuid}`, updateData);
    
    if (response.data.code === 200) {
      message.success('分类更新成功');
      editCategoryModalVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '分类更新失败');
    }
  } catch (error) {
    console.error('Edit category failed:', error);
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('分类更新失败');
    }
  }
};

// 删除分类
const deleteCategory = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除分类 "${record.name}" 吗？删除后该分类下的所有帖子将无法显示。`,
    okText: '确认',
    cancelText: '取消',
    okType: 'danger',
    async onOk() {
      try {
        const response = await request.delete(`${API_BASE_URL}/${record.uuid}`);
        
        if (response.data.code === 200) {
          message.success('分类删除成功');
          refreshList();
        } else {
          message.error(response.data.message || '分类删除失败');
        }
      } catch (error) {
        console.error('Delete category failed:', error);
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('分类删除失败');
        }
      }
    }
  });
};

// 重置添加表单
const resetAddForm = () => {
  Object.assign(addCategoryForm, {
    name: '',
    description: '',
    icon: '',
    color: '#1890ff',
    sort_order: 0,
    is_active: true
  });
};

// 刷新列表
const refreshList = () => {
  fetchCategories(pagination.current, pagination.pageSize, searchValue.value);
};

// 分页变化处理
const handleTableChange = (page, pageSize) => {
  pagination.current = page;
  pagination.pageSize = pageSize;
  fetchCategories(page, pageSize, searchValue.value);
};

// 搜索处理
const handleSearch = () => {
  pagination.current = 1;
  fetchCategories(1, pagination.pageSize, searchValue.value);
};

// 重置搜索
const resetSearch = () => {
  searchValue.value = '';
  pagination.current = 1;
  fetchCategories(1, pagination.pageSize, '');
};

// 打开添加弹窗
const openAddModal = () => {
  resetAddForm();
  addCategoryModalVisible.value = true;
};

// 切换分类状态
const toggleCategoryStatus = async (record) => {
  try {
    const response = await request.put(`${API_BASE_URL}/${record.uuid}`, {
      is_active: !record.is_active
    });
    
    if (response.data.code === 200) {
      message.success(`分类已${!record.is_active ? '激活' : '停用'}`);
      refreshList();
    } else {
      message.error(response.data.message || '状态更新失败');
    }
  } catch (error) {
    console.error('Toggle status failed:', error);
    message.error('状态更新失败');
  }
};

// 表格列配置
const columns = [
  {
    title: '分类名称',
    dataIndex: 'name',
    key: 'name',
    width: 200,
  },
  {
    title: '图标',
    dataIndex: 'icon',
    key: 'icon',
    width: 80,
    align: 'center',
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    ellipsis: true,
  },
  {
    title: '帖子数量',
    dataIndex: 'post_count',
    key: 'post_count',
    width: 100,
    align: 'center',
  },
  {
    title: '排序',
    dataIndex: 'sort_order',
    key: 'sort_order',
    width: 80,
    align: 'center',
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    key: 'is_active',
    width: 100,
    align: 'center',
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
  },
  {
    title: '操作',
    key: 'action',
    width: 200,
    fixed: 'right',
  },
];

onMounted(() => {
  fetchCategories();
});
</script>

<template>
  <div class="forum-management">
    <div class="page-header">
      <h1 class="page-title">论坛分类管理</h1>
      <p class="page-subtitle">管理论坛讨论分类，设置分类信息和状态</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" @click="openAddModal">
          <template #icon><PlusOutlined /></template>
          添加分类
        </a-button>
        <a-button @click="refreshList">
          刷新
        </a-button>
      </div>
      
      <div class="right-actions">
        <a-input 
          v-model:value="searchValue"
          placeholder="搜索分类名称"
          class="search-input"
          allow-clear
          @pressEnter="handleSearch"
        />
        <a-button type="primary" @click="handleSearch">
          <template #icon><SearchOutlined /></template>
          查询
        </a-button>
        <a-button @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>
    
    <div class="table-container">
      <a-table 
        :dataSource="categories" 
        :columns="columns"
        :pagination="false"
        :loading="loading"
        row-key="uuid"
        :scroll="{ x: 1200, y: 'calc(100vh - 320px)' }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <div class="category-name" :style="{ borderLeft: `3px solid ${record.color || '#1890ff'}` }">
              <span class="name-text">{{ record.name }}</span>
            </div>
          </template>
          
          <template v-else-if="column.key === 'icon'">
            <span class="category-icon" v-if="record.icon">{{ record.icon }}</span>
            <span class="no-icon" v-else>-</span>
          </template>
          
          <template v-else-if="column.key === 'description'">
            <span class="description-text">{{ record.description || '-' }}</span>
          </template>
          
          <template v-else-if="column.key === 'post_count'">
            <a-tag color="blue">{{ record.post_count || 0 }}</a-tag>
          </template>
          
          <template v-else-if="column.key === 'is_active'">
            <a-switch 
              :checked="record.is_active !== false" 
              @change="() => toggleCategoryStatus(record)"
              checked-children="启用"
              un-checked-children="停用"
            />
          </template>
          
          <template v-else-if="column.key === 'created_at'">
            {{ new Date(record.created_at).toLocaleString('zh-CN') }}
          </template>
          
          <template v-else-if="column.key === 'action'">
            <div class="action-buttons">
              <a-button size="small" type="primary" @click="editCategory(record)">
                <template #icon><EditOutlined /></template>
                编辑
              </a-button>
              <a-button 
                size="small" 
                danger 
                @click="deleteCategory(record)"
                :disabled="(record.post_count || 0) > 0"
              >
                <template #icon><DeleteOutlined /></template>
                删除
              </a-button>
            </div>
          </template>
        </template>
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

    <!-- 添加分类弹窗 -->
    <a-modal
      v-model:open="addCategoryModalVisible"
      title="添加论坛分类"
      @ok="handleAddCategory"
      @cancel="addCategoryModalVisible = false"
      width="600px"
    >
      <a-form 
        :model="addCategoryForm" 
        layout="vertical"
        :label-col="{ span: 24 }"
        :wrapper-col="{ span: 24 }"
      >
        <a-form-item label="分类名称" required>
          <a-input 
            v-model:value="addCategoryForm.name" 
            placeholder="请输入分类名称"
            maxlength="50"
            show-count
          />
        </a-form-item>
        
        <a-form-item label="分类描述">
          <a-textarea 
            v-model:value="addCategoryForm.description" 
            placeholder="请输入分类描述"
            :rows="3"
            maxlength="200"
            show-count
          />
        </a-form-item>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="分类图标">
              <a-select 
                v-model:value="addCategoryForm.icon" 
                placeholder="选择图标"
                allow-clear
              >
                <a-select-option v-for="icon in iconOptions" :key="icon.value" :value="icon.value">
                  {{ icon.label }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          
          <a-col :span="12">
            <a-form-item label="分类颜色">
              <a-select v-model:value="addCategoryForm.color" placeholder="选择颜色">
                <a-select-option v-for="color in colorOptions" :key="color" :value="color">
                  <div style="display: flex; align-items: center;">
                    <div 
                      :style="{ 
                        width: '16px', 
                        height: '16px', 
                        backgroundColor: color, 
                        borderRadius: '2px',
                        marginRight: '8px'
                      }"
                    ></div>
                    {{ color }}
                  </div>
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="排序顺序">
              <a-input-number 
                v-model:value="addCategoryForm.sort_order" 
                :min="0"
                :max="999"
                style="width: 100%"
                placeholder="数字越小排序越靠前"
              />
            </a-form-item>
          </a-col>
          
          <a-col :span="12">
            <a-form-item label="状态">
              <a-switch 
                v-model:checked="addCategoryForm.is_active"
                checked-children="启用"
                un-checked-children="停用"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 编辑分类弹窗 -->
    <a-modal
      v-model:open="editCategoryModalVisible"
      title="编辑论坛分类"
      @ok="handleEditCategory"
      @cancel="editCategoryModalVisible = false"
      width="600px"
    >
      <a-form 
        :model="editCategoryForm" 
        layout="vertical"
        :label-col="{ span: 24 }"
        :wrapper-col="{ span: 24 }"
      >
        <a-form-item label="分类名称" required>
          <a-input 
            v-model:value="editCategoryForm.name" 
            placeholder="请输入分类名称"
            maxlength="50"
            show-count
          />
        </a-form-item>
        
        <a-form-item label="分类描述">
          <a-textarea 
            v-model:value="editCategoryForm.description" 
            placeholder="请输入分类描述"
            :rows="3"
            maxlength="200"
            show-count
          />
        </a-form-item>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="分类图标">
              <a-select 
                v-model:value="editCategoryForm.icon" 
                placeholder="选择图标"
                allow-clear
              >
                <a-select-option v-for="icon in iconOptions" :key="icon.value" :value="icon.value">
                  {{ icon.label }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          
          <a-col :span="12">
            <a-form-item label="分类颜色">
              <a-select v-model:value="editCategoryForm.color" placeholder="选择颜色">
                <a-select-option v-for="color in colorOptions" :key="color" :value="color">
                  <div style="display: flex; align-items: center;">
                    <div 
                      :style="{ 
                        width: '16px', 
                        height: '16px', 
                        backgroundColor: color, 
                        borderRadius: '2px',
                        marginRight: '8px'
                      }"
                    ></div>
                    {{ color }}
                  </div>
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="排序顺序">
              <a-input-number 
                v-model:value="editCategoryForm.sort_order" 
                :min="0"
                :max="999"
                style="width: 100%"
                placeholder="数字越小排序越靠前"
              />
            </a-form-item>
          </a-col>
          
          <a-col :span="12">
            <a-form-item label="状态">
              <a-switch 
                v-model:checked="editCategoryForm.is_active"
                checked-children="启用"
                un-checked-children="停用"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.forum-management {
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  margin-bottom: 16px;
}

.page-title {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 500;
  color: #262626;
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

.pagination-container {
  padding: 12px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fff;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-shrink: 0;
}

.category-name {
  padding-left: 12px;
  display: flex;
  align-items: center;
}

.name-text {
  font-weight: 500;
  color: #262626;
}

.category-icon {
  font-size: 18px;
  text-align: center;
}

.no-icon {
  color: #bfbfbf;
  text-align: center;
}

.description-text {
  color: #595959;
  line-height: 1.4;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

:deep(.ant-table) {
  border-radius: 12px;
  font-size: 14px;
}

:deep(.ant-table-thead > tr > th) {
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 16px;
  font-weight: 500;
  color: #262626;
}

:deep(.ant-table-tbody > tr > td) {
  padding: 12px 16px;
  vertical-align: middle;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background-color: #f5f5f5;
}

:deep(.ant-btn) {
  border-radius: 6px;
  font-size: 14px;
}

:deep(.ant-btn-primary) {
  background: #1890ff;
  border-color: #1890ff;
}

:deep(.ant-btn-primary:hover) {
  background: #40a9ff;
  border-color: #40a9ff;
}

:deep(.ant-switch-checked) {
  background-color: #52c41a;
}

:deep(.ant-modal-header) {
  border-bottom: 1px solid #f0f0f0;
  padding: 16px 24px;
}

:deep(.ant-modal-body) {
  padding: 24px;
}

:deep(.ant-form-item-label > label) {
  font-weight: 500;
  color: #262626;
}

:deep(.ant-select-selection-item) {
  display: flex;
  align-items: center;
}
</style>
