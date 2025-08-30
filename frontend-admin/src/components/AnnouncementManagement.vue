<script setup>
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined, NotificationOutlined, UploadOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import request from '../utils/request';

const announcements = ref([]);
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

// 编辑抽屉
const editDrawerVisible = ref(false);
const editingAnnouncement = ref(null);
const editForm = reactive({
  name: '',
  summary: '',
  detail_info: '',
  cover_url: ''
});

// 添加公告抽屉
const addAnnouncementDrawerVisible = ref(false);
const addAnnouncementForm = reactive({
  name: '',
  summary: '',
  detail_info: '',
  cover_url: ''
});

// 封面图上传相关
const coverFileList = ref([]);
const coverUploadProgress = ref(0);
const isCoverUploading = ref(false);

// 编辑时的封面图上传相关
const editCoverFileList = ref([]);
const editCoverUploadProgress = ref(0);
const isEditCoverUploading = ref(false);

// 公告详情抽屉
const announcementDetailDrawerVisible = ref(false);
const announcementDetail = ref(null);

// 列设置
const columnSettingsVisible = ref(false);
const availableColumns = [
  { key: 'cover_url', title: '封面预览', visible: true },
  { key: 'name', title: '公告标题', visible: true },
  { key: 'uuid', title: '公告编号', visible: false },
  { key: 'summary', title: '摘要', visible: true },
  { key: 'status', title: '状态', visible: true },
  { key: 'publisher_id', title: '发布者ID', visible: false },
  { key: 'created_at', title: '发布时间', visible: true },
  { key: 'updated_at', title: '更新时间', visible: false }
];
const columnSettings = reactive([...availableColumns]);

// 表格高度自适应
const tableHeight = ref(600);

const API_BASE_URL = 'http://localhost:8000/api/v1/admin/announcements';

// 状态选项
const statusOptions = [
  { label: '未发布', value: 'draft' },
  { label: '已发布', value: 'published' }
];

const fetchAnnouncements = async (page = 1, pageSize = 20, search = '') => {
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
      announcements.value = data.items;
      pagination.total = data.total;
      pagination.current = page;
    } else {
      message.error(response.data.message || '获取公告列表失败');
    }
  } catch (error) {
    console.error('Failed to fetch announcements:', error);
    message.error('获取公告列表失败');
  } finally {
    loading.value = false;
  }
};

const addNewAnnouncement = () => {
  Object.assign(addAnnouncementForm, {
    name: '',
    summary: '',
    detail_info: '',
    cover_url: ''
  });
  
  // 重置封面图相关状态
  coverFileList.value = [];
  coverUploadProgress.value = 0;
  isCoverUploading.value = false;
  
  addAnnouncementDrawerVisible.value = true;
};

const refreshList = () => {
  fetchAnnouncements(pagination.current, pagination.pageSize, searchValue.value);
};

// 获取七牛云上传token和配置信息
const getQiniuUploadToken = async (fileKey, purpose) => {
  try {
    const response = await request.post('http://localhost:8000/api/v1/qiniu/admin/upload-token', {
      file_key: fileKey,
      purpose: purpose
    });
    
    if (response.data.code === 201) {
      const data = response.data.data;
      return {
        token: data.token,
        upload_domain: data.upload_domain,
        download_domain: data.download_domain
      };
    } else {
      throw new Error(response.data.message || '获取上传token失败');
    }
  } catch (error) {
    console.error('获取上传token失败:', error);
    throw error;
  }
};

// 封面图上传前验证
const handleCoverBeforeUpload = (file) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  if (!isJpgOrPng) {
    message.error('只能上传 JPG/PNG 格式的图片!');
    return false;
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    message.error('图片大小不能超过 2MB!');
    return false;
  }
  return true;
};

// 自定义封面图上传到七牛云
const handleCoverCustomUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  try {
    isCoverUploading.value = true;
    coverUploadProgress.value = 0;
    
    // 生成文件key
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `announcement/cover/${timestamp}_${randomStr}.${fileExtension}`;
    
    // 获取上传token和配置信息
    const tokenInfo = await getQiniuUploadToken(fileKey, `公告封面上传: ${file.name}`);
    
    // 上传到七牛云
    const formData = new FormData();
    formData.append('key', fileKey);
    formData.append('token', tokenInfo.token);
    formData.append('file', file, file.name);
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        coverUploadProgress.value = percent;
        onProgress({ percent });
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          const imageUrl = `${tokenInfo.download_domain}/${result.key}`;
          addAnnouncementForm.cover_url = imageUrl;
          
          coverFileList.value = [{
            uid: file.uid,
            name: file.name,
            status: 'done',
            url: imageUrl
          }];
          
          onSuccess(result);
          message.success('封面图上传成功');
        } catch (parseError) {
          console.error('解析上传结果失败:', parseError);
          onError(parseError);
          message.error('上传失败：结果解析错误');
        }
      } else {
        const error = new Error(`上传失败: ${xhr.status}`);
        onError(error);
        message.error('封面图上传失败');
      }
      isCoverUploading.value = false;
    });
    
    xhr.addEventListener('error', () => {
      const error = new Error('上传请求失败');
      onError(error);
      message.error('封面图上传失败');
      isCoverUploading.value = false;
    });
    
    xhr.open('POST', tokenInfo.upload_domain);
    xhr.send(formData);
    
  } catch (error) {
    console.error('封面图上传失败:', error);
    onError(error);
    message.error('封面图上传失败: ' + error.message);
    isCoverUploading.value = false;
  }
};

// 编辑时封面图上传
const handleEditCoverCustomUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  try {
    isEditCoverUploading.value = true;
    editCoverUploadProgress.value = 0;
    
    // 生成文件key
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `announcement/cover/${timestamp}_${randomStr}.${fileExtension}`;
    
    // 获取上传token和配置信息
    const tokenInfo = await getQiniuUploadToken(fileKey, `公告封面编辑上传: ${file.name}`);
    
    // 上传到七牛云
    const formData = new FormData();
    formData.append('key', fileKey);
    formData.append('token', tokenInfo.token);
    formData.append('file', file, file.name);
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        editCoverUploadProgress.value = percent;
        onProgress({ percent });
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          const imageUrl = `${tokenInfo.download_domain}/${result.key}`;
          editForm.cover_url = imageUrl;
          
          editCoverFileList.value = [{
            uid: file.uid,
            name: file.name,
            status: 'done',
            url: imageUrl
          }];
          
          onSuccess(result);
          message.success('封面图上传成功');
        } catch (parseError) {
          console.error('解析上传结果失败:', parseError);
          onError(parseError);
          message.error('上传失败：结果解析错误');
        }
      } else {
        const error = new Error(`上传失败: ${xhr.status}`);
        onError(error);
        message.error('封面图上传失败');
      }
      isEditCoverUploading.value = false;
    });
    
    xhr.addEventListener('error', () => {
      const error = new Error('上传请求失败');
      onError(error);
      message.error('封面图上传失败');
      isEditCoverUploading.value = false;
    });
    
    xhr.open('POST', tokenInfo.upload_domain);
    xhr.send(formData);
    
  } catch (error) {
    console.error('封面图上传失败:', error);
    onError(error);
    message.error('封面图上传失败: ' + error.message);
    isEditCoverUploading.value = false;
  }
};

// 移除封面图
const handleCoverRemove = () => {
  addAnnouncementForm.cover_url = '';
  coverFileList.value = [];
  coverUploadProgress.value = 0;
  return true;
};

// 编辑时移除封面图
const handleEditCoverRemove = () => {
  editForm.cover_url = '';
  editCoverFileList.value = [];
  editCoverUploadProgress.value = 0;
  return true;
};

// 提交新增公告
const handleAddAnnouncement = async () => {
  try {
    if (!addAnnouncementForm.name.trim()) {
      message.error('请输入公告标题');
      return;
    }

    const response = await request.post(API_BASE_URL, addAnnouncementForm);
    
    if (response.data.code === 200) {
      message.success('公告添加成功');
      addAnnouncementDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '公告添加失败');
    }
  } catch (error) {
    console.error('Add announcement failed:', error);
    message.error('公告添加失败');
  }
};

// 编辑公告
const editAnnouncement = (record) => {
  editingAnnouncement.value = record;
  Object.assign(editForm, {
    name: record.name,
    summary: record.summary || '',
    detail_info: record.detail_info || '',
    cover_url: record.cover_url || ''
  });
  
  // 设置封面图文件列表
  if (record.cover_url) {
    editCoverFileList.value = [{
      uid: '-1',
      name: 'cover.jpg',
      status: 'done',
      url: record.cover_url
    }];
  } else {
    editCoverFileList.value = [];
  }
  
  editCoverUploadProgress.value = 0;
  isEditCoverUploading.value = false;
  
  editDrawerVisible.value = true;
};

// 提交编辑公告
const handleEditAnnouncement = async () => {
  try {
    if (!editForm.name.trim()) {
      message.error('请输入公告标题');
      return;
    }

    const response = await request.put(`${API_BASE_URL}/${editingAnnouncement.value.uuid}`, editForm);
    
    if (response.data.code === 200) {
      message.success('公告更新成功');
      editDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '公告更新失败');
    }
  } catch (error) {
    console.error('Edit announcement failed:', error);
    message.error('公告更新失败');
  }
};

// 删除公告
const deleteAnnouncement = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除公告 "${record.name}" 吗？`,
    okText: '确认',
    cancelText: '取消',
    async onOk() {
      try {
        const response = await request.delete(`${API_BASE_URL}/${record.uuid}`);
        
        if (response.data.code === 200) {
          message.success('公告删除成功');
          refreshList();
        } else {
          message.error(response.data.message || '公告删除失败');
        }
      } catch (error) {
        console.error('Delete announcement failed:', error);
        message.error('公告删除失败');
      }
    }
  });
};

// 查看公告详情
const viewAnnouncementDetail = async (record) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${record.uuid}`);
    
    if (response.data.code === 200) {
      announcementDetail.value = response.data.data;
      announcementDetailDrawerVisible.value = true;
    } else {
      message.error(response.data.message || '获取公告详情失败');
    }
  } catch (error) {
    console.error('Failed to fetch announcement detail:', error);
    message.error('获取公告详情失败');
  }
};

// 表格列配置
const visibleColumns = computed(() => {
  return columnSettings.filter(col => col.visible);
});

// 分页变化处理
const handleTableChange = (page, pageSize) => {
  pagination.current = page;
  pagination.pageSize = pageSize;
  fetchAnnouncements(page, pageSize, searchValue.value);
};

// 搜索处理
const handleSearch = () => {
  pagination.current = 1;
  fetchAnnouncements(1, pagination.pageSize, searchValue.value);
};

// 搜索框回车事件
const onSearchEnter = () => {
  handleSearch();
};

// 重置搜索
const resetSearch = () => {
  searchValue.value = '';
  pagination.current = 1;
  fetchAnnouncements(1, pagination.pageSize, '');
};

// 监听窗口大小变化
const updateTableHeight = () => {
  const windowHeight = window.innerHeight;
  tableHeight.value = Math.max(400, windowHeight - 300);
};

onMounted(() => {
  fetchAnnouncements();
  updateTableHeight();
  window.addEventListener('resize', updateTableHeight);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateTableHeight);
});

// 切换公告状态
const toggleAnnouncementStatus = async (uuid, currentStatus) => {
  const newStatus = currentStatus === 'published' ? 'draft' : 'published';
  const statusText = newStatus === 'published' ? '发布' : '下架';
  
  Modal.confirm({
    title: `确认${statusText}公告`,
    content: `确定要${statusText}这个公告吗？`,
    onOk: async () => {
      try {
        const response = await request.put(`${API_BASE_URL}/${uuid}/status`, {
          status: newStatus
        });
        
        if (response.data.code === 200) {
          message.success(`公告${statusText}成功`);
          refreshList();
        } else {
          message.error(response.data.message || `${statusText}失败`);
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error(`${statusText}公告失败`);
        }
      }
    }
  });
};

// 监听搜索值变化（可选：实现实时搜索）
watch(searchValue, (newVal) => {
  if (!newVal) {
    handleSearch();
  }
});
</script>

<template>
  <div class="announcement-management">
    <div class="page-header">
      <h1 class="page-title">公告管理</h1>
      <p class="page-subtitle">查看、编辑系统中的公告</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="addNewAnnouncement">
          <template #icon><PlusOutlined /></template>
          新增公告
        </a-button>
        <a-button class="refresh-btn" @click="refreshList">
          刷新
        </a-button>
        <a-button class="settings-btn" @click="columnSettingsVisible = true">
          <template #icon><SettingOutlined /></template>
          列设置
        </a-button>
      </div>
      
      <div class="right-actions">
        <a-input 
          v-model:value="searchValue"
          placeholder="公告标题"
          class="search-input rounded-input"
          allow-clear
        />
        <a-button type="primary" class="search-btn" @click="handleSearch">
          查询
        </a-button>
        <a-button class="reset-btn" @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>

    <div class="table-container">
      <a-table 
        :dataSource="announcements" 
        :pagination="false"
        :loading="loading"
        @change="handleTableChange"
        class="announcement-table"
        row-key="uuid"
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
          <template v-if="column.key === 'cover_url'">
            <div class="cover-preview">
              <img v-if="record.cover_url" :src="record.cover_url" alt="公告封面" />
              <div v-else class="cover-placeholder">
                <NotificationOutlined style="font-size: 32px; color: #ccc;" />
              </div>
            </div>
          </template>
          <template v-else-if="column.key === 'created_at' || column.key === 'updated_at'">
            {{ new Date(record[column.key]).toLocaleString('zh-CN') }}
          </template>
          <template v-else-if="column.key === 'summary'">
            <div class="description-cell">
              {{ record.summary || '-' }}
            </div>
          </template>
          <template v-else-if="column.key === 'name'">
            <a @click="viewAnnouncementDetail(record)">{{ record.name }}</a>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="record.status === 'published' ? 'green' : 'orange'">
              {{ statusOptions.find(s => s.value === record.status)?.label || record.status }}
            </a-tag>
          </template>
          <template v-else>
            {{ record[column.key] || '-' }}
          </template>
        </template>
      </a-table-column>
      
      <!-- 操作列 -->
      <a-table-column key="action" title="操作" width="260" fixed="right">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewAnnouncementDetail(record)">查看</a-button>
            <a-button size="small" type="primary" @click="editAnnouncement(record)">编辑</a-button>
            <a-button 
              size="small" 
              :type="record.status === 'published' ? 'default' : 'primary'"
              @click="toggleAnnouncementStatus(record.uuid, record.status)"
              style="margin-right: 4px;"
            >
              {{ record.status === 'published' ? '下架' : '发布' }}
            </a-button>
            <a-button size="small" danger @click="deleteAnnouncement(record)">删除</a-button>
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

    <!-- 新增公告抽屉 -->
    <a-drawer
      v-model:open="addAnnouncementDrawerVisible"
      title="新增公告"
      width="600"
      placement="left"
      :closable="true"
      :maskClosable="true"
    >
      <div class="drawer-content">
        <a-form layout="vertical">
          <a-form-item label="公告标题" required>
            <a-input 
              v-model:value="addAnnouncementForm.name" 
              placeholder="请输入公告标题"
              :maxlength="255"
              show-count
            />
          </a-form-item>
          
          <a-form-item label="摘要">
            <a-textarea 
              v-model:value="addAnnouncementForm.summary" 
              placeholder="请输入公告摘要"
              :rows="3"
              :maxlength="512"
              show-count
            />
          </a-form-item>
          
          <a-form-item label="详细内容">
            <a-textarea 
              v-model:value="addAnnouncementForm.detail_info" 
              placeholder="请输入公告详细内容"
              :rows="8"
            />
          </a-form-item>
          
          <a-form-item label="封面图">
            <a-upload
              v-model:file-list="coverFileList"
              name="cover"
              list-type="picture-card"
              class="cover-uploader"
              :show-upload-list="true"
              :custom-request="handleCoverCustomUpload"
              :before-upload="handleCoverBeforeUpload"
              :on-remove="handleCoverRemove"
              :max-count="1"
            >
              <div v-if="coverFileList.length < 1">
                <UploadOutlined />
                <div style="margin-top: 8px">上传封面</div>
              </div>
            </a-upload>
            <div class="upload-tip">支持JPG、PNG格式，大小不超过2MB</div>
          </a-form-item>
        </a-form>
      </div>
      
      <template #footer>
        <div class="drawer-footer">
          <a-button @click="addAnnouncementDrawerVisible = false">取消</a-button>
          <a-button type="primary" @click="handleAddAnnouncement" :loading="isCoverUploading">
            确认添加
          </a-button>
        </div>
      </template>
    </a-drawer>

    <!-- 编辑公告抽屉 -->
    <a-drawer
      v-model:open="editDrawerVisible"
      title="编辑公告"
      width="600"
      placement="left"
      :closable="true"
      :maskClosable="true"
    >
      <div class="drawer-content">
        <a-form layout="vertical">
          <a-form-item label="公告标题" required>
            <a-input 
              v-model:value="editForm.name" 
              placeholder="请输入公告标题"
              :maxlength="255"
              show-count
            />
          </a-form-item>
          
          <a-form-item label="摘要">
            <a-textarea 
              v-model:value="editForm.summary" 
              placeholder="请输入公告摘要"
              :rows="3"
              :maxlength="512"
              show-count
            />
          </a-form-item>
          
          <a-form-item label="详细内容">
            <a-textarea 
              v-model:value="editForm.detail_info" 
              placeholder="请输入公告详细内容"
              :rows="8"
            />
          </a-form-item>
          
          <a-form-item label="封面图">
            <a-upload
              v-model:file-list="editCoverFileList"
              name="cover"
              list-type="picture-card"
              class="cover-uploader"
              :show-upload-list="true"
              :custom-request="handleEditCoverCustomUpload"
              :before-upload="handleCoverBeforeUpload"
              :on-remove="handleEditCoverRemove"
              :max-count="1"
            >
              <div v-if="editCoverFileList.length < 1">
                <UploadOutlined />
                <div style="margin-top: 8px">上传封面</div>
              </div>
            </a-upload>
            <div class="upload-tip">支持JPG、PNG格式，大小不超过2MB</div>
          </a-form-item>
        </a-form>
      </div>
      
      <template #footer>
        <div class="drawer-footer">
          <a-button @click="editDrawerVisible = false">取消</a-button>
          <a-button type="primary" @click="handleEditAnnouncement" :loading="isEditCoverUploading">
            确认保存
          </a-button>
        </div>
      </template>
    </a-drawer>

    <!-- 公告详情抽屉 -->
    <a-drawer
      v-model:open="announcementDetailDrawerVisible"
      title="公告详情"
      width="600"
      :closable="true"
    >
      <div v-if="announcementDetail" class="announcement-detail">
        <div class="detail-section">
          <h3>{{ announcementDetail.name }}</h3>
        </div>
        
        <div v-if="announcementDetail.cover_url" class="detail-section">
          <h4>封面图</h4>
          <img 
            :src="announcementDetail.cover_url" 
            alt="封面" 
            class="detail-cover"
          />
        </div>
        
        <div v-if="announcementDetail.summary" class="detail-section">
          <h4>摘要</h4>
          <p>{{ announcementDetail.summary }}</p>
        </div>
        
        <div v-if="announcementDetail.detail_info" class="detail-section">
          <h4>详细内容</h4>
          <div class="detail-content" v-html="announcementDetail.detail_info.replace(/\n/g, '<br>')"></div>
        </div>
        
        <div class="detail-section">
          <h4>发布信息</h4>
          <p>发布者ID: {{ announcementDetail.publisher_id }}</p>
          <p>发布时间: {{ new Date(announcementDetail.created_at).toLocaleString('zh-CN') }}</p>
          <p>更新时间: {{ new Date(announcementDetail.updated_at).toLocaleString('zh-CN') }}</p>
        </div>
      </div>
    </a-drawer>

    <!-- 列设置弹窗 -->
    <a-modal
      v-model:open="columnSettingsVisible"
      title="列设置"
      @ok="columnSettingsVisible = false"
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
        <a-button @click="columnSettingsVisible = false" style="margin-right: 8px;">
          取消
        </a-button>
        <a-button type="primary" @click="columnSettingsVisible = false">
          确定
        </a-button>
      </template>
    </a-modal>
  </div>
</template>

<style scoped>
.announcement-management {
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

.rounded-input :deep(.ant-input) {
  border-radius: 8px;
}

/* 表格样式 */
.table-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.announcement-table {
  width: 100%;
  flex: 1;
}

.pagination-container {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fff;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.cover-preview {
  width: 160px;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}

.description-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  height: 60px;
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

.search-input :deep(.ant-input::placeholder) {
  font-size: 11px;
  font-weight: 500;
  color: #bfbfbf;
}

.drawer-content {
  padding-bottom: 60px;
}

.drawer-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  border-top: 1px solid #e8e8e8;
  background: #fff;
  text-align: right;
}

.cover-uploader {
  width: 160px;
  height: 90px;
}

.cover-uploader :deep(.ant-upload-select) {
  width: 160px !important;
  height: 90px !important;
}

.upload-tip {
  margin-top: 8px;
  color: #666;
  font-size: 12px;
}

.announcement-detail {
  .detail-section {
    margin-bottom: 24px;
    
    h3 {
      font-size: 18px;
      font-weight: 500;
      margin-bottom: 16px;
      color: #262626;
    }
    
    h4 {
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 8px;
      color: #595959;
    }
    
    p {
      margin: 0;
      line-height: 1.6;
      color: #262626;
    }
  }
  
  .detail-cover {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .detail-content {
    line-height: 1.6;
    color: #262626;
    white-space: pre-wrap;
  }
}

.column-settings {
  .column-item {
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
  }
}


:deep(.ant-upload-list-picture-card .ant-upload-list-item) {
  width: 160px;
  height: 90px;
}

:deep(.ant-upload-list-picture-card .ant-upload-list-item-thumbnail img) {
  width: 160px;
  height: 90px;
  object-fit: cover;
}
</style>
