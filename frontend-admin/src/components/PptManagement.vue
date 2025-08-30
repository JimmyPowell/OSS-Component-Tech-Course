<script setup>
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue';
import { SearchOutlined, PlusOutlined, SettingOutlined, FileTextOutlined, UploadOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import request from '../utils/request';

const resources = ref([]);
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
const editingResource = ref(null);
const editForm = reactive({
  name: '',
  description: '',
  cover_url: '',
  resource_url: '',
  file_size: null,
  mime_type: ''
});

// 添加资源抽屉
const addResourceDrawerVisible = ref(false);
const addResourceForm = reactive({
  name: '',
  type: 'ppt',
  description: '',
  cover_url: '',
  resource_url: '',
  file_size: null,
  mime_type: 'application/vnd.ms-powerpoint'
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

// 资源详情抽屉
const resourceDetailDrawerVisible = ref(false);
const resourceDetail = ref(null);

// 列设置
const columnSettingsVisible = ref(false);
const availableColumns = [
  { key: 'cover_url', title: '封面预览', visible: true },
  { key: 'name', title: '课件名称', visible: true },
  { key: 'uuid', title: '课件编号', visible: false },
  { key: 'description', title: '课件描述', visible: true },
  { key: 'status', title: '状态', visible: true },
  { key: 'file_size', title: '文件大小', visible: true },
  { key: 'download_count', title: '下载次数', visible: true },
  { key: 'creator_id', title: '发布者ID', visible: false },
  { key: 'created_at', title: '发布时间', visible: true },
  { key: 'updated_at', title: '更新时间', visible: false }
];
const columnSettings = reactive([...availableColumns]);

// 表格高度自适应
const tableHeight = ref(600);

const API_BASE_URL = 'http://localhost:8000/api/v1/admin/course-resources';

// 状态选项
const statusOptions = [
  { label: '未发布', value: 'draft' },
  { label: '已发布', value: 'published' }
];

const fetchResources = async (page = 1, pageSize = 20, search = '') => {
  loading.value = true;
  try {
    const skip = (page - 1) * pageSize;
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: pageSize.toString(),
      resource_type: 'ppt'
    });
    
    if (search) {
      params.append('name', search);
    }

    const response = await request.get(`${API_BASE_URL}?${params}`);

    if (response.data.code === 200) {
      const data = response.data.data;
      resources.value = data.items;
      pagination.total = data.total;
      pagination.current = page;
    } else {
      message.error(response.data.message || '获取PPT列表失败');
    }
  } catch (error) {
    console.error('Failed to fetch resources:', error);
    message.error('获取PPT列表失败');
  } finally {
    loading.value = false;
  }
};

const addNewResource = () => {
  Object.assign(addResourceForm, {
    name: '',
    type: 'ppt',
    description: '',
    cover_url: '',
    resource_url: '',
    file_size: null,
    mime_type: 'application/vnd.ms-powerpoint'
  });
  fileList.value = [];
  uploadProgress.value = 0;
  isUploading.value = false;
  
  // 重置封面图相关状态
  coverFileList.value = [];
  coverUploadProgress.value = 0;
  isCoverUploading.value = false;
  
  addResourceDrawerVisible.value = true;
};

const refreshList = () => {
  fetchResources(pagination.current, pagination.pageSize, searchValue.value);
};

// 文件上传前的验证
const handleBeforeUpload = (file) => {
  const isPPT = file.type === 'application/vnd.ms-powerpoint' || 
                file.type === 'application/vnd.openxmlformats-officedocument.presentationml.presentation' ||
                file.type === 'application/pdf';
  
  if (!isPPT) {
    message.error('只能上传 PPT、PPTX 或 PDF 文件!');
    return false;
  }
  
  const isLt50M = file.size / 1024 / 1024 < 50;
  if (!isLt50M) {
    message.error('文件大小不能超过 50MB!');
    return false;
  }
  
  return true; // 允许上传，将使用custom-request处理
};

// 移除文件
const handleRemoveFile = (file) => {
  addResourceForm.resource_url = '';
  addResourceForm.file_size = null;
  addResourceForm.mime_type = 'application/vnd.ms-powerpoint';
  uploadProgress.value = 0;
  return true;
};

// 获取七牛云上传token和配置信息
const getQiniuUploadToken = async (fileKey, purpose) => {
  try {
    console.log('请求上传token，参数:', { file_key: fileKey, purpose });
    
    const response = await request.post('http://localhost:8000/api/v1/qiniu/admin/upload-token', {
      file_key: fileKey,
      purpose: purpose
    });
    
    console.log('后端响应:', response.data);
    
    if (response.data.code === 201) {
      const data = response.data.data;
      console.log('获取到token:', data.token.substring(0, 50) + '...');
      console.log('上传域名:', data.upload_domain);
      console.log('下载域名:', data.download_domain);
      
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
    if (error.response) {
      console.error('错误状态:', error.response.status);
      console.error('错误数据:', error.response.data);
    }
    throw error;
  }
};


// 自定义上传到七牛云
const handleCustomUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  console.log('开始上传文件:', file.name);
  
  try {
    isUploading.value = true;
    uploadProgress.value = 0;
    
    // 更新文件列表为上传中状态
    fileList.value = [{
      uid: file.uid,
      name: file.name,
      status: 'uploading',
      percent: 0
    }];
    
    // 生成文件key
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `ppt/${timestamp}_${randomStr}.${fileExtension}`;
    
    console.log('生成的文件key:', fileKey);
    
    // 获取上传token和配置信息
    const tokenInfo = await getQiniuUploadToken(fileKey, `PPT文件上传: ${file.name}`);
    console.log('获取到上传token和配置信息');
    
    // 上传到七牛云 - 按照官方文档格式
    const formData = new FormData();
    formData.append('key', fileKey);  // 资源名
    formData.append('token', tokenInfo.token);  // 上传凭证
    formData.append('file', file, file.name);  // 文件（确保包含文件名）
    
    console.log('FormData内容:');
    console.log('key:', fileKey);
    console.log('token (完整):', tokenInfo.token);
    console.log('token (前50字符):', tokenInfo.token.substring(0, 50) + '...');
    console.log('file:', file.name, file.size);
    console.log('上传URL:', tokenInfo.upload_domain);
    
    // 验证token格式
    const tokenParts = tokenInfo.token.split(':');
    console.log('Token部分数量:', tokenParts.length);
    console.log('Access Key:', tokenParts[0]);
    console.log('Signature长度:', tokenParts[1]?.length);
    console.log('Policy长度:', tokenParts[2]?.length);
    
    const xhr = new XMLHttpRequest();
    
    // 不要手动设置Content-Type，让浏览器自动设置multipart/form-data
    // xhr.setRequestHeader('Content-Type', 'multipart/form-data'); // 不要这样做
    
    // 监听上传进度
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        uploadProgress.value = percent;
        
        // 更新文件列表进度
        fileList.value = [{
          uid: file.uid,
          name: file.name,
          status: 'uploading',
          percent: percent
        }];
        
        // 调用ant-design的进度回调
        if (onProgress) {
          onProgress({ percent });
        }
      }
    });
    
    // 上传完成处理
    xhr.addEventListener('load', () => {
      console.log('=== 七牛云响应详情 ===');
      console.log('HTTP状态码:', xhr.status);
      console.log('响应头:', xhr.getAllResponseHeaders());
      console.log('响应体:', xhr.responseText);
      console.log('========================');
      
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          console.log('上传成功，七牛云返回:', result);
          
          // 设置文件信息到表单
          addResourceForm.resource_url = `${tokenInfo.download_domain}/${result.key}`;
          addResourceForm.file_size = file.size;
          addResourceForm.mime_type = file.type;
          
          // 如果名称为空，自动设置
          if (!addResourceForm.name) {
            addResourceForm.name = file.name.replace(/\.[^/.]+$/, '');
          }
          
          uploadProgress.value = 100;
          message.success('文件上传成功');
          
          // 更新文件列表状态
          fileList.value = [{
            uid: file.uid,
            name: file.name,
            status: 'done',
            url: addResourceForm.resource_url,
            percent: 100
          }];
          
          // 调用ant-design的成功回调
          if (onSuccess) {
            onSuccess(result, file);
          }
          
        } catch (parseError) {
          console.error('解析响应失败:', parseError);
          console.error('原始响应:', xhr.responseText);
          message.error('服务器响应格式错误');
          fileList.value = [];
          if (onError) {
            onError(parseError);
          }
        }
      } else {
        // 尝试解析错误响应
        let errorMessage = `HTTP ${xhr.status}`;
        try {
          const errorResponse = JSON.parse(xhr.responseText);
          console.error('七牛云错误响应:', errorResponse);
          if (errorResponse.error) {
            errorMessage = `${xhr.status}: ${errorResponse.error}`;
          }
        } catch (e) {
          console.error('无法解析错误响应为JSON:', xhr.responseText);
          errorMessage = `${xhr.status}: ${xhr.responseText || '未知错误'}`;
        }
        
        console.error('上传失败:', errorMessage);
        message.error(`文件上传失败: ${errorMessage}`);
        fileList.value = [];
        if (onError) {
          onError(new Error(errorMessage));
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
      fileList.value = [];
      if (onError) {
        onError(error);
      }
    });
    
    // 发送请求到七牛云 - 使用从后端获取的上传域名
    xhr.open('POST', tokenInfo.upload_domain);
    
    // 添加调试信息
    console.log('即将发送请求到:', tokenInfo.upload_domain);
    console.log('请求方法: POST');
    console.log('FormData字段数量:', Array.from(formData.entries()).length);
    
    xhr.send(formData);
    
  } catch (error) {
    console.error('上传失败:', error);
    message.error(error.message || '文件上传失败');
    isUploading.value = false;
    uploadProgress.value = 0;
    fileList.value = [];
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
  addResourceForm.cover_url = '';
  coverUploadProgress.value = 0;
  return true;
};

// 自定义封面图上传到七牛云
const handleCustomCoverUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  console.log('开始上传封面图:', file.name);
  
  try {
    isCoverUploading.value = true;
    coverUploadProgress.value = 0;
    
    // 更新文件列表为上传中状态
    coverFileList.value = [{
      uid: file.uid,
      name: file.name,
      status: 'uploading',
      percent: 0
    }];
    
    // 生成文件key
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `ppt/cover/${timestamp}_${randomStr}.${fileExtension}`;
    
    console.log('生成的封面图文件key:', fileKey);
    
    // 获取上传token和配置信息
    const tokenInfo = await getQiniuUploadToken(fileKey, `封面图上传: ${file.name}`);
    console.log('获取到封面图上传token和配置信息');
    
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
        coverUploadProgress.value = percent;
        
        // 更新文件列表进度
        coverFileList.value = [{
          uid: file.uid,
          name: file.name,
          status: 'uploading',
          percent: percent
        }];
        
        // 调用ant-design的进度回调
        if (onProgress) {
          onProgress({ percent });
        }
      }
    });
    
    // 上传完成处理
    xhr.addEventListener('load', () => {
      console.log('=== 封面图七牛云响应详情 ===');
      console.log('HTTP状态码:', xhr.status);
      console.log('响应体:', xhr.responseText);
      console.log('========================');
      
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          console.log('封面图上传成功，七牛云返回:', result);
          
          // 设置封面图URL到表单
          addResourceForm.cover_url = `${tokenInfo.download_domain}/${result.key}`;
          
          coverUploadProgress.value = 100;
          message.success('封面图上传成功');
          
          // 更新文件列表状态
          coverFileList.value = [{
            uid: file.uid,
            name: file.name,
            status: 'done',
            url: addResourceForm.cover_url,
            percent: 100
          }];
          
          // 调用ant-design的成功回调
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
    
    // 上传错误处理
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
    
    // 发送请求到七牛云
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

// 编辑时的文件上传前验证
const handleEditBeforeUpload = (file) => {
  const isPPT = file.type === 'application/vnd.ms-powerpoint' || 
                file.type === 'application/vnd.openxmlformats-officedocument.presentationml.presentation' ||
                file.type === 'application/pdf';
  
  if (!isPPT) {
    message.error('只能上传 PPT、PPTX 或 PDF 文件!');
    return false;
  }
  
  const isLt50M = file.size / 1024 / 1024 < 50;
  if (!isLt50M) {
    message.error('文件大小不能超过 50MB!');
    return false;
  }
  
  return true;
};

// 编辑时移除文件
const handleEditRemoveFile = (file) => {
  editForm.resource_url = '';
  editForm.file_size = null;
  editForm.mime_type = 'application/vnd.ms-powerpoint';
  editUploadProgress.value = 0;
  return true;
};

// 编辑时的自定义文件上传到七牛云
const handleEditCustomUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  console.log('开始上传编辑文件:', file.name);
  
  try {
    isEditUploading.value = true;
    editUploadProgress.value = 0;
    
    // 更新文件列表为上传中状态
    editFileList.value = [{
      uid: file.uid,
      name: file.name,
      status: 'uploading',
      percent: 0
    }];
    
    // 生成文件key
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `ppt/${timestamp}_${randomStr}.${fileExtension}`;
    
    console.log('生成的编辑文件key:', fileKey);
    
    // 获取上传token和配置信息
    const tokenInfo = await getQiniuUploadToken(fileKey, `PPT文件编辑上传: ${file.name}`);
    console.log('获取到编辑文件上传token和配置信息');
    
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
        editUploadProgress.value = percent;
        
        // 更新文件列表进度
        editFileList.value = [{
          uid: file.uid,
          name: file.name,
          status: 'uploading',
          percent: percent
        }];
        
        // 调用ant-design的进度回调
        if (onProgress) {
          onProgress({ percent });
        }
      }
    });
    
    // 上传完成处理
    xhr.addEventListener('load', () => {
      console.log('=== 编辑文件七牛云响应详情 ===');
      console.log('HTTP状态码:', xhr.status);
      console.log('响应体:', xhr.responseText);
      console.log('========================');
      
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          console.log('编辑文件上传成功，七牛云返回:', result);
          
          // 设置文件信息到表单
          editForm.resource_url = `${tokenInfo.download_domain}/${result.key}`;
          editForm.file_size = file.size;
          editForm.mime_type = file.type;
          
          editUploadProgress.value = 100;
          message.success('文件上传成功');
          
          // 更新文件列表状态
          editFileList.value = [{
            uid: file.uid,
            name: file.name,
            status: 'done',
            url: editForm.resource_url,
            percent: 100
          }];
          
          // 调用ant-design的成功回调
          if (onSuccess) {
            onSuccess(result, file);
          }
          
        } catch (parseError) {
          console.error('解析编辑文件响应失败:', parseError);
          message.error('服务器响应格式错误');
          editFileList.value = [];
          if (onError) {
            onError(parseError);
          }
        }
      } else {
        console.error('编辑文件上传失败:', xhr.status);
        message.error(`文件上传失败: HTTP ${xhr.status}`);
        editFileList.value = [];
        if (onError) {
          onError(new Error(`HTTP ${xhr.status}`));
        }
      }
      isEditUploading.value = false;
    });
    
    // 上传错误处理
    xhr.addEventListener('error', (error) => {
      console.error('编辑文件上传网络错误:', error);
      message.error('文件上传失败');
      isEditUploading.value = false;
      editUploadProgress.value = 0;
      editFileList.value = [];
      if (onError) {
        onError(error);
      }
    });
    
    // 发送请求到七牛云
    xhr.open('POST', tokenInfo.upload_domain);
    xhr.send(formData);
    
  } catch (error) {
    console.error('编辑文件上传失败:', error);
    message.error(error.message || '文件上传失败');
    isEditUploading.value = false;
    editUploadProgress.value = 0;
    editFileList.value = [];
    if (onError) {
      onError(error);
    }
  }
};

// 编辑时的封面图上传前验证
const handleEditCoverBeforeUpload = (file) => {
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

// 编辑时移除封面图文件
const handleEditRemoveCoverFile = (file) => {
  editForm.cover_url = '';
  editCoverUploadProgress.value = 0;
  return true;
};

// 编辑时的自定义封面图上传到七牛云
const handleEditCustomCoverUpload = async (options) => {
  const { file, onProgress, onSuccess, onError } = options;
  
  console.log('开始上传编辑封面图:', file.name);
  
  try {
    isEditCoverUploading.value = true;
    editCoverUploadProgress.value = 0;
    
    // 更新文件列表为上传中状态
    editCoverFileList.value = [{
      uid: file.uid,
      name: file.name,
      status: 'uploading',
      percent: 0
    }];
    
    // 生成文件key
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const fileExtension = file.name.split('.').pop();
    const fileKey = `ppt/cover/${timestamp}_${randomStr}.${fileExtension}`;
    
    console.log('生成的编辑封面图文件key:', fileKey);
    
    // 获取上传token和配置信息
    const tokenInfo = await getQiniuUploadToken(fileKey, `编辑封面图上传: ${file.name}`);
    console.log('获取到编辑封面图上传token和配置信息');
    
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
        editCoverUploadProgress.value = percent;
        
        // 更新文件列表进度
        editCoverFileList.value = [{
          uid: file.uid,
          name: file.name,
          status: 'uploading',
          percent: percent
        }];
        
        // 调用ant-design的进度回调
        if (onProgress) {
          onProgress({ percent });
        }
      }
    });
    
    // 上传完成处理
    xhr.addEventListener('load', () => {
      console.log('=== 编辑封面图七牛云响应详情 ===');
      console.log('HTTP状态码:', xhr.status);
      console.log('响应体:', xhr.responseText);
      console.log('========================');
      
      if (xhr.status === 200) {
        try {
          const result = JSON.parse(xhr.responseText);
          console.log('编辑封面图上传成功，七牛云返回:', result);
          
          // 设置封面图URL到表单
          editForm.cover_url = `${tokenInfo.download_domain}/${result.key}`;
          
          editCoverUploadProgress.value = 100;
          message.success('封面图上传成功');
          
          // 更新文件列表状态
          editCoverFileList.value = [{
            uid: file.uid,
            name: file.name,
            status: 'done',
            url: editForm.cover_url,
            percent: 100
          }];
          
          // 调用ant-design的成功回调
          if (onSuccess) {
            onSuccess(result, file);
          }
          
        } catch (parseError) {
          console.error('解析编辑封面图响应失败:', parseError);
          message.error('服务器响应格式错误');
          editCoverFileList.value = [];
          if (onError) {
            onError(parseError);
          }
        }
      } else {
        console.error('编辑封面图上传失败:', xhr.status);
        message.error(`封面图上传失败: HTTP ${xhr.status}`);
        editCoverFileList.value = [];
        if (onError) {
          onError(new Error(`HTTP ${xhr.status}`));
        }
      }
      isEditCoverUploading.value = false;
    });
    
    // 上传错误处理
    xhr.addEventListener('error', (error) => {
      console.error('编辑封面图上传网络错误:', error);
      message.error('封面图上传失败');
      isEditCoverUploading.value = false;
      editCoverUploadProgress.value = 0;
      editCoverFileList.value = [];
      if (onError) {
        onError(error);
      }
    });
    
    // 发送请求到七牛云
    xhr.open('POST', tokenInfo.upload_domain);
    xhr.send(formData);
    
  } catch (error) {
    console.error('编辑封面图上传失败:', error);
    message.error(error.message || '封面图上传失败');
    isEditCoverUploading.value = false;
    editCoverUploadProgress.value = 0;
    editCoverFileList.value = [];
    if (onError) {
      onError(error);
    }
  }
};

const configSettings = () => {
  columnSettingsVisible.value = true;
};

const searchResource = () => {
  pagination.current = 1;
  fetchResources(1, pagination.pageSize, searchValue.value);
};

const resetSearch = () => {
  searchValue.value = '';
  pagination.current = 1;
  fetchResources(1, pagination.pageSize, '');
};

const handleTableChange = (page, pageSize) => {
  pagination.current = page;
  pagination.pageSize = pageSize;
  fetchResources(page, pageSize, searchValue.value);
};

const viewResource = async (uuid) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${uuid}`);
    
    if (response.data.code === 200) {
      resourceDetail.value = response.data.data;
      resourceDetailDrawerVisible.value = true;
    }
  } catch (error) {
    message.error('获取PPT详情失败');
  }
};

const editResource = async (uuid) => {
  try {
    const response = await request.get(`${API_BASE_URL}/${uuid}`);
    
    if (response.data.code === 200) {
      const resource = response.data.data;
      editingResource.value = resource;
      editForm.name = resource.name;
      editForm.description = resource.description || '';
      editForm.cover_url = resource.cover_url || '';
      editForm.resource_url = resource.resource_url;
      editForm.file_size = resource.file_size;
      editForm.mime_type = resource.mime_type || '';
      
      // 重置编辑时的上传状态
      editFileList.value = [];
      editUploadProgress.value = 0;
      isEditUploading.value = false;
      
      editCoverFileList.value = [];
      editCoverUploadProgress.value = 0;
      isEditCoverUploading.value = false;
      
      // 如果有现有的封面图，在列表中显示
      if (resource.cover_url) {
        editCoverFileList.value = [{
          uid: '-1',
          name: '当前封面图',
          status: 'done',
          url: resource.cover_url
        }];
      }
      
      editDrawerVisible.value = true;
    }
  } catch (error) {
    message.error('获取PPT信息失败');
  }
};

const handleEditSubmit = async () => {
  try {
    const response = await request.put(`${API_BASE_URL}/${editingResource.value.uuid}`, editForm);
    
    if (response.data.code === 200) {
      message.success('PPT信息更新成功');
      editDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '更新失败');
    }
  } catch (error) {
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('更新PPT信息失败');
    }
  }
};

const deleteResource = (uuid) => {
  const resource = resources.value.find(r => r.uuid === uuid);
  
  Modal.confirm({
    title: '确认删除PPT',
    content: `确定要删除PPT "${resource.name}" 吗？此操作不可恢复！`,
    okType: 'danger',
    onOk: async () => {
      try {
        const response = await request.delete(`${API_BASE_URL}/${uuid}`);
        
        if (response.data.code === 200) {
          message.success('PPT删除成功');
          refreshList();
        } else {
          message.error(response.data.message || '删除失败');
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error('删除PPT失败');
        }
      }
    }
  });
};

// 添加PPT
const handleAddResource = async () => {
  // 验证必填字段
  if (!addResourceForm.name.trim()) {
    message.error('请输入PPT名称');
    return;
  }
  
  if (!addResourceForm.resource_url) {
    message.error('请先上传PPT文件');
    return;
  }
  
  if (isUploading.value) {
    message.error('文件正在上传中，请稍候...');
    return;
  }

  try {
    const response = await request.post(API_BASE_URL, addResourceForm);
    
    if (response.data.code === 200) {
      message.success('PPT创建成功');
      addResourceDrawerVisible.value = false;
      refreshList();
    } else {
      message.error(response.data.message || '创建失败');
    }
  } catch (error) {
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('创建PPT失败');
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

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '-';
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

// 计算表格高度 - 默认填满可用高度，数据超出时滚动
const calculateTableHeight = () => {
  const windowHeight = window.innerHeight;
  const navbarHeight = 60;
  const pageHeaderHeight = 80;
  const actionBarHeight = 70;
  const paginationHeight = 60;
  const padding = 40;
  
  // 表格始终填满可用高度，与侧边栏底部对齐
  const availableHeight = windowHeight - navbarHeight - pageHeaderHeight - actionBarHeight - paginationHeight - padding;
  
  // 直接使用可用高度作为表格高度，让表格内部滚动处理数据超出的情况
  tableHeight.value = Math.max(availableHeight, 400);
};

// 监听窗口大小变化和数据变化
const resizeObserver = new ResizeObserver(calculateTableHeight);

onMounted(() => {
  fetchResources();
  calculateTableHeight();
  
  window.addEventListener('resize', calculateTableHeight);
  
  const contentContainer = document.querySelector('.content-container');
  if (contentContainer) {
    resizeObserver.observe(contentContainer);
  }
});

// 切换课件状态
const toggleResourceStatus = async (uuid, currentStatus) => {
  const newStatus = currentStatus === 'published' ? 'draft' : 'published';
  const statusText = newStatus === 'published' ? '发布' : '下架';
  
  Modal.confirm({
    title: `确认${statusText}课件`,
    content: `确定要${statusText}这个课件吗？`,
    onOk: async () => {
      try {
        const response = await request.put(`${API_BASE_URL}/${uuid}/status`, {
          status: newStatus
        });
        
        if (response.data.code === 200) {
          message.success(`课件${statusText}成功`);
          refreshList();
        } else {
          message.error(response.data.message || `${statusText}失败`);
        }
      } catch (error) {
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else {
          message.error(`${statusText}课件失败`);
        }
      }
    }
  });
};

// 高度只需要监听窗口变化，不需要监听数据变化

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight);
  resizeObserver.disconnect();
});
</script>

<template>
  <div class="resource-management">
    <div class="page-header">
      <h1 class="page-title">课件PPT管理</h1>
      <p class="page-subtitle">查看、编辑系统中的PPT课件</p>
    </div>
    
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="addNewResource">
          <template #icon><PlusOutlined /></template>
          添加PPT
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
          placeholder="PPT名称"
          class="search-input rounded-input"
          allow-clear
        />
        <a-button type="primary" class="search-btn" @click="searchResource">
          查询
        </a-button>
        <a-button class="reset-btn" @click="resetSearch">
          重置
        </a-button>
      </div>
    </div>
    
    <div class="table-container">
      <a-table 
        :dataSource="resources" 
        :pagination="false"
        :loading="loading"
        @change="handleTableChange"
        class="resource-table"
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
              <img v-if="record.cover_url" :src="record.cover_url" alt="PPT封面" />
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
          <template v-else-if="column.key === 'file_size'">
            {{ formatFileSize(record.file_size) }}
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
      <a-table-column key="action" title="操作" width="280" fixed="right">
        <template #default="{ record }">
          <div class="action-buttons">
            <a-button size="small" @click="viewResource(record.uuid)">查看</a-button>
            <a-button size="small" type="primary" @click="editResource(record.uuid)">编辑</a-button>
            <a-button 
              size="small" 
              :type="record.status === 'published' ? 'default' : 'primary'"
              @click="toggleResourceStatus(record.uuid, record.status)"
              style="margin-right: 4px;"
            >
              {{ record.status === 'published' ? '下架' : '发布' }}
            </a-button>
            <a-button size="small" danger @click="deleteResource(record.uuid)">删除</a-button>
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

    <!-- 编辑PPT抽屉 -->
    <a-drawer
      v-model:open="editDrawerVisible"
      title="编辑课程PPT信息"
      width="480"
      placement="left"
      @close="editDrawerVisible = false"
      :maskClosable="true"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="更换PPT文件">
          <a-upload
            v-model:file-list="editFileList"
            name="file"
            :multiple="false"
            :before-upload="handleEditBeforeUpload"
            :remove="handleEditRemoveFile"
            accept=".ppt,.pptx,.pdf"
            :custom-request="handleEditCustomUpload"
            :show-upload-list="true"
            :max-count="1"
          >
            <a-button>
              <template #icon><upload-outlined /></template>
              重新上传文件
            </a-button>
          </a-upload>
          <div v-if="editUploadProgress > 0 && editUploadProgress < 100" style="margin-top: 8px;">
            <a-progress :percent="editUploadProgress" />
          </div>
          <div style="margin-top: 4px; font-size: 12px; color: #666;">
            如需更换PPT文件，请重新上传。支持 PPT、PPTX、PDF 格式，文件大小不超过 50MB
          </div>
        </a-form-item>
        <a-form-item label="PPT名称" required>
          <a-input v-model:value="editForm.name" placeholder="请输入PPT名称" />
        </a-form-item>
        <a-form-item label="更换封面图">
          <a-upload
            v-model:file-list="editCoverFileList"
            name="cover"
            :multiple="false"
            :before-upload="handleEditCoverBeforeUpload"
            :remove="handleEditRemoveCoverFile"
            accept="image/*"
            :custom-request="handleEditCustomCoverUpload"
            :show-upload-list="true"
            :max-count="1"
            list-type="picture"
            class="cover-upload-rectangle"
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
        <a-form-item label="PPT描述">
          <a-textarea v-model:value="editForm.description" placeholder="请输入PPT描述" :rows="3" />
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

    <!-- 添加PPT抽屉 -->
    <a-drawer
      v-model:open="addResourceDrawerVisible"
      title="添加PPT"
      width="480"
      placement="left"
      @close="addResourceDrawerVisible = false"
      :maskClosable="true"
    >
      <a-form :model="addResourceForm" layout="vertical">
        <a-form-item label="上传PPT文件" required>
          <a-upload
            v-model:file-list="fileList"
            name="file"
            :multiple="false"
            :before-upload="handleBeforeUpload"
            :remove="handleRemoveFile"
            accept=".ppt,.pptx,.pdf"
            :custom-request="handleCustomUpload"
            :show-upload-list="true"
            :max-count="1"
          >
            <a-button>
              <template #icon><upload-outlined /></template>
              上传文件
            </a-button>
          </a-upload>
          <div v-if="uploadProgress > 0 && uploadProgress < 100" style="margin-top: 8px;">
            <a-progress :percent="uploadProgress" />
          </div>
        </a-form-item>
        <a-form-item label="PPT名称" required>
          <a-input v-model:value="addResourceForm.name" placeholder="请输入PPT名称" />
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
            list-type="picture"
            class="cover-upload-rectangle"
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
        <a-form-item label="PPT描述">
          <a-textarea v-model:value="addResourceForm.description" placeholder="请输入PPT描述" :rows="3" />
        </a-form-item>
      </a-form>
      
      <template #footer>
        <div style="text-align: right;">
          <a-button @click="addResourceDrawerVisible = false" style="margin-right: 8px;">
            取消
          </a-button>
          <a-button type="primary" @click="handleAddResource">
            确定
          </a-button>
        </div>
      </template>
    </a-drawer>

    <!-- PPT详情抽屉 -->
    <a-drawer
      v-model:open="resourceDetailDrawerVisible"
      title="PPT详情"
      width="480"
      placement="left"
      :maskClosable="true"
    >
      <div v-if="resourceDetail" class="resource-detail">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="PPT名称">
            {{ resourceDetail.name }}
          </a-descriptions-item>
          <a-descriptions-item label="PPT编号">
            {{ resourceDetail.uuid }}
          </a-descriptions-item>
          <a-descriptions-item label="PPT描述">
            {{ resourceDetail.description || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="文件大小">
            {{ formatFileSize(resourceDetail.file_size) }}
          </a-descriptions-item>
          <a-descriptions-item label="MIME类型">
            {{ resourceDetail.mime_type || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="下载次数">
            {{ resourceDetail.download_count }}
          </a-descriptions-item>
          <a-descriptions-item label="发布者ID">
            {{ resourceDetail.creator_id }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ new Date(resourceDetail.created_at).toLocaleString('zh-CN') }}
          </a-descriptions-item>
          <a-descriptions-item label="更新时间">
            {{ new Date(resourceDetail.updated_at).toLocaleString('zh-CN') }}
          </a-descriptions-item>
          <a-descriptions-item label="封面预览" v-if="resourceDetail.cover_url">
            <img :src="resourceDetail.cover_url" alt="PPT封面" style="max-width: 200px; max-height: 150px;" />
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
.resource-management {
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

.resource-table {
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
  width: 240px;
  height: 135px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

/* 长方形封面上传样式 */
.cover-upload-rectangle :deep(.ant-upload) {
  width: 240px !important;
  height: 135px !important;
  border-radius: 8px;
}

.cover-upload-rectangle :deep(.ant-upload-select) {
  width: 240px !important;
  height: 135px !important;
  border-radius: 8px;
  border: 2px dashed #d9d9d9;
  background-color: #fafafa;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-upload-rectangle :deep(.ant-upload-select:hover) {
  border-color: #1890ff;
  background-color: #f0f8ff;
}

.cover-upload-rectangle :deep(.ant-upload-list-item) {
  width: 240px !important;
  height: 135px !important;
  border-radius: 8px;
}

.cover-upload-rectangle :deep(.ant-upload-list-picture .ant-upload-list-item-thumbnail img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 隐藏文件名显示 */
.cover-upload-rectangle :deep(.ant-upload-list-picture .ant-upload-list-item-name) {
  display: none !important;
}

/* 隐藏文件操作按钮，只在图片上显示 */
.cover-upload-rectangle :deep(.ant-upload-list-picture .ant-upload-list-item-actions) {
  background: rgba(0, 0, 0, 0.5);
}

/* 确保上传区域内容居中 */
.cover-upload-rectangle :deep(.ant-upload-select > div) {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}
</style>