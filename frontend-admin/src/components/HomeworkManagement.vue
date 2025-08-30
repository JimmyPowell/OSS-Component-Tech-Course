<script setup>
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined, FileTextOutlined, UploadOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import request from '../utils/request';

const homeworks = ref([]);
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
const editingHomework = ref(null);
const editForm = reactive({
  name: '',
  description: '',
  content: '',
  cover_url: '',
  resource_urls: [],
  lasting_time: null,
  status: 'draft'
});

// 添加作业抽屉
const addHomeworkDrawerVisible = ref(false);
const addHomeworkForm = reactive({
  name: '',
  description: '',
  content: '',
  cover_url: '',
  resource_urls: [],
  lasting_time: null,
  status: 'draft'
});

// 文件上传相关
const fileList = ref([]);
const uploadProgress = ref(0);
const isUploading = ref(false);

// 封面图上传相关
const coverFileList = ref([]);
const coverUploadProgress = ref(0);
const isCoverUploading = ref(false);

// 编辑时的文件上传相关
const editFileList = ref([]);
const editUploadProgress = ref(0);
const isEditUploading = ref(false);

// 编辑时的封面图上传相关
const editCoverFileList = ref([]);
const editCoverUploadProgress = ref(0);
const isEditCoverUploading = ref(false);

// 作业详情抽屉
const homeworkDetailDrawerVisible = ref(false);
const homeworkDetail = ref(null);

// 列设置
const columnSettingsVisible = ref(false);
const availableColumns = [
  { key: 'cover_url', title: '封面预览', visible: true },
  { key: 'name', title: '作业名称', visible: true },
  { key: 'uuid', title: '作业编号', visible: false },
  { key: 'description', title: '作业描述', visible: true },
  { key: 'status', title: '状态', visible: true },
  { key: 'lasting_time', title: '时长限制', visible: true },
  { key: 'creator_id', title: '发布者ID', visible: false },
  { key: 'created_at', title: '发布时间', visible: true },
  { key: 'updated_at', title: '更新时间', visible: false }
];
const columnSettings = reactive([...availableColumns]);

// 表格高度自适应
const tableHeight = ref(600);

// 状态选项
const statusOptions = [
  { label: '未发布', value: 'draft' },
  { label: '已发布', value: 'published' }
];

const API_BASE_URL = 'http://localhost:8000/api/v1/admin/homeworks';

const fetchHomeworks = async (page = 1, pageSize = 20, search = '') => {
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
      homeworks.value = data.items;
      pagination.total = data.total;
      pagination.current = page;
    } else {
      message.error(response.data.message || '获取作业列表失败');
    }
  } catch (error) {
    console.error('Failed to fetch homeworks:', error);
    message.error('获取作业列表失败');
  } finally {
    loading.value = false;
  }
};

const addNewHomework = () => {
  Object.assign(addHomeworkForm, {
    name: '',
    description: '',
    content: '',
    cover_url: '',
    resource_urls: [],
    lasting_time: null,
    status: 'draft'
  });
  fileList.value = [];
  uploadProgress.value = 0;
  isUploading.value = false;
  
  // 重置封面图相关状态
  coverFileList.value = [];
  coverUploadProgress.value = 0;
  isCoverUploading.value = false;
  
  addHomeworkDrawerVisible.value = true;
};

const refreshList = () => {
  fetchHomeworks(pagination.current, pagination.pageSize, searchValue.value);
};

// 文件上传前的验证
const handleBeforeUpload = (file) => {
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/zip',
    'application/x-rar-compressed',
    'text/plain',
    'image/jpeg',
    'image/png',
    'image/gif'
  ];
  
  const isAllowed = allowedTypes.includes(file.type);
  
  if (!isAllowed) {
    message.error('只能上传 PDF、Word、Excel、压缩包、文本或图片文件!');
    return false;
  }
  
  const isLt50M = file.size / 1024 / 1024 < 50;
  if (!isLt50M) {
    message.error('文件大小不能超过 50MB!');
    return false;
  }
  
  return true;
};

// 移除文件
const handleRemoveFile = (file) => {
  const index = addHomeworkForm.resource_urls.findIndex(url => url.includes(file.name));
  if (index > -1) {
    addHomeworkForm.resource_urls.splice(index, 1);
  }
  uploadProgress.value = 0;
  return true;
};

// 获取七牛云上传token和配置信息
const getQiniuUploadToken = async (fileKey, purpose) => {
  try {
    console.log('正在请求上传token:', { fileKey, purpose });
    
    const response = await request.post('http://localhost:8000/api/v1/qiniu/admin/upload-token', {
      file_key: fileKey,
      purpose: purpose
    });
    
    console.log('上传token响应:', response);
    
    if (response.data.code === 201) {
      const data = response.data.data;
      console.log('成功获取上传token:', data);
      return {
        token: data.token,
        upload_domain: data.upload_domain,
        download_domain: data.download_domain
      };
    } else {
      console.error('上传token响应错误:', response.data);
      throw new Error(response.data.message || '获取上传token失败');
    }
  } catch (error) {
    console.error('获取上传token失败 - 详细错误信息:');
    console.error('错误对象:', error);
    console.error('错误消息:', error.message);
    console.error('响应状态:', error.response?.status);
    console.error('响应数据:', error.response?.data);
    console.error('响应头:', error.response?.headers);
    console.error('请求配置:', error.config);
    throw error;
  }
};

// 自定义上传到七牛云
const handleCustomUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  try {
    isUploading.value = true;
    uploadProgress.value = 0;
    
    // 更新文件列表为上传中状态
    const newFileList = [...fileList.value];
    const existingIndex = newFileList.findIndex(f => f.uid === file.uid);
    const fileItem = {
      uid: file.uid,
      name: file.name,
      status: 'uploading',
      percent: 0
    };
    
    if (existingIndex >= 0) {
      newFileList[existingIndex] = fileItem;
    } else {
      newFileList.push(fileItem);
    }
    fileList.value = newFileList;
    
    // 生成文件key
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `homework/${timestamp}_${randomStr}.${fileExtension}`;
    
    // 获取上传token和配置信息
    const tokenInfo = await getQiniuUploadToken(fileKey, `作业资源上传: ${file.name}`);
    
    // 上传到七牛云
    const formData = new FormData();
    formData.append('key', fileKey);
    formData.append('token', tokenInfo.token);
    formData.append('file', file, file.name);
    
    const xhr = new XMLHttpRequest();
    
    // 监听上传进度
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        uploadProgress.value = percent;
        
        const updatedFileList = [...fileList.value];
        const fileIndex = updatedFileList.findIndex(f => f.uid === file.uid);
        if (fileIndex >= 0) {
          updatedFileList[fileIndex] = {
            ...updatedFileList[fileIndex],
            percent: percent
          };
          fileList.value = updatedFileList;
        }
        
        if (onProgress) {
          onProgress({ percent });
        }
      }
    });
    
    // 上传完成处理
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          
          // 添加文件URL到作业资源列表
          const fileUrl = `${tokenInfo.download_domain}/${result.key}`;
          addHomeworkForm.resource_urls.push(fileUrl);
          
          uploadProgress.value = 100;
          message.success('文件上传成功');
          
          const updatedFileList = [...fileList.value];
          const fileIndex = updatedFileList.findIndex(f => f.uid === file.uid);
          if (fileIndex >= 0) {
            updatedFileList[fileIndex] = {
              ...updatedFileList[fileIndex],
              status: 'done',
              url: fileUrl,
              percent: 100
            };
            fileList.value = updatedFileList;
          }
          
          if (onSuccess) {
            onSuccess(result, file);
          }
          
        } catch (parseError) {
          console.error('解析响应失败:', parseError);
          message.error('服务器响应格式错误');
          const updatedFileList = fileList.value.filter(f => f.uid !== file.uid);
          fileList.value = updatedFileList;
          if (onError) {
            onError(parseError);
          }
        }
      } else {
        console.error('上传失败:', xhr.status);
        message.error(`文件上传失败: HTTP ${xhr.status}`);
        const updatedFileList = fileList.value.filter(f => f.uid !== file.uid);
        fileList.value = updatedFileList;
        if (onError) {
          onError(new Error(`HTTP ${xhr.status}`));
        }
      }
      isUploading.value = false;
    });
    
    // 上传错误处理
    xhr.addEventListener('error', (error) => {
      console.error('上传网络错误:', error);
      message.error('文件上传失败');
      isUploading.value = false;
      uploadProgress.value = 0;
      const updatedFileList = fileList.value.filter(f => f.uid !== file.uid);
      fileList.value = updatedFileList;
      if (onError) {
        onError(error);
      }
    });
    
    xhr.open('POST', tokenInfo.upload_domain);
    xhr.send(formData);
    
  } catch (error) {
    console.error('上传失败:', error);
    message.error(error.message || '文件上传失败');
    isUploading.value = false;
    uploadProgress.value = 0;
    const updatedFileList = fileList.value.filter(f => f.uid !== file.uid);
    fileList.value = updatedFileList;
    if (onError) {
      onError(error);
    }
  }
};

// 封面图上传前的验证
const handleCoverBeforeUpload = (file) => {
  const isImage = file.type.startsWith('image/');
  
  if (!isImage) {
    message.error('只能上传图片文件!');
    return false;
  }
  
  const isLt5M = file.size / 1024 / 1024 < 5;
  if (!isLt5M) {
    message.error('图片大小不能超过 5MB!');
    return false;
  }
  
  return true;
};

// 移除封面图文件
const handleRemoveCoverFile = (file) => {
  addHomeworkForm.cover_url = '';
  coverUploadProgress.value = 0;
  return true;
};

// 自定义封面图上传到七牛云
const handleCustomCoverUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  try {
    isCoverUploading.value = true;
    coverUploadProgress.value = 0;
    
    coverFileList.value = [{
      uid: file.uid,
      name: file.name,
      status: 'uploading',
      percent: 0
    }];
    
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `homework/cover/${timestamp}_${randomStr}.${fileExtension}`;
    
    const tokenInfo = await getQiniuUploadToken(fileKey, `作业封面图上传: ${file.name}`);
    
    const formData = new FormData();
    formData.append('key', fileKey);
    formData.append('token', tokenInfo.token);
    formData.append('file', file, file.name);
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        coverUploadProgress.value = percent;
        
        coverFileList.value = [{
          uid: file.uid,
          name: file.name,
          status: 'uploading',
          percent: percent
        }];
        
        if (onProgress) {
          onProgress({ percent });
        }
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          
          addHomeworkForm.cover_url = `${tokenInfo.download_domain}/${result.key}`;
          
          coverUploadProgress.value = 100;
          message.success('封面图上传成功');
          
          coverFileList.value = [{
            uid: file.uid,
            name: file.name,
            status: 'done',
            url: addHomeworkForm.cover_url,
            percent: 100
          }];
          
          if (onSuccess) {
            onSuccess(result, file);
          }
          
        } catch (parseError) {
          console.error('解析封面图响应失败:', parseError);
          message.error('服务器响应格式错误');
          coverFileList.value = [];
          if (onError) {
            onError(parseError);
          }
        }
      } else {
        console.error('封面图上传失败:', xhr.status);
        message.error(`封面图上传失败: HTTP ${xhr.status}`);
        coverFileList.value = [];
        if (onError) {
          onError(new Error(`HTTP ${xhr.status}`));
        }
      }
      isCoverUploading.value = false;
    });
    
    xhr.addEventListener('error', (error) => {
      console.error('封面图上传网络错误:', error);
      message.error('封面图上传失败');
      isCoverUploading.value = false;
      coverUploadProgress.value = 0;
      coverFileList.value = [];
      if (onError) {
        onError(error);
      }
    });
    
    xhr.open('POST', tokenInfo.upload_domain);
    xhr.send(formData);
    
  } catch (error) {
    console.error('封面图上传失败:', error);
    message.error(error.message || '封面图上传失败');
    isCoverUploading.value = false;
    coverUploadProgress.value = 0;
    coverFileList.value = [];
    if (onError) {
      onError(error);
    }
  }
};

const configSettings = () => {
  columnSettingsVisible.value = true;
};

const searchHomework = () => {
  pagination.current = 1;
  fetchHomeworks(1, pagination.pageSize, searchValue.value);
};

const resetSearch = () => {
  searchValue.value = '';
  pagination.current = 1;
  fetchHomeworks(1, pagination.pageSize, '');
};

const handleTableChange = (page, pageSize) => {
  pagination.current = page;
  pagination.pageSize = pageSize;
  fetchHomeworks(page, pageSize, searchValue.value);
};

const viewHomework = async (uuid) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${uuid}`);
    
    if (response.data.code === 200) {
      homeworkDetail.value = response.data.data;
      homeworkDetailDrawerVisible.value = true;
    }
  } catch (error) {
    message.error('获取作业详情失败');
  }
};

const editHomework = async (uuid) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${uuid}`);
    
    if (response.data.code === 200) {
      const homework = response.data.data;
      editingHomework.value = homework;
      editForm.name = homework.name;
      editForm.description = homework.description || '';
      editForm.content = homework.content || '';
      editForm.cover_url = homework.cover_url || '';
      editForm.resource_urls = homework.resource_urls || [];
      editForm.lasting_time = homework.lasting_time;
      editForm.status = homework.status || 'draft';
      
      // 重置编辑时的上传状态
      editFileList.value = [];
      editUploadProgress.value = 0;
      isEditUploading.value = false;
      
      editCoverFileList.value = [];
      editCoverUploadProgress.value = 0;
      isEditCoverUploading.value = false;
      
      // 如果有现有的封面图，在列表中显示
      if (homework.cover_url) {
        editCoverFileList.value = [{
          uid: '-1',
          name: '当前封面图',
          status: 'done',
          url: homework.cover_url
        }];
      }
      
      editDrawerVisible.value = true;
    }
  } catch (error) {
    message.error('获取作业信息失败');
  }
};

const handleEditSubmit = async () => {
  try {
    const response = await request.put(`${API_BASE_URL}/${editingHomework.value.uuid}`, editForm);
    
    if (response.data.code === 200) {
      message.success('作业信息更新成功');
      editDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '更新失败');
    }
  } catch (error) {
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('更新作业信息失败');
    }
  }
};

// 状态切换功能
const toggleHomeworkStatus = async (uuid, currentStatus) => {
  const newStatus = currentStatus === 'published' ? 'draft' : 'published';
  const statusText = newStatus === 'published' ? '发布' : '下架';
  
  Modal.confirm({
    title: `确认${statusText}作业`,
    content: `确定要${statusText}这个作业吗？`,
    onOk: async () => {
      try {
        const response = await request.put(`${API_BASE_URL}/${uuid}/status`, {
          status: newStatus
        });
        
        if (response.data.code === 200) {
          message.success(response.data.message || `作业已${statusText}`);
          refreshList();
        } else {
          message.error(response.data.message || `${statusText}失败`);
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error(`${statusText}作业失败`);
        }
      }
    }
  });
};

const deleteHomework = (uuid) => {
  const homework = homeworks.value.find(h => h.uuid === uuid);
  
  Modal.confirm({
    title: '确认删除作业',
    content: `确定要删除作业 "${homework.name}" 吗？此操作不可恢复！`,
    okType: 'danger',
    onOk: async () => {
      try {
        const response = await request.delete(`${API_BASE_URL}/${uuid}`);
        
        if (response.data.code === 200) {
          message.success('作业删除成功');
          refreshList();
        } else {
          message.error(response.data.message || '删除失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('删除作业失败');
        }
      }
    }
  });
};

// 添加作业
const handleAddHomework = async () => {
  // 验证必填字段
  if (!addHomeworkForm.name.trim()) {
    message.error('请输入作业名称');
    return;
  }
  
  if (isUploading.value) {
    message.error('文件正在上传中，请稍候...');
    return;
  }

  try {
    const response = await request.post(API_BASE_URL, addHomeworkForm);
    
    if (response.data.code === 200) {
      message.success('作业创建成功');
      addHomeworkDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '创建失败');
    }
  } catch (error) {
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('创建作业失败');
    }
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

// 格式化时长
const formatDuration = (minutes) => {
  if (!minutes) return '-';
  if (minutes < 60) return `${minutes}分钟`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}小时${mins}分钟` : `${hours}小时`;
};

// 计算表格高度
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
  fetchHomeworks();
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
  <div class="homework-management">
    <div class="page-header">
      <h1 class="page-title">课程作业管理</h1>
      <p class="page-subtitle">查看、编辑系统中的课程作业</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="addNewHomework">
          <template #icon><PlusOutlined /></template>
          添加作业
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
          placeholder="作业名称"
          class="search-input rounded-input"
          allow-clear
        />
        <a-button type="primary" class="search-btn" @click="searchHomework">
          查询
        </a-button>
        <a-button class="reset-btn" @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>
    
    <div class="table-container">
      <a-table 
        :dataSource="homeworks" 
        :pagination="false"
        :loading="loading"
        @change="handleTableChange"
        class="homework-table"
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
              <img v-if="record.cover_url" :src="record.cover_url" alt="作业封面" />
              <div v-else class="cover-placeholder">
                <FileTextOutlined style="font-size: 32px; color: #ccc;" />
              </div>
            </div>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="record.status === 'published' ? 'green' : 'orange'">
              {{ statusOptions.find(s => s.value === record.status)?.label || record.status }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'lasting_time'">
            {{ formatDuration(record.lasting_time) }}
          </template>
          <template v-else-if="column.key === 'created_at' || column.key === 'updated_at'">
            {{ new Date(record[column.key]).toLocaleString('zh-CN') }}
          </template>
          <template v-else-if="column.key === 'description'">
            <div class="description-cell">
              {{ record.description || '-' }}
            </div>
          </template>
          <template v-else>
            {{ record[column.key] || '-' }}
          </template>
        </template>
      </a-table-column>
      
      <!-- 操作列 -->
      <a-table-column key="action" title="操作" width="250" fixed="right">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewHomework(record.uuid)">查看</a-button>
            <a-button size="small" type="primary" @click="editHomework(record.uuid)">编辑</a-button>
            <a-button 
              size="small" 
              :type="record.status === 'published' ? 'default' : 'primary'"
              @click="toggleHomeworkStatus(record.uuid, record.status)"
              style="margin-right: 4px;"
            >
              {{ record.status === 'published' ? '下架' : '发布' }}
            </a-button>
            <a-button size="small" danger @click="deleteHomework(record.uuid)">删除</a-button>
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

    <!-- 编辑作业抽屉 -->
    <a-drawer
      v-model:open="editDrawerVisible"
      title="编辑作业信息"
      width="480"
      placement="left"
      @close="editDrawerVisible = false"
      :maskClosable="true"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="作业名称" required>
          <a-input v-model:value="editForm.name" placeholder="请输入作业名称" />
        </a-form-item>
        <a-form-item label="更换封面图">
          <a-upload
            v-model:file-list="editCoverFileList"
            name="cover"
            :multiple="false"
            :before-upload="handleCoverBeforeUpload"
            :remove="handleRemoveCoverFile"
            accept="image/*"
            :custom-request="handleCustomCoverUpload"
            :show-upload-list="true"
            :max-count="1"
            list-type="picture-card"
          >
            <div v-if="editCoverFileList.length < 1">
              <upload-outlined />
              <div style="margin-top: 8px">上传封面</div>
            </div>
          </a-upload>
          <div v-if="editCoverUploadProgress > 0 && editCoverUploadProgress < 100" style="margin-top: 8px;">
            <a-progress :percent="editCoverUploadProgress" />
          </div>
          <div style="margin-top: 4px; font-size: 12px; color: #666;">
            如需更换封面图，请重新上传。支持 JPG、PNG 等图片格式，文件大小不超过 5MB
          </div>
        </a-form-item>
        <a-form-item label="作业描述">
          <a-textarea v-model:value="editForm.description" placeholder="请输入作业描述" :rows="3" />
        </a-form-item>
        <a-form-item label="作业内容">
          <a-textarea v-model:value="editForm.content" placeholder="请输入作业具体内容" :rows="5" />
        </a-form-item>
        <a-form-item label="时长限制（分钟）">
          <a-input-number v-model:value="editForm.lasting_time" placeholder="请输入作业时长限制" style="width: 100%" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="editForm.status" placeholder="请选择作业状态">
            <a-select-option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </a-select-option>
          </a-select>
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

    <!-- 添加作业抽屉 -->
    <a-drawer
      v-model:open="addHomeworkDrawerVisible"
      title="添加作业"
      width="480"
      placement="left"
      @close="addHomeworkDrawerVisible = false"
      :maskClosable="true"
    >
      <a-form :model="addHomeworkForm" layout="vertical">
        <a-form-item label="作业名称" required>
          <a-input v-model:value="addHomeworkForm.name" placeholder="请输入作业名称" />
        </a-form-item>
        <a-form-item label="上传封面图">
          <a-upload
            v-model:file-list="coverFileList"
            name="cover"
            :multiple="false"
            :before-upload="handleCoverBeforeUpload"
            :remove="handleRemoveCoverFile"
            accept="image/*"
            :custom-request="handleCustomCoverUpload"
            :show-upload-list="true"
            :max-count="1"
            list-type="picture-card"
          >
            <div v-if="coverFileList.length < 1">
              <upload-outlined />
              <div style="margin-top: 8px">上传封面</div>
            </div>
          </a-upload>
          <div v-if="coverUploadProgress > 0 && coverUploadProgress < 100" style="margin-top: 8px;">
            <a-progress :percent="coverUploadProgress" />
          </div>
          <div style="margin-top: 4px; font-size: 12px; color: #666;">
            支持 JPG、PNG 等图片格式，文件大小不超过 5MB
          </div>
        </a-form-item>
        <a-form-item label="作业描述">
          <a-textarea v-model:value="addHomeworkForm.description" placeholder="请输入作业描述" :rows="3" />
        </a-form-item>
        <a-form-item label="作业内容">
          <a-textarea v-model:value="addHomeworkForm.content" placeholder="请输入作业具体内容" :rows="5" />
        </a-form-item>
        <a-form-item label="上传作业资源">
          <a-upload
            v-model:file-list="fileList"
            name="file"
            :multiple="true"
            :before-upload="handleBeforeUpload"
            :remove="handleRemoveFile"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.zip,.rar,.txt,.jpg,.png,.gif"
            :custom-request="handleCustomUpload"
            :show-upload-list="true"
          >
            <a-button>
              <template #icon><upload-outlined /></template>
              上传资源文件
            </a-button>
          </a-upload>
          <div v-if="uploadProgress > 0 && uploadProgress < 100" style="margin-top: 8px;">
            <a-progress :percent="uploadProgress" />
          </div>
          <div style="margin-top: 4px; font-size: 12px; color: #666;">
            支持 PDF、Word、Excel、压缩包、文本、图片格式，单个文件大小不超过 50MB
          </div>
        </a-form-item>
        <a-form-item label="时长限制（分钟）">
          <a-input-number v-model:value="addHomeworkForm.lasting_time" placeholder="请输入作业时长限制" style="width: 100%" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="addHomeworkForm.status" placeholder="请选择作业状态">
            <a-select-option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
      
      <template #footer>
        <div style="text-align: right;">
          <a-button @click="addHomeworkDrawerVisible = false" style="margin-right: 8px;">
            取消
          </a-button>
          <a-button type="primary" @click="handleAddHomework">
            确定
          </a-button>
        </div>
      </template>
    </a-drawer>

    <!-- 作业详情抽屉 -->
    <a-drawer
      v-model:open="homeworkDetailDrawerVisible"
      title="作业详情"
      width="480"
      placement="left"
      :maskClosable="true"
    >
      <div v-if="homeworkDetail" class="homework-detail">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="作业名称">
            {{ homeworkDetail.name }}
          </a-descriptions-item>
          <a-descriptions-item label="作业编号">
            {{ homeworkDetail.uuid }}
          </a-descriptions-item>
          <a-descriptions-item label="作业描述">
            {{ homeworkDetail.description || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="作业内容">
            <div style="white-space: pre-wrap;">{{ homeworkDetail.content || '-' }}</div>
          </a-descriptions-item>
          <a-descriptions-item label="时长限制">
            {{ formatDuration(homeworkDetail.lasting_time) }}
          </a-descriptions-item>
          <a-descriptions-item label="资源文件" v-if="homeworkDetail.resource_urls?.length">
            <div v-for="(url, index) in homeworkDetail.resource_urls" :key="index" style="margin-bottom: 4px;">
              <a :href="url" target="_blank">资源文件 {{ index + 1 }}</a>
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="发布者ID">
            {{ homeworkDetail.creator_id }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ new Date(homeworkDetail.created_at).toLocaleString('zh-CN') }}
          </a-descriptions-item>
          <a-descriptions-item label="更新时间">
            {{ new Date(homeworkDetail.updated_at).toLocaleString('zh-CN') }}
          </a-descriptions-item>
          <a-descriptions-item label="封面预览" v-if="homeworkDetail.cover_url">
            <img :src="homeworkDetail.cover_url" alt="作业封面" style="max-width: 200px; max-height: 150px;" />
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
.homework-management {
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

.homework-table {
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

.status-cell {
  display: flex;
  align-items: center;
  justify-content: flex-start;
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

.search-input :deep(.ant-input::placeholder) {
  font-size: 11px;
  font-weight: 500;
  color: #bfbfbf;
}
</style>