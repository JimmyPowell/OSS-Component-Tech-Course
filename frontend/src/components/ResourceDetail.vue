<template>
  <div class="course-detail-wrapper">
    <div v-if="loading" class="loading-state">
      <p>正在加载课件详情...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchResourceDetail" class="btn btn-secondary">重新加载</button>
    </div>
    
    <div v-else-if="resourceDetail" class="course-detail-content">
      <!-- 左侧资源封面 -->
      <div class="book-cover-section">
        <div class="book-cover">
          <img :src="getResourceCover()" :alt="resourceDetail.name">
          <div v-if="isAttachment" class="file-type-overlay">
            {{ getFileExtension() }}
          </div>
        </div>
      </div>
      
      <!-- 右侧课程信息 -->
      <div class="course-info-section">
        <!-- 面包屑导航 -->
        <nav class="breadcrumb-nav">
          <router-link to="/resources" class="breadcrumb-link">课程资源</router-link>
          <span class="breadcrumb-separator">></span>
          <a @click="navigateToSection" class="breadcrumb-link clickable">{{ getResourceTypeText() }}</a>
          <span class="breadcrumb-separator">></span>
          <span class="breadcrumb-current">{{ resourceDetail?.name }}</span>
        </nav>
        
        <div class="course-header">
          <h2>{{ resourceDetail.name }}</h2>
          <div class="preview-buttons">
            <button v-if="resourceDetail.resource_url && isVideoResource" class="btn-preview" @click="previewVideo">
              <span class="iconfont icon-link"></span>
              视频预览
            </button>
            <button v-else-if="resourceDetail.resource_url && isOfficeDocument" class="btn-preview" @click="previewOfficeDocument">
              <span class="iconfont icon-link"></span>
              在线预览
            </button>
            <button v-else-if="resourceDetail.resource_url && !isAttachment" class="btn-preview" @click="previewResource">
              <span class="iconfont icon-link"></span>
              预览
            </button>
          </div>
        </div>
        
        <div class="course-info">
          <div class="meta-item">
            <span>发布者:</span>
            <span class="publisher-info">
              <img v-if="resourceDetail.publisher_avatar" :src="resourceDetail.publisher_avatar" class="avatar" alt="头像">
              {{ resourceDetail.publisher_name }}
            </span>
          </div>
          <div class="meta-item">
            <span>发布日期:</span>
            <span>{{ formatDate(resourceDetail.created_at) }}</span>
          </div>
          <div class="meta-item">
            <span>文件大小:</span>
            <span>{{ formatFileSize(resourceDetail.file_size) }}</span>
          </div>
          <div v-if="isAttachment" class="meta-item">
            <span>文件类型:</span>
            <span>{{ getFileTypeDescription() }}</span>
          </div>
          <div class="meta-item">
            <span>下载次数:</span>
            <span>{{ resourceDetail.download_count }}</span>
          </div>
        </div>
        
        <div class="course-info">
          <p><strong>{{ isAttachment ? '文件说明:' : '课程简介:' }}</strong></p>
          <p>{{ resourceDetail.description || (isAttachment ? '点击下载此附件' : '暂无描述') }}</p>
        </div>
        
        <div class="course-actions">
          <button class="btn btn-primary btn-download" @click="handleDownload" :disabled="downloading">
            <span class="iconfont icon-xiazai"></span>
            {{ downloading ? '下载中...' : `下载${getResourceTypeText()}` }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 文件大小超限提示 -->
    <Teleport to="body">
      <transition name="toast-fade">
        <div v-if="showFileSizeToast" class="toast-notification warning">
          <div class="toast-content">
            <i class="iconfont icon-warning toast-icon"></i>
            <div class="toast-message">
              <div class="toast-title">文件过大，无法预览</div>
              <div class="toast-desc">文件大小 {{ fileSizeText }}，超过10MB限制，正在为您下载...</div>
            </div>
          </div>
          <div class="toast-progress">
            <div class="toast-progress-bar" :style="{ width: toastProgress + '%' }"></div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue'
import { getCourseResourceDetail, downloadResource, incrementViewCount } from '@/api/courseResource.js';

const route = useRoute();
const router = useRouter();
const resourceDetail = ref(null);
const loading = ref(false);
const error = ref('');
const downloading = ref(false);

// Toast通知相关
const showFileSizeToast = ref(false);
const fileSizeText = ref('');
const toastProgress = ref(0);

// 计算属性
const isAttachment = computed(() => {
  return resourceDetail.value?.type === 'attachment';
});

const isVideoResource = computed(() => {
  return resourceDetail.value?.type === 'video';
});

// 判断是否为可预览的Office文档
const isOfficeDocument = computed(() => {
  if (!resourceDetail.value?.resource_url) return false;
  
  const url = resourceDetail.value.resource_url.toLowerCase();
  const mimeType = resourceDetail.value.mime_type?.toLowerCase() || '';
  
  // 检查文件扩展名
  const officeExtensions = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf'];
  const hasOfficeExtension = officeExtensions.some(ext => url.includes(ext));
  
  // 检查MIME类型
  const officeMimeTypes = [
    'application/vnd.ms-word',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/pdf'
  ];
  const hasOfficeMimeType = officeMimeTypes.some(mime => mimeType.includes(mime));
  
  return hasOfficeExtension || hasOfficeMimeType;
});

// 获取资源封面
const getResourceCover = () => {
  if (!resourceDetail.value) return '/images/book.png';
  
  if (isAttachment.value) {
    return getAttachmentIcon(resourceDetail.value.mime_type);
  }
  
  return resourceDetail.value.cover_url || '/images/book.png';
};

// 获取文件扩展名
const getFileExtension = () => {
  if (!resourceDetail.value?.name) return '';
  const parts = resourceDetail.value.name.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toUpperCase() : '';
};

// 获取文件类型描述
const getFileTypeDescription = () => {
  if (!resourceDetail.value?.mime_type) return '未知类型';
  
  const mimeType = resourceDetail.value.mime_type;
  if (mimeType.includes('pdf')) return 'PDF文档';
  if (mimeType.includes('word') || mimeType.includes('msword')) return 'Word文档';
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'Excel表格';
  if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) return 'PowerPoint演示文稿';
  if (mimeType.includes('zip') || mimeType.includes('rar')) return '压缩文件';
  if (mimeType.includes('image')) return '图片文件';
  if (mimeType.includes('text')) return '文本文件';
  
  return '附件文件';
};

// 获取资源类型文本
const getResourceTypeText = () => {
  if (!resourceDetail.value) return '文件';
  
  const resourceType = resourceDetail.value.type;
  
  if (resourceType === 'attachment') return '附件';
  if (resourceType === 'video') return '课程视频';  
  if (resourceType === 'ppt') return '课件';
  
  // 如果type为空，尝试根据文件扩展名判断
  if (!resourceType && resourceDetail.value.name) {
    const fileName = resourceDetail.value.name.toLowerCase();
    if (fileName.includes('.ppt') || fileName.includes('.pptx')) return '课件';
    if (fileName.includes('.mp4') || fileName.includes('.avi') || fileName.includes('.mov')) return '课程视频';
    if (fileName.includes('.pdf') || fileName.includes('.doc') || fileName.includes('.xls')) return '附件';
  }
  
  return '文件';
};

// 获取资源类型对应的页面区块ID
const getResourceTypeSection = () => {
  if (!resourceDetail.value) return '';
  
  const resourceType = resourceDetail.value.type;
  
  if (resourceType === 'attachment') return 'attachment-section';
  if (resourceType === 'video') return 'video-section'; 
  if (resourceType === 'ppt') return 'ppt-section';
  
  // 如果type为空，尝试根据文件扩展名判断
  if (!resourceType && resourceDetail.value.name) {
    const fileName = resourceDetail.value.name.toLowerCase();
    if (fileName.includes('.ppt') || fileName.includes('.pptx')) return 'ppt-section';
    if (fileName.includes('.mp4') || fileName.includes('.avi') || fileName.includes('.mov')) return 'video-section';
    if (fileName.includes('.pdf') || fileName.includes('.doc') || fileName.includes('.xls')) return 'attachment-section';
  }
  
  return '';
};

// 根据MIME类型获取附件图标
const getAttachmentIcon = (mimeType) => {
  if (!mimeType) return '/images/file.png';
  
  if (mimeType.includes('pdf')) return '/images/pdf.png';
  if (mimeType.includes('word') || mimeType.includes('msword')) return '/images/doc.png';
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return '/images/excel.png';
  if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) return '/images/ppt.png';
  if (mimeType.includes('zip') || mimeType.includes('rar')) return '/images/zip.png';
  if (mimeType.includes('image')) return '/images/image.png';
  
  return '/images/file.png';
};

// 获取资源详情
const fetchResourceDetail = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    const uuid = route.params.id; // 从路由参数获取UUID
    if (!uuid) {
      error.value = '资源ID不存在';
      return;
    }
    
    const response = await getCourseResourceDetail(uuid);
    if (response.success) {
      resourceDetail.value = response.data;
      // 增加播放次数统计
      await incrementViewCount(uuid);
    } else {
      error.value = response.message || '获取资源详情失败';
    }
  } catch (err) {
    console.error('获取资源详情失败:', err);
    error.value = '网络错误，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 下载资源
const handleDownload = async () => {
  try {
    downloading.value = true;
    const uuid = route.params.id;
    
    const result = await downloadResource(uuid);
    if (result.success) {
      console.log('下载开始');
    } else {
      message.error(result.message || '下载失败，请稍后重试');
    }
  } catch (error) {
    console.error('下载失败:', error);
    message.error('下载失败，请稍后重试');
  } finally {
    downloading.value = false;
  }
};

// 预览资源
const previewResource = () => {
  if (resourceDetail.value?.resource_url) {
    window.open(resourceDetail.value.resource_url, '_blank');
  }
};

// 预览视频
const previewVideo = () => {
  if (resourceDetail.value?.uuid) {
    router.push(`/resource/${resourceDetail.value.uuid}/preview`);
  }
};

// 显示文件大小超限Toast并自动下载
const showFileSizeToastAndDownload = (sizeMB, originalUrl) => {
  fileSizeText.value = `${sizeMB}MB`;
  showFileSizeToast.value = true;
  toastProgress.value = 0;
  
  // 进度条动画
  const progressInterval = setInterval(() => {
    toastProgress.value += 20;
    if (toastProgress.value >= 100) {
      clearInterval(progressInterval);
    }
  }, 200);
  
  // 自动下载文件
  setTimeout(() => {
    const link = document.createElement('a');
    link.href = originalUrl;
    link.download = resourceDetail.value.name || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, 500);
  
  // 3秒后隐藏Toast
  setTimeout(() => {
    showFileSizeToast.value = false;
  }, 3000);
};

// 预览Office文档
const previewOfficeDocument = () => {
  if (resourceDetail.value?.resource_url) {
    const originalUrl = resourceDetail.value.resource_url;
    const fileSize = resourceDetail.value.file_size || 0;
    const fileSizeMB = fileSize / (1024 * 1024);
    
    console.log('=== Office预览调试信息 ===');
    console.log('原始文件URL:', originalUrl);
    console.log('文件大小:', fileSize, 'bytes', `(${fileSizeMB.toFixed(2)} MB)`);
    console.log('========================');
    
    // 检查文件大小限制（10MB）
    if (fileSizeMB > 10) {
      showFileSizeToastAndDownload(fileSizeMB.toFixed(2), originalUrl);
      return;
    }
    
    const encodedUrl = encodeURIComponent(originalUrl);
    const isPDF = originalUrl.toLowerCase().includes('.pdf');
    
    if (isPDF) {
      // PDF直接在浏览器中打开（浏览器原生支持）
      window.open(originalUrl, '_blank');
    } else {
      // Office文档使用Microsoft Office Online预览
      const microsoftUrl = `https://view.officeapps.live.com/op/view.aspx?src=${encodedUrl}`;
      console.log('Microsoft预览链接:', microsoftUrl);
      window.open(microsoftUrl, '_blank');
    }
  } else {
    console.error('没有找到resource_url');
  }
};

// 导航到对应的资源类型区块
const navigateToSection = () => {
  const sectionId = getResourceTypeSection();
  router.push({
    path: '/resources',
    hash: sectionId ? `#${sectionId}` : ''
  });
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '未知';
  
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

// 组件挂载时获取数据
onMounted(() => {
  fetchResourceDetail();
});
</script>

<style scoped>
.course-detail-wrapper {
  padding: 60px;
  position: relative;
}

/* 面包屑导航样式 */
.breadcrumb-nav {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 13px;
  color: #999;
  gap: 6px;
}

.breadcrumb-link {
  color: #666;
  text-decoration: none;
  transition: color 0.2s ease;
  cursor: pointer;
}

.breadcrumb-link:hover,
.breadcrumb-link.clickable:hover {
  color: #5277ff;
  text-decoration: none;
}

.breadcrumb-separator {
  color: #ccc;
  font-size: 12px;
  margin: 0 2px;
}

.breadcrumb-current {
  color: #333;
  font-weight: 500;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.error-state p {
  margin-bottom: 20px;
  color: #e74c3c;
}

.course-detail-content {
  display: flex;
  gap: 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.book-cover-section {
  flex-shrink: 0;
}

.book-cover {
  width: 280px;
  height: 370px;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
  background: white;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 附件类型特殊样式 */
.book-cover img[src*="/images/pdf.png"],
.book-cover img[src*="/images/doc.png"],
.book-cover img[src*="/images/excel.png"],
.book-cover img[src*="/images/zip.png"],
.book-cover img[src*="/images/file.png"] {
  width: 120px;
  height: 120px;
  object-fit: contain;
}

.file-type-overlay {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(82, 119, 255, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(5px);
}

.course-info-section {
  flex: 1;
  padding-top: 20px;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}

.preview-buttons {
  display: flex;
  gap: 10px;
}

.course-header h2 {
  font-size: 32px;
  color: #333;
  margin: 0;
  flex: 1;
  margin-right: 20px;
  font-weight: 600;
  line-height: 1.3;
}

.btn-preview {
  background: transparent;
  border: 1px solid #5277ff;
  padding: 10px 20px;
  border-radius: 4px;
  color: #5277ff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 14px;
}

.btn-preview:hover {
  background: #5277ff;
  color: white;
}

.course-info {
  margin-bottom: 40px;
}

.meta-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 16px;
}

.meta-item > span:first-child {
  font-weight: 500;
  color: #666;
  width: 90px;
  flex-shrink: 0;
}

.publisher-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #333;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f0f0f0;
}

.course-info p {
  line-height: 1.8;
  color: #666;
  margin: 0;
  font-size: 16px;
}

.course-info p:first-child {
  font-weight: 500;
  color: #333;
  margin-bottom: 10px;
}

.course-actions {
  margin-top: 50px;
}

.btn-download {
  background: #5277ff;
  color: white;
  border: none;
  padding: 16px 40px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.btn-download:hover:not(:disabled) {
  background: #4165ee;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(82, 119, 255, 0.3);
}

.btn-download:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-secondary:hover {
  background: #5a6268;
}

/* Toast通知样式 */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 9999;
  overflow: hidden;
  border-left: 4px solid #ff9800;
}

.toast-notification.warning {
  border-left-color: #ff9800;
}

.toast-content {
  padding: 16px 20px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.toast-icon {
  color: #ff9800;
  font-size: 20px;
  margin-top: 2px;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
}

.toast-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.toast-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

.toast-progress {
  height: 3px;
  background: #f0f0f0;
  position: relative;
  overflow: hidden;
}

.toast-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #ff9800, #ffb74d);
  transition: width 0.3s ease;
  border-radius: 0 2px 2px 0;
}

/* Toast动画 */
.toast-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}

.toast-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.755, 0.05, 0.855, 0.06);
}

.toast-fade-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.toast-fade-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toast-notification {
    width: calc(100vw - 40px);
    right: 20px;
    left: 20px;
  }
  .course-detail-wrapper {
    padding: 30px 20px;
  }
  
  .breadcrumb-nav {
    margin-bottom: 20px;
    font-size: 12px;
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .breadcrumb-current {
    max-width: 180px;
  }
  
  .breadcrumb-separator {
    font-size: 11px;
  }
  
  .course-detail-content {
    flex-direction: column;
    gap: 30px;
  }
  
  .book-cover {
    width: 100%;
    max-width: 280px;
    margin: 0 auto;
    height: 320px;
  }
  
  .course-info-section {
    padding-top: 0;
  }
  
  .course-header {
    flex-direction: column;
    gap: 15px;
    margin-bottom: 30px;
  }
  
  .course-header h2 {
    font-size: 26px;
    margin-right: 0;
  }
  
  .meta-item {
    margin-bottom: 15px;
  }
  
  .meta-item > span:first-child {
    width: 80px;
  }
  
  .course-actions {
    margin-top: 30px;
  }
  
  .btn-download {
    padding: 14px 30px;
    justify-content: center;
  }
}
</style>
