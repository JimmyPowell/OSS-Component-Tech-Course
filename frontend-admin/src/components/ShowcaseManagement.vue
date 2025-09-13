<script setup>
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined, AppstoreOutlined, UploadOutlined, TagOutlined, MessageOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import request from '../utils/request';

const showcases = ref([]);
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
const editingShowcase = ref(null);
const editForm = reactive({
  name: '',
  summary: '',
  detailed_introduction: '',
  avatar_url: '',
  project_url: '',
  tags: [],
  status: 'draft'
});

// 添加作品抽屉
const addShowcaseDrawerVisible = ref(false);
const addShowcaseForm = reactive({
  name: '',
  summary: '',
  detailed_introduction: '',
  avatar_url: '',
  project_url: '',
  tags: [],
  status: 'draft'
});

// 封面图上传相关
const avatarFileList = ref([]);
const avatarUploadProgress = ref(0);
const isAvatarUploading = ref(false);

// 编辑时的封面图上传相关
const editAvatarFileList = ref([]);
const editAvatarUploadProgress = ref(0);
const isEditAvatarUploading = ref(false);

// 作品详情抽屉
const showcaseDetailDrawerVisible = ref(false);
const showcaseDetail = ref(null);

// 讨论管理相关
const commentsDrawerVisible = ref(false);
const currentShowcase = ref(null);
const showcaseComments = ref([]);
const loadingComments = ref(false);
const expandedCommentKeys = ref([]);
const commentDetails = ref({});
const commentReplies = ref({});
const loadingDetails = ref(new Set());
const loadingReplies = ref(new Set());

// 列设置
const columnSettingsVisible = ref(false);
const availableColumns = [
  { key: 'avatar_url', title: '封面预览', visible: true },
  { key: 'name', title: '作品名称', visible: true },
  { key: 'uuid', title: '作品编号', visible: false },
  { key: 'summary', title: '作品简介', visible: true },
  { key: 'status', title: '状态', visible: true },
  { key: 'views_count', title: '浏览数', visible: true },
  { key: 'likes_count', title: '点赞数', visible: true },
  { key: 'comments_count', title: '评论数', visible: true },
  { key: 'author_id', title: '作者ID', visible: false },
  { key: 'created_at', title: '创建时间', visible: true },
  { key: 'updated_at', title: '更新时间', visible: false }
];
const columnSettings = reactive([...availableColumns]);

// 表格高度自适应
const tableHeight = ref(600);


const API_BASE_URL = '/admin/showcases';

const fetchShowcases = async (page = 1, pageSize = 20, search = '') => {
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
      showcases.value = data.items;
      pagination.total = data.total;
      pagination.current = page;
    } else {
      message.error(response.data.message || '获取作品列表失败');
    }
  } catch (error) {
    console.error('Failed to fetch showcases:', error);
    message.error('获取作品列表失败');
  } finally {
    loading.value = false;
  }
};

const addNewShowcase = () => {
  Object.assign(addShowcaseForm, {
    name: '',
    summary: '',
    detailed_introduction: '',
    avatar_url: '',
    project_url: '',
    tags: [],
    status: 'draft'
  });
  
  // 重置封面图相关状态
  avatarFileList.value = [];
  avatarUploadProgress.value = 0;
  isAvatarUploading.value = false;
  
  addShowcaseDrawerVisible.value = true;
};

const refreshList = () => {
  fetchShowcases(pagination.current, pagination.pageSize, searchValue.value);
};

// 获取七牛云上传token和配置信息
const getQiniuUploadToken = async (fileKey, purpose) => {
  try {
    const response = await request.post('/qiniu/admin/upload-token', {
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
const handleAvatarBeforeUpload = (file) => {
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
const handleAvatarCustomUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  try {
    isAvatarUploading.value = true;
    avatarUploadProgress.value = 0;
    
    // 生成文件key
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `showcase/avatar/${timestamp}_${randomStr}.${fileExtension}`;
    
    // 获取上传token和配置信息
    const tokenInfo = await getQiniuUploadToken(fileKey, `作品封面上传: ${file.name}`);
    
    // 上传到七牛云
    const formData = new FormData();
    formData.append('key', fileKey);
    formData.append('token', tokenInfo.token);
    formData.append('file', file, file.name);
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        avatarUploadProgress.value = percent;
        onProgress({ percent });
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          const imageUrl = `${tokenInfo.download_domain}/${result.key}`;
          addShowcaseForm.avatar_url = imageUrl;
          
          avatarFileList.value = [{
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
      isAvatarUploading.value = false;
    });
    
    xhr.addEventListener('error', () => {
      const error = new Error('上传请求失败');
      onError(error);
      message.error('封面图上传失败');
      isAvatarUploading.value = false;
    });
    
    xhr.open('POST', tokenInfo.upload_domain);
    xhr.send(formData);
    
  } catch (error) {
    console.error('封面图上传失败:', error);
    onError(error);
    message.error('封面图上传失败: ' + error.message);
    isAvatarUploading.value = false;
  }
};

// 编辑时封面图上传
const handleEditAvatarCustomUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  try {
    isEditAvatarUploading.value = true;
    editAvatarUploadProgress.value = 0;
    
    // 生成文件key
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `showcase/avatar/${timestamp}_${randomStr}.${fileExtension}`;
    
    // 获取上传token和配置信息
    const tokenInfo = await getQiniuUploadToken(fileKey, `作品封面编辑上传: ${file.name}`);
    
    // 上传到七牛云
    const formData = new FormData();
    formData.append('key', fileKey);
    formData.append('token', tokenInfo.token);
    formData.append('file', file, file.name);
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        editAvatarUploadProgress.value = percent;
        onProgress({ percent });
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          const imageUrl = `${tokenInfo.download_domain}/${result.key}`;
          editForm.avatar_url = imageUrl;
          
          editAvatarFileList.value = [{
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
      isEditAvatarUploading.value = false;
    });
    
    xhr.addEventListener('error', () => {
      const error = new Error('上传请求失败');
      onError(error);
      message.error('封面图上传失败');
      isEditAvatarUploading.value = false;
    });
    
    xhr.open('POST', tokenInfo.upload_domain);
    xhr.send(formData);
    
  } catch (error) {
    console.error('封面图上传失败:', error);
    onError(error);
    message.error('封面图上传失败: ' + error.message);
    isEditAvatarUploading.value = false;
  }
};

// 移除封面图
const handleAvatarRemove = () => {
  addShowcaseForm.avatar_url = '';
  avatarFileList.value = [];
  avatarUploadProgress.value = 0;
  return true;
};

// 编辑时移除封面图
const handleEditAvatarRemove = () => {
  editForm.avatar_url = '';
  editAvatarFileList.value = [];
  editAvatarUploadProgress.value = 0;
  return true;
};

// 提交新增作品
const handleAddShowcase = async () => {
  try {
    if (!addShowcaseForm.name.trim()) {
      message.error('请输入作品名称');
      return;
    }

    const response = await request.post(API_BASE_URL, addShowcaseForm);
    
    if (response.data.code === 200) {
      message.success('作品添加成功');
      addShowcaseDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '作品添加失败');
    }
  } catch (error) {
    console.error('Add showcase failed:', error);
    message.error('作品添加失败');
  }
};

// 编辑作品
const editShowcase = (record) => {
  editingShowcase.value = record;
  Object.assign(editForm, {
    name: record.name,
    summary: record.summary || '',
    detailed_introduction: record.detailed_introduction || '',
    avatar_url: record.avatar_url || '',
    project_url: record.project_url || '',
    tags: record.tags || [],
    status: record.status || 'draft'
  });
  
  // 设置封面图文件列表
  if (record.avatar_url) {
    editAvatarFileList.value = [{
      uid: '-1',
      name: 'avatar.jpg',
      status: 'done',
      url: record.avatar_url
    }];
  } else {
    editAvatarFileList.value = [];
  }
  
  editAvatarUploadProgress.value = 0;
  isEditAvatarUploading.value = false;
  
  editDrawerVisible.value = true;
};

// 提交编辑作品
const handleEditShowcase = async () => {
  try {
    if (!editForm.name.trim()) {
      message.error('请输入作品名称');
      return;
    }

    const response = await request.put(`${API_BASE_URL}/${editingShowcase.value.uuid}`, editForm);
    
    if (response.data.code === 200) {
      message.success('作品更新成功');
      editDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '作品更新失败');
    }
  } catch (error) {
    console.error('Edit showcase failed:', error);
    message.error('作品更新失败');
  }
};

// 删除作品
const deleteShowcase = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除作品 "${record.name}" 吗？`,
    okText: '确认',
    cancelText: '取消',
    async onOk() {
      try {
        const response = await request.delete(`${API_BASE_URL}/${record.uuid}`);
        
        if (response.data.code === 200) {
          message.success('作品删除成功');
          refreshList();
        } else {
          message.error(response.data.message || '作品删除失败');
        }
      } catch (error) {
        console.error('Delete showcase failed:', error);
        message.error('作品删除失败');
      }
    }
  });
};

// 查看作品详情
const viewShowcaseDetail = async (record) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${record.uuid}`);
    
    if (response.data.code === 200) {
      showcaseDetail.value = response.data.data;
      showcaseDetailDrawerVisible.value = true;
    } else {
      message.error(response.data.message || '获取作品详情失败');
    }
  } catch (error) {
    console.error('Failed to fetch showcase detail:', error);
    message.error('获取作品详情失败');
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
  fetchShowcases(page, pageSize, searchValue.value);
};

// 搜索处理
const handleSearch = () => {
  pagination.current = 1;
  fetchShowcases(1, pagination.pageSize, searchValue.value);
};

// 搜索框回车事件
const onSearchEnter = () => {
  handleSearch();
};

// 重置搜索
const resetSearch = () => {
  searchValue.value = '';
  pagination.current = 1;
  fetchShowcases(1, pagination.pageSize, '');
};

// 监听窗口大小变化
const updateTableHeight = () => {
  const windowHeight = window.innerHeight;
  tableHeight.value = Math.max(400, windowHeight - 300);
};

onMounted(() => {
  fetchShowcases();
  updateTableHeight();
  window.addEventListener('resize', updateTableHeight);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateTableHeight);
});

// 下架作品
const archiveShowcase = async (uuid) => {
  Modal.confirm({
    title: '确认下架作品',
    content: '确定要下架这个作品吗？下架后可以重新恢复。',
    onOk: async () => {
      try {
        const response = await request.post(`${API_BASE_URL}/${uuid}/archive`);
        
        if (response.data.code === 200) {
          message.success('作品下架成功');
          refreshList();
        } else {
          message.error(response.data.message || '下架失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('下架作品失败');
        }
      }
    }
  });
};

// 恢复作品
const restoreShowcase = async (uuid) => {
  Modal.confirm({
    title: '确认恢复作品',
    content: '确定要恢复这个作品吗？',
    onOk: async () => {
      try {
        const response = await request.post(`${API_BASE_URL}/${uuid}/restore`);
        
        if (response.data.code === 200) {
          message.success('作品恢复成功');
          refreshList();
        } else {
          message.error(response.data.message || '恢复失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('恢复作品失败');
        }
      }
    }
  });
};

// 设为优秀作品
const promoteToExcellent = async (uuid) => {
  Modal.confirm({
    title: '确认设为优秀',
    content: '确定要将这个作品设为优秀吗？',
    onOk: async () => {
      try {
        const response = await request.post(`${API_BASE_URL}/${uuid}/promote`, {
          action: 'excellent',
          review_comment: '管理员设为优秀操作'
        });
        
        if (response.data.code === 200) {
          message.success('作品设为优秀成功');
          refreshList();
        } else {
          message.error(response.data.message || '设为优秀失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('设为优秀失败');
        }
      }
    }
  });
};

// 获取状态颜色
const getStatusColor = (status) => {
  const statusColors = {
    'draft': 'default',
    'pending': 'orange', 
    'published': 'blue',
    'reject': 'red',
    'excellent': 'purple',
    'archived': 'red'
  };
  return statusColors[status] || 'default';
};

// 获取状态文本
const getStatusText = (status) => {
  const statusTexts = {
    'draft': '草稿',
    'pending': '待审核',
    'published': '已发布',
    'reject': '已拒绝', 
    'excellent': '优秀',
    'archived': '已下架'
  };
  return statusTexts[status] || status;
};

// ==================== 讨论管理相关方法 ====================

// 查看作品讨论
const viewShowcaseComments = async (showcase) => {
  currentShowcase.value = showcase;
  commentsDrawerVisible.value = true;
  await fetchShowcaseComments(showcase.uuid);
};

// 获取作品评论列表
const fetchShowcaseComments = async (showcaseUuid, page = 1, pageSize = 20) => {
  loadingComments.value = true;
  try {
    // 先通过showcase UUID获取showcase ID
    const showcaseResponse = await request.get(`/showcases/${showcaseUuid}`);
    
    if (showcaseResponse.data.code !== 200) {
      message.error('获取作品信息失败');
      return;
    }
    
    const showcaseId = showcaseResponse.data.data.id;
    
    // 获取评论列表
    const response = await request.get(`/showcase-comments?showcase_id=${showcaseId}&skip=0&limit=100`);
    
    if (response.data.code === 200) {
      showcaseComments.value = response.data.data.items;
    } else {
      message.error('获取评论列表失败');
    }
  } catch (error) {
    console.error('获取评论失败:', error);
    message.error('获取评论列表失败');
  } finally {
    loadingComments.value = false;
  }
};

// 加载评论回复
const loadCommentReplies = async (commentUuid) => {
  if (loadingReplies.value.has(commentUuid)) return;
  
  loadingReplies.value.add(commentUuid);
  try {
    const response = await request.get(`/showcase-comment-replies?comment_uuid=${commentUuid}&skip=0&limit=100`);
    
    if (response.data.code === 200) {
      commentReplies.value[commentUuid] = response.data.data.items;
    } else {
      commentReplies.value[commentUuid] = [];
    }
  } catch (error) {
    console.error('获取回复失败:', error);
    commentReplies.value[commentUuid] = [];
  } finally {
    loadingReplies.value.delete(commentUuid);
  }
};

// 展开/折叠评论详情
const toggleCommentExpansion = async (commentUuid) => {
  const index = expandedCommentKeys.value.indexOf(commentUuid);
  if (index > -1) {
    // 折叠
    expandedCommentKeys.value.splice(index, 1);
  } else {
    // 展开
    expandedCommentKeys.value.push(commentUuid);
    // 加载回复数据
    await loadCommentReplies(commentUuid);
  }
};

// 删除评论
const deleteShowcaseComment = (commentUuid) => {
  Modal.confirm({
    title: '确认删除评论',
    content: '确定要删除这条评论吗？此操作不可恢复！',
    okType: 'danger',
    onOk: async () => {
      try {
        const response = await request.delete(`/showcase-comments/${commentUuid}`);
        
        if (response.data.code === 200) {
          message.success('评论删除成功');
          // 重新加载评论列表
          await fetchShowcaseComments(currentShowcase.value.uuid);
        } else {
          message.error('删除评论失败');
        }
      } catch (error) {
        console.error('删除评论失败:', error);
        message.error('删除评论失败');
      }
    }
  });
};

// 删除回复
const deleteCommentReply = (commentUuid, replyUuid) => {
  Modal.confirm({
    title: '确认删除回复',
    content: '确定要删除这条回复吗？此操作不可恢复！',
    okType: 'danger',
    onOk: async () => {
      try {
        const response = await request.delete(`/showcase-comment-replies/${replyUuid}`);
        
        if (response.data.code === 200) {
          message.success('回复删除成功');
          // 重新加载该评论的回复
          await loadCommentReplies(commentUuid);
        } else {
          message.error('删除回复失败');
        }
      } catch (error) {
        console.error('删除回复失败:', error);
        message.error('删除回复失败');
      }
    }
  });
};

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return '-';
  return new Date(timeString).toLocaleString('zh-CN');
};

// ==================== 原有方法 ====================

// 监听搜索值变化
watch(searchValue, (newVal) => {
  if (!newVal) {
    handleSearch();
  }
});
</script>

<template>
  <div class="showcase-management">
    <div class="page-header">
      <h1 class="page-title">作品管理</h1>
      <p class="page-subtitle">查看、编辑系统中的作品</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="addNewShowcase">
          <template #icon><PlusOutlined /></template>
          新增作品
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
          placeholder="作品名称"
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
        :dataSource="showcases" 
        :pagination="false"
        :loading="loading"
        @change="handleTableChange"
        class="showcase-table"
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
          <template v-if="column.key === 'avatar_url'">
            <div class="cover-preview">
              <img v-if="record.avatar_url" :src="record.avatar_url" alt="作品封面" />
              <div v-else class="cover-placeholder">
                <AppstoreOutlined style="font-size: 32px; color: #ccc;" />
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
            <a @click="viewShowcaseDetail(record)">{{ record.name }}</a>
          </template>
          <template v-else-if="column.key === 'comments_count'">
            <a-tag color="blue">{{ record.comments_count || 0 }}</a-tag>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-else>
            {{ record[column.key] || '-' }}
          </template>
        </template>
      </a-table-column>
      
      <!-- 操作列 -->
      <a-table-column key="action" title="操作" width="280" fixed="right">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewShowcaseDetail(record)">查看</a-button>
            <a-button size="small" @click="viewShowcaseComments(record)">
              <template #icon><MessageOutlined /></template>
              讨论管理
            </a-button>
            <a-button size="small" type="primary" @click="editShowcase(record)">编辑</a-button>
            <a-button size="small" danger @click="deleteShowcase(record)">删除</a-button>
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

    <!-- 新增作品抽屉 -->
    <a-drawer
      v-model:open="addShowcaseDrawerVisible"
      title="新增作品"
      width="600"
      placement="left"
      :closable="true"
      :maskClosable="true"
    >
      <div class="drawer-content">
        <a-form layout="vertical">
          <a-form-item label="作品名称" required>
            <a-input 
              v-model:value="addShowcaseForm.name" 
              placeholder="请输入作品名称"
              :maxlength="255"
              show-count
            />
          </a-form-item>
          
          <a-form-item label="作品简介">
            <a-textarea 
              v-model:value="addShowcaseForm.summary" 
              placeholder="请输入作品简介"
              :rows="3"
              :maxlength="512"
              show-count
            />
          </a-form-item>
          
          <a-form-item label="详细介绍">
            <a-textarea 
              v-model:value="addShowcaseForm.detailed_introduction" 
              placeholder="请输入作品详细介绍"
              :rows="6"
            />
          </a-form-item>
          
          <a-form-item label="项目地址">
            <a-input 
              v-model:value="addShowcaseForm.project_url" 
              placeholder="请输入项目地址(如GitHub、官网等)"
            />
          </a-form-item>
          
          
          <a-form-item label="标签">
            <a-select
              v-model:value="addShowcaseForm.tags"
              mode="tags"
              placeholder="请输入或选择标签"
              :maxTagCount="5"
            />
          </a-form-item>
          
          <a-form-item label="作品状态" required>
            <a-select
              v-model:value="addShowcaseForm.status"
              placeholder="请选择作品状态"
            >
              <a-select-option value="draft">
                <a-tag color="default">草稿</a-tag>
              </a-select-option>
              <a-select-option value="published">
                <a-tag color="blue">已发布</a-tag>
              </a-select-option>
              <a-select-option value="excellent">
                <a-tag color="purple">优秀作品</a-tag>
              </a-select-option>
              <a-select-option value="archived">
                <a-tag color="red">已下架</a-tag>
              </a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="作品封面">
            <a-upload
              v-model:file-list="avatarFileList"
              name="avatar"
              list-type="picture-card"
              class="avatar-uploader"
              :show-upload-list="true"
              :custom-request="handleAvatarCustomUpload"
              :before-upload="handleAvatarBeforeUpload"
              :on-remove="handleAvatarRemove"
              :max-count="1"
            >
              <div v-if="avatarFileList.length < 1">
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
          <a-button @click="addShowcaseDrawerVisible = false">取消</a-button>
          <a-button type="primary" @click="handleAddShowcase" :loading="isAvatarUploading">
            确认添加
          </a-button>
        </div>
      </template>
    </a-drawer>

    <!-- 编辑作品抽屉 -->
    <a-drawer
      v-model:open="editDrawerVisible"
      title="编辑作品"
      width="600"
      placement="left"
      :closable="true"
      :maskClosable="true"
    >
      <div class="drawer-content">
        <a-form layout="vertical">
          <a-form-item label="作品名称" required>
            <a-input 
              v-model:value="editForm.name" 
              placeholder="请输入作品名称"
              :maxlength="255"
              show-count
            />
          </a-form-item>
          
          <a-form-item label="作品简介">
            <a-textarea 
              v-model:value="editForm.summary" 
              placeholder="请输入作品简介"
              :rows="3"
              :maxlength="512"
              show-count
            />
          </a-form-item>
          
          <a-form-item label="详细介绍">
            <a-textarea 
              v-model:value="editForm.detailed_introduction" 
              placeholder="请输入作品详细介绍"
              :rows="6"
            />
          </a-form-item>
          
          <a-form-item label="项目地址">
            <a-input 
              v-model:value="editForm.project_url" 
              placeholder="请输入项目地址(如GitHub、官网等)"
            />
          </a-form-item>
          
          
          <a-form-item label="标签">
            <a-select
              v-model:value="editForm.tags"
              mode="tags"
              placeholder="请输入或选择标签"
              :maxTagCount="5"
            />
          </a-form-item>
          
          <a-form-item label="作品状态" required>
            <a-select
              v-model:value="editForm.status"
              placeholder="请选择作品状态"
            >
              <a-select-option value="draft">
                <a-tag color="default">草稿</a-tag>
              </a-select-option>
              <a-select-option value="published">
                <a-tag color="blue">已发布</a-tag>
              </a-select-option>
              <a-select-option value="excellent">
                <a-tag color="purple">优秀作品</a-tag>
              </a-select-option>
              <a-select-option value="archived">
                <a-tag color="red">已下架</a-tag>
              </a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="作品封面">
            <a-upload
              v-model:file-list="editAvatarFileList"
              name="avatar"
              list-type="picture-card"
              class="avatar-uploader"
              :show-upload-list="true"
              :custom-request="handleEditAvatarCustomUpload"
              :before-upload="handleAvatarBeforeUpload"
              :on-remove="handleEditAvatarRemove"
              :max-count="1"
            >
              <div v-if="editAvatarFileList.length < 1">
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
          <a-button type="primary" @click="handleEditShowcase" :loading="isEditAvatarUploading">
            确认保存
          </a-button>
        </div>
      </template>
    </a-drawer>

    <!-- 作品详情抽屉 -->
    <a-drawer
      v-model:open="showcaseDetailDrawerVisible"
      title="作品详情"
      width="600"
      :closable="true"
    >
      <div v-if="showcaseDetail" class="showcase-detail">
        <div class="detail-section">
          <h3>{{ showcaseDetail.name }}</h3>
        </div>
        
        <div v-if="showcaseDetail.avatar_url" class="detail-section">
          <h4>作品封面</h4>
          <img 
            :src="showcaseDetail.avatar_url" 
            alt="封面" 
            class="detail-cover"
          />
        </div>
        
        <div v-if="showcaseDetail.summary" class="detail-section">
          <h4>作品简介</h4>
          <p>{{ showcaseDetail.summary }}</p>
        </div>
        
        <div v-if="showcaseDetail.detailed_introduction" class="detail-section">
          <h4>详细介绍</h4>
          <div class="detail-content" v-html="showcaseDetail.detailed_introduction.replace(/\n/g, '<br>')"></div>
        </div>
        
        <div v-if="showcaseDetail.project_url" class="detail-section">
          <h4>项目地址</h4>
          <a :href="showcaseDetail.project_url" target="_blank">{{ showcaseDetail.project_url }}</a>
        </div>
        
        <div v-if="showcaseDetail.tags && showcaseDetail.tags.length" class="detail-section">
          <h4>标签</h4>
          <div class="tags-container">
            <a-tag v-for="tag in showcaseDetail.tags" :key="tag" color="blue">{{ tag }}</a-tag>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>作品信息</h4>
          <p>浏览数: {{ showcaseDetail.views_count }}</p>
          <p>点赞数: {{ showcaseDetail.likes_count }}</p>
          <p>作者ID: {{ showcaseDetail.author_id }}</p>
          <p>创建时间: {{ new Date(showcaseDetail.created_at).toLocaleString('zh-CN') }}</p>
          <p>更新时间: {{ new Date(showcaseDetail.updated_at).toLocaleString('zh-CN') }}</p>
        </div>
      </div>
    </a-drawer>

    <!-- 讨论管理抽屉 -->
    <a-drawer
      v-model:open="commentsDrawerVisible"
      :title="`${currentShowcase?.name || ''} - 讨论管理`"
      width="800"
      :closable="true"
    >
      <div class="comments-management">
        <div class="comments-header">
          <h4>评论列表 ({{ showcaseComments.length }})</h4>
        </div>
        
        <div v-if="loadingComments" class="loading-container">
          <a-spin size="large" />
          <p>加载评论中...</p>
        </div>
        
        <div v-else-if="showcaseComments.length === 0" class="empty-comments">
          <div class="empty-icon">💬</div>
          <p>暂无评论</p>
        </div>
        
        <div v-else class="comments-list">
          <div
            v-for="comment in showcaseComments"
            :key="comment.uuid"
            class="comment-item"
          >
            <!-- 评论头部 -->
            <div class="comment-header">
              <div class="comment-user">
                <strong>{{ comment.user?.username || comment.user?.real_name || '匿名用户' }}</strong>
                <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
              </div>
              <div class="comment-actions">
                <a-button 
                  size="small"
                  @click="toggleCommentExpansion(comment.uuid)"
                  :type="expandedCommentKeys.includes(comment.uuid) ? 'primary' : 'default'"
                >
                  <template #icon><EyeOutlined /></template>
                  {{ expandedCommentKeys.includes(comment.uuid) ? '收起' : '查看详情' }}
                </a-button>
                <a-button 
                  size="small" 
                  danger
                  @click="deleteShowcaseComment(comment.uuid)"
                >
                  <template #icon><DeleteOutlined /></template>
                  删除
                </a-button>
              </div>
            </div>
            
            <!-- 评论内容 -->
            <div class="comment-content">
              <p>{{ comment.content }}</p>
            </div>
            
            <!-- 评论统计 -->
            <div class="comment-stats">
              <span>点赞: {{ comment.likes_count || 0 }}</span>
              <span>回复: {{ (commentReplies[comment.uuid] || []).length }}</span>
            </div>
            
            <!-- 展开的回复区域 -->
            <div v-if="expandedCommentKeys.includes(comment.uuid)" class="replies-section">
              <div v-if="loadingReplies.has(comment.uuid)" class="loading-replies">
                <a-spin size="small" />
                <span>加载回复中...</span>
              </div>
              
              <div v-else-if="commentReplies[comment.uuid]?.length > 0" class="replies-list">
                <h5>回复列表 ({{ commentReplies[comment.uuid].length }})</h5>
                <div
                  v-for="reply in commentReplies[comment.uuid]"
                  :key="reply.uuid"
                  class="reply-item"
                >
                  <div class="reply-header">
                    <div class="reply-user">
                      <strong>{{ reply.user?.username || reply.user?.real_name || '匿名用户' }}</strong>
                      <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
                    </div>
                    <a-button 
                      size="small" 
                      danger
                      @click="deleteCommentReply(comment.uuid, reply.uuid)"
                    >
                      <template #icon><DeleteOutlined /></template>
                      删除
                    </a-button>
                  </div>
                  <div class="reply-content">
                    <p>{{ reply.content }}</p>
                  </div>
                  <div class="reply-stats">
                    <span>点赞: {{ reply.likes_count || 0 }}</span>
                  </div>
                </div>
              </div>
              
              <div v-else class="no-replies">
                <p>暂无回复</p>
              </div>
            </div>
          </div>
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
.showcase-management {
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  height: calc(100vh - 140px); /* 减去导航栏高度和额外间距，增加更多显示空间 */
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

.showcase-table {
  width: 100%;
  flex: 1;
}

.pagination-container {
  padding: 12px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fff;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: auto;
}

.cover-preview {
  width: 100px;
  height: 60px;
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
  max-width: 150px;
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
  height: 80px;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background-color: #f5f5f5;
}

:deep(.ant-table-tbody > tr > td .action-buttons) {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
  justify-content: flex-start;
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

.avatar-uploader {
  width: 160px;
  height: 90px;
}

.avatar-uploader :deep(.ant-upload-select) {
  width: 160px !important;
  height: 90px !important;
}

.upload-tip {
  margin-top: 8px;
  color: #666;
  font-size: 12px;
}

.showcase-detail {
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
  
  .tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
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

/* ==================== 讨论管理样式 ==================== */
.comments-management {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.comments-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.comments-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 16px;
}

.loading-container p {
  margin: 0;
  color: #666;
}

.empty-comments {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.comments-list {
  flex: 1;
  overflow-y: auto;
}

.comment-item {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 16px;
  padding: 16px;
  transition: all 0.2s ease;
}

.comment-item:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.comment-user {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.comment-user strong {
  color: #262626;
  font-size: 14px;
}

.comment-time {
  color: #999;
  font-size: 12px;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.comment-content {
  margin: 12px 0;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #1890ff;
}

.comment-content p {
  margin: 0;
  color: #333;
  line-height: 1.6;
  word-break: break-word;
}

.comment-stats {
  display: flex;
  gap: 16px;
  color: #666;
  font-size: 12px;
  margin-top: 8px;
}

.replies-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
  border-radius: 6px;
  padding: 16px;
}

.loading-replies {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  padding: 20px;
  color: #666;
}

.replies-list h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.reply-item {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.reply-item:last-child {
  margin-bottom: 0;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.reply-user {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.reply-user strong {
  color: #262626;
  font-size: 13px;
}

.reply-time {
  color: #999;
  font-size: 11px;
}

.reply-content {
  margin: 8px 0;
}

.reply-content p {
  margin: 0;
  color: #333;
  line-height: 1.6;
  font-size: 13px;
  word-break: break-word;
}

.reply-stats {
  color: #666;
  font-size: 11px;
  margin-top: 6px;
}

.no-replies {
  text-align: center;
  color: #999;
  padding: 20px;
  font-style: italic;
}

.no-replies p {
  margin: 0;
}
</style>
