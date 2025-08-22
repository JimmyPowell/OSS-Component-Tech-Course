<template>
  <div class="page page-bg">
    <div class="container">
      <div class="page-title" id="ppt-section">课程课件</div>
      <div class="card-cels">
        <div v-if="pptLoading && pptResources.length === 0" class="loading">
          <div class="loading-spinner"></div>
          <span>正在加载课件资源...</span>
        </div>
        <div v-else-if="!pptLoading && pptResources.length === 0" class="empty-state">
          <p>暂无课件资源</p>
        </div>
        <transition name="fade-slide" mode="out-in">
          <ul v-if="pptResources.length > 0" class="row card-row" :key="pptPagination.currentPage">
            <li class="col-md-4" v-for="ppt in pptResources" :key="ppt.uuid">
              <router-link :to="`/resource/${ppt.uuid}`">
                <div class="ppt-cell">
                  <div class="ppt-img scale">
                    <img :src="ppt.cover_url || '/images/ppt.png'" alt="">
                  </div>
                  <div class="ppt-body">
                    <div class="card-grid mb-10">
                      <div class="card-title">{{ ppt.name }}</div>
                    </div>
                    <div class="card-desc">{{ ppt.description || '暂无描述' }}</div>
                  </div>
                </div>
              </router-link>
            </li>
          </ul>
        </transition>
        <div class="pagination-cell flex-center" v-if="pptPagination.total > pptPagination.limit">
          <a @click="changePptPage(pptPagination.currentPage - 1)" 
             :class="['pagination-btn', { disabled: pptPagination.currentPage <= 1 }]">
            <span class="iconfont icon-l-left"></span>
          </a>
          <a v-for="page in getPaginationPages(pptPagination)" 
             :key="page"
             @click="changePptPage(page)"
             :class="['pagination-btn', { active: page === pptPagination.currentPage }]">
            {{ page }}
          </a>
          <a @click="changePptPage(pptPagination.currentPage + 1)"
             :class="['pagination-btn', { disabled: pptPagination.currentPage >= Math.ceil(pptPagination.total / pptPagination.limit) }]">
            <span class="iconfont icon-l-right"></span>
          </a>
          <div class="pagination-info flex-center">
            <span>跳至</span>
            <input type="text" 
                   class="form-control pagination-input"
                   v-model="pptJumpPage"
                   @keyup.enter="jumpToPptPage">
            <span>页</span>
          </div>
        </div>
      </div>
      <div class="attachment-cells">
        <div class="attachment-title" id="attachment-section">附件</div>
        <div v-if="attachmentLoading && attachmentResources.length === 0" class="loading">
          <div class="loading-spinner"></div>
          <span>正在加载附件资源...</span>
        </div>
        <div v-else-if="!attachmentLoading && attachmentResources.length === 0" class="empty-state">
          <p>暂无附件资源</p>
        </div>
        <transition name="fade-slide" mode="out-in">
          <ul v-if="attachmentResources.length > 0" class="row" :key="attachmentPagination.currentPage">
            <li class="col-md-6" v-for="attachment in attachmentResources" :key="attachment.uuid">
              <router-link :to="`/resource/${attachment.uuid}`" class="attachment-link">
                <div class="attachment-cell">
                  <div class="attachment-icon">
                    <img :src="getAttachmentIcon(attachment.mime_type)" alt="">
                  </div>
                  <div class="flex-col">
                    <div class="card-grid mb-10">
                      <div class="card-title">{{ attachment.name }}</div>
                    </div>
                    <div class="card-desc">{{ attachment.description || '点击查看详情' }}</div>
                    <div class="attachment-info">
                      <span v-if="attachment.file_size">大小: {{ formatFileSize(attachment.file_size) }}</span>
                      <span>下载次数: {{ attachment.download_count }}</span>
                    </div>
                  </div>
                </div>
              </router-link>
            </li>
          </ul>
        </transition>
        <div class="pagination-cell flex-center" v-if="attachmentPagination.total > attachmentPagination.limit">
          <a @click="changeAttachmentPage(attachmentPagination.currentPage - 1)" 
             :class="['pagination-btn', { disabled: attachmentPagination.currentPage <= 1 }]">
            <span class="iconfont icon-l-left"></span>
          </a>
          <a v-for="page in getPaginationPages(attachmentPagination)" 
             :key="page"
             @click="changeAttachmentPage(page)"
             :class="['pagination-btn', { active: page === attachmentPagination.currentPage }]">
            {{ page }}
          </a>
          <a @click="changeAttachmentPage(attachmentPagination.currentPage + 1)"
             :class="['pagination-btn', { disabled: attachmentPagination.currentPage >= Math.ceil(attachmentPagination.total / attachmentPagination.limit) }]">
            <span class="iconfont icon-l-right"></span>
          </a>
          <div class="pagination-info flex-center">
            <span>跳至</span>
            <input type="text" 
                   class="form-control pagination-input"
                   v-model="attachmentJumpPage"
                   @keyup.enter="jumpToAttachmentPage">
            <span>页</span>
          </div>
        </div>
      </div>
      <div class="page-title" id="video-section">在线课程视频</div>
      <div class="card-cels">
        <div v-if="videoLoading && videoResources.length === 0" class="loading">
          <div class="loading-spinner"></div>
          <span>正在加载视频资源...</span>
        </div>
        <div v-else-if="!videoLoading && videoResources.length === 0" class="empty-state">
          <p>暂无视频资源</p>
        </div>
        <transition name="fade-slide" mode="out-in">
          <ul v-if="videoResources.length > 0" class="row card-row" :key="videoPagination.currentPage">
            <li class="col-md-4" v-for="video in videoResources" :key="video.uuid">
              <router-link :to="`/resource/${video.uuid}`">
                <div class="ppt-cell">
                  <div class="ppt-img scale">
                    <img :src="video.cover_url || `/images/show${Math.floor(Math.random() * 3) + 2}.png`" alt="">
                    <span class="v-icon"></span>
                  </div>
                  <div class="ppt-body">
                    <div class="card-grid mb-10">
                      <div class="card-title">{{ video.name }}</div>
                    </div>
                    <div class="card-desc">{{ video.description || '精彩视频内容，点击观看' }}</div>
                  </div>
                </div>
              </router-link>
            </li>
          </ul>
        </transition>
        <div class="pagination-cell flex-center" v-if="videoPagination.total > videoPagination.limit">
          <a @click="changeVideoPage(videoPagination.currentPage - 1)" 
             :class="['pagination-btn', { disabled: videoPagination.currentPage <= 1 }]">
            <span class="iconfont icon-l-left"></span>
          </a>
          <a v-for="page in getPaginationPages(videoPagination)" 
             :key="page"
             @click="changeVideoPage(page)"
             :class="['pagination-btn', { active: page === videoPagination.currentPage }]">
            {{ page }}
          </a>
          <a @click="changeVideoPage(videoPagination.currentPage + 1)"
             :class="['pagination-btn', { disabled: videoPagination.currentPage >= Math.ceil(videoPagination.total / videoPagination.limit) }]">
            <span class="iconfont icon-l-right"></span>
          </a>
          <div class="pagination-info flex-center">
            <span>跳至</span>
            <input type="text" 
                   class="form-control pagination-input"
                   v-model="videoJumpPage"
                   @keyup.enter="jumpToVideoPage">
            <span>页</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue';
import { 
  getPptResources, 
  getVideoResources, 
  getAttachmentResources
} from '@/api/courseResource.js';

// 响应式数据
const pptResources = ref([]);
const videoResources = ref([]);
const attachmentResources = ref([]);

// 分页数据
const pptPagination = reactive({
  currentPage: 1,
  limit: 6,
  total: 0
});

const videoPagination = reactive({
  currentPage: 1,
  limit: 9,
  total: 0
});

const attachmentPagination = reactive({
  currentPage: 1,
  limit: 6,
  total: 0
});

// 页面跳转输入
const pptJumpPage = ref('');
const videoJumpPage = ref('');
const attachmentJumpPage = ref('');

// 加载状态
const pptLoading = ref(false);
const videoLoading = ref(false);
const attachmentLoading = ref(false);

// 获取课件资源
const fetchPptResources = async () => {
  try {
    pptLoading.value = true;
    const response = await getPptResources({
      skip: (pptPagination.currentPage - 1) * pptPagination.limit,
      limit: pptPagination.limit
    });
    
    if (response.success) {
      pptResources.value = response.data.items || [];
      pptPagination.total = response.data.total || 0;
    }
  } catch (error) {
    console.error('获取课件资源失败:', error);
    pptResources.value = [];
  } finally {
    pptLoading.value = false;
  }
};

// 获取视频资源
const fetchVideoResources = async () => {
  try {
    videoLoading.value = true;
    const response = await getVideoResources({
      skip: (videoPagination.currentPage - 1) * videoPagination.limit,
      limit: videoPagination.limit
    });
    
    if (response.success) {
      videoResources.value = response.data.items || [];
      videoPagination.total = response.data.total || 0;
    }
  } catch (error) {
    console.error('获取视频资源失败:', error);
    videoResources.value = [];
  } finally {
    videoLoading.value = false;
  }
};

// 获取附件资源
const fetchAttachmentResources = async () => {
  try {
    attachmentLoading.value = true;
    const response = await getAttachmentResources({
      skip: (attachmentPagination.currentPage - 1) * attachmentPagination.limit,
      limit: attachmentPagination.limit
    });
    
    if (response.success) {
      attachmentResources.value = response.data.items || [];
      attachmentPagination.total = response.data.total || 0;
    }
  } catch (error) {
    console.error('获取附件资源失败:', error);
    attachmentResources.value = [];
  } finally {
    attachmentLoading.value = false;
  }
};

// 课件分页切换
const changePptPage = (page) => {
  const maxPage = Math.ceil(pptPagination.total / pptPagination.limit);
  if (page >= 1 && page <= maxPage && page !== pptPagination.currentPage) {
    pptPagination.currentPage = page;
    fetchPptResources();
  }
};

// 视频分页切换
const changeVideoPage = (page) => {
  const maxPage = Math.ceil(videoPagination.total / videoPagination.limit);
  if (page >= 1 && page <= maxPage && page !== videoPagination.currentPage) {
    videoPagination.currentPage = page;
    fetchVideoResources();
  }
};

// 跳转到指定页面（课件）
const jumpToPptPage = () => {
  const page = parseInt(pptJumpPage.value);
  if (!isNaN(page)) {
    changePptPage(page);
    pptJumpPage.value = '';
  }
};

// 跳转到指定页面（视频）
const jumpToVideoPage = () => {
  const page = parseInt(videoJumpPage.value);
  if (!isNaN(page)) {
    changeVideoPage(page);
    videoJumpPage.value = '';
  }
};

// 附件分页切换
const changeAttachmentPage = (page) => {
  const maxPage = Math.ceil(attachmentPagination.total / attachmentPagination.limit);
  if (page >= 1 && page <= maxPage && page !== attachmentPagination.currentPage) {
    attachmentPagination.currentPage = page;
    fetchAttachmentResources();
  }
};

// 跳转到指定页面（附件）
const jumpToAttachmentPage = () => {
  const page = parseInt(attachmentJumpPage.value);
  if (!isNaN(page)) {
    changeAttachmentPage(page);
    attachmentJumpPage.value = '';
  }
};

// 生成分页页码数组
const getPaginationPages = (pagination) => {
  const maxPage = Math.ceil(pagination.total / pagination.limit);
  const currentPage = pagination.currentPage;
  const pages = [];
  
  let startPage = Math.max(1, currentPage - 2);
  let endPage = Math.min(maxPage, currentPage + 2);
  
  // 确保总是显示5页（如果有足够的页数）
  if (endPage - startPage < 4) {
    if (startPage === 1) {
      endPage = Math.min(maxPage, 5);
    } else if (endPage === maxPage) {
      startPage = Math.max(1, maxPage - 4);
    }
  }
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  
  return pages;
};


// 根据MIME类型获取附件图标
const getAttachmentIcon = (mimeType) => {
  if (!mimeType) return '/images/pdf.png';
  
  if (mimeType.includes('pdf')) return '/images/pdf.png';
  if (mimeType.includes('word') || mimeType.includes('msword')) return '/images/doc.png';
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return '/images/excel.png';
  if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) return '/images/ppt.png';
  if (mimeType.includes('zip') || mimeType.includes('rar')) return '/images/zip.png';
  
  return '/images/pdf.png'; // 默认图标
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '';
  
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

// 处理锚点跳转
const handleAnchorScroll = () => {
  const hash = window.location.hash;
  if (hash) {
    setTimeout(() => {
      const element = document.querySelector(hash);
      if (element) {
        // 计算目标位置，留出一些顶部空间
        const elementRect = element.getBoundingClientRect();
        const offset = window.pageYOffset + elementRect.top - 50; // 距离顶部50px
        
        window.scrollTo({
          top: offset,
          behavior: 'smooth'
        });
        
        // 高亮目标区域
        setTimeout(() => {
          element.style.transition = 'background-color 0.3s ease';
          element.style.backgroundColor = '#f8f9ff';
          setTimeout(() => {
            element.style.backgroundColor = '';
          }, 1000);
        }, 300);
      }
    }, 300);
  }
};

// 组件挂载时加载数据
onMounted(() => {
  fetchPptResources();
  fetchVideoResources();
  fetchAttachmentResources();
  
  // 处理初始锚点跳转
  handleAnchorScroll();
  
  // 监听hash变化
  window.addEventListener('hashchange', handleAnchorScroll);
});

// 组件卸载时清理事件监听器
onUnmounted(() => {
  window.removeEventListener('hashchange', handleAnchorScroll);
});
</script>

<style scoped>
/* 平滑滚动 */
html {
  scroll-behavior: smooth;
}

/* 锚点目标样式 */
#ppt-section, #attachment-section, #video-section {
  scroll-margin-top: 30px;
  position: relative;
}

/* 确保附件标题有足够的上边距 */
.attachment-title {
  margin-top: 40px;
  margin-bottom: 30px;
}

/* 分页按钮禁用状态 */
.pagination-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* 附件信息样式 */
.attachment-info {
  display: flex;
  gap: 15px;
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}

/* 附件链接样式 */
.attachment-link {
  text-decoration: none;
  color: inherit;
  display: block;
  margin-bottom: 15px;
}

.attachment-link:hover {
  text-decoration: none;
  color: inherit;
}

/* 附件单元格悬停效果 */
.attachment-cell {
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  background: #f9f9f9;
}

.attachment-link:hover .attachment-cell {
  background: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* 加载状态样式 */
.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}


/* 页面切换动画 */
.fade-slide-enter-active {
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.55, 0.085, 0.68, 0.53);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.95);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-15px) scale(1.02);
}

/* 为列表容器添加固定最小高度，避免高度变化 */
.card-cels, .attachment-cells {
  min-height: 400px;
  position: relative;
}

/* 列表项动画 */
.card-row li, .row li {
  animation: slideInUp 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(30px);
}

.card-row li:nth-child(1) { animation-delay: 0.1s; }
.card-row li:nth-child(2) { animation-delay: 0.2s; }
.card-row li:nth-child(3) { animation-delay: 0.3s; }
.card-row li:nth-child(4) { animation-delay: 0.4s; }
.card-row li:nth-child(5) { animation-delay: 0.5s; }
.card-row li:nth-child(6) { animation-delay: 0.6s; }
.card-row li:nth-child(7) { animation-delay: 0.7s; }
.card-row li:nth-child(8) { animation-delay: 0.8s; }
.card-row li:nth-child(9) { animation-delay: 0.9s; }

@keyframes slideInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 加载动画 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

.loading-spinner.small {
  width: 24px;
  height: 24px;
  border-width: 2px;
  margin-bottom: 0;
}

/* 加载遮罩 */
.loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  backdrop-filter: blur(5px);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 分页按钮动画增强 */
.pagination-btn {
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* 卡片悬停动画优化 */
.ppt-cell,
.card-cell {
  transition: all 0.3s ease;
}

.ppt-cell:hover,
.card-cell:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .attachment-cell {
    flex-direction: column;
    text-align: center;
  }
  
  .attachment-icon {
    margin-bottom: 10px;
  }
  
  .pagination-info {
    margin-top: 10px;
  }
  
  .fade-slide-enter-from,
  .fade-slide-leave-to {
    transform: translateY(10px);
  }
}
</style>
