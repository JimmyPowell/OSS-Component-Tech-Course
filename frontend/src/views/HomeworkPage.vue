<template>
  <div class="page page-bg">
    <div class="container">
      <div class="page-title">作业任务发布墙</div>
      
      
      <div class="card-cels">
        <!-- 加载状态 -->
        <div v-if="loading && homeworkList.length === 0" class="loading">
          <div class="loading-spinner"></div>
          <span>正在加载作业列表...</span>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="!loading && homeworkList.length === 0" class="empty-state">
          <div class="empty-icon">📝</div>
          <p>暂无作业发布</p>
          <span class="empty-desc">老师还没有发布作业，请稍后查看</span>
        </div>
        
        <!-- 作业列表 -->
        <transition name="fade-slide" mode="out-in">
          <ul v-if="homeworkList.length > 0" class="row card-row" :key="pagination.currentPage">
            <li class="col-md-4" v-for="homework in homeworkList" :key="homework.uuid">
              <div class="ppt-cell" @click="viewHomeworkDetail(homework.uuid)">
                <div class="ppt-img scale">
                  <img :src="homework.cover_url || getDefaultCover()" :alt="homework.name">
                  <span class="homework-icon">作</span>
                </div>
                <div class="ppt-body">
                  <div class="card-grid mb-10">
                    <div class="card-title">{{ homework.name }}</div>
                  </div>
                  <div class="card-desc">{{ homework.description || '暂无描述' }}</div>
                </div>
              </div>
            </li>
          </ul>
        </transition>
        
        <!-- 分页 -->
        <div class="pagination-cell flex-center" v-if="pagination.total > pagination.limit">
          <a @click="changePage(pagination.currentPage - 1)" 
             :class="['pagination-btn', { disabled: pagination.currentPage <= 1 }]">
            <span class="iconfont icon-l-left"></span>
          </a>
          <a v-for="page in getPaginationPages()" 
             :key="page"
             @click="changePage(page)"
             :class="['pagination-btn', { active: page === pagination.currentPage }]">
            {{ page }}
          </a>
          <a @click="changePage(pagination.currentPage + 1)"
             :class="['pagination-btn', { disabled: pagination.currentPage >= Math.ceil(pagination.total / pagination.limit) }]">
            <span class="iconfont icon-l-right"></span>
          </a>
          <div class="pagination-info flex-center">
            <span>跳至</span>
            <input type="text" 
                   class="form-control pagination-input"
                   v-model="jumpPage"
                   @keyup.enter="jumpToPage">
            <span>页</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getHomeworkList, formatDuration, formatDate } from '@/api/homework.js';

const router = useRouter();

// 响应式数据
const homeworkList = ref([]);
const loading = ref(false);
const jumpPage = ref('');

// 分页数据
const pagination = reactive({
  currentPage: 1,
  limit: 9,
  total: 0
});

// 获取作业列表
const fetchHomeworkList = async () => {
  try {
    loading.value = true;
    const response = await getHomeworkList({
      skip: (pagination.currentPage - 1) * pagination.limit,
      limit: pagination.limit
    });
    
    if (response.success) {
      homeworkList.value = response.data.items || [];
      pagination.total = response.data.total || 0;
    } else {
      console.error('获取作业列表失败:', response.message);
      homeworkList.value = [];
    }
  } catch (error) {
    console.error('获取作业列表失败:', error);
    homeworkList.value = [];
  } finally {
    loading.value = false;
  }
};


// 分页切换
const changePage = (page) => {
  const maxPage = Math.ceil(pagination.total / pagination.limit);
  if (page >= 1 && page <= maxPage && page !== pagination.currentPage) {
    pagination.currentPage = page;
    fetchHomeworkList();
  }
};

// 跳转到指定页面
const jumpToPage = () => {
  const page = parseInt(jumpPage.value);
  if (!isNaN(page)) {
    changePage(page);
    jumpPage.value = '';
  }
};

// 生成分页页码数组
const getPaginationPages = () => {
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

// 获取默认封面图
const getDefaultCover = () => {
  const workImages = ['work1', 'work2', 'work3', 'work4'];
  const randomIndex = Math.floor(Math.random() * workImages.length);
  return `/images/${workImages[randomIndex]}.png`;
};

// 查看作业详情
const viewHomeworkDetail = (uuid) => {
  router.push(`/homework/${uuid}`);
};

// 下载资源文件
const downloadResources = (resourceUrls) => {
  if (!resourceUrls || resourceUrls.length === 0) return;
  
  resourceUrls.forEach((url, index) => {
    setTimeout(() => {
      const link = document.createElement('a');
      link.href = url;
      link.download = `resource_${index + 1}`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }, index * 500); // 延迟下载，避免浏览器阻止多个下载
  });
};

// 组件挂载时加载数据
onMounted(() => {
  fetchHomeworkList();
});
</script>

<style scoped>

/* 作业卡片样式 */
.ppt-cell {
  transition: all 0.3s ease;
  cursor: pointer;
}

.ppt-cell:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.homework-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(82, 119, 255, 0.9);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

/* 加载状态 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #5277ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.empty-state p {
  font-size: 18px;
  color: #666;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #999;
}

/* 分页按钮禁用状态 */
.pagination-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
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

/* 列表项动画 */
.card-row li {
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

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-section {
    margin: 20px;
    padding: 15px;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .homework-card .card-img {
    height: 160px;
  }
  
  .card-content {
    padding: 15px;
  }
  
  .homework-info {
    flex-direction: column;
    gap: 8px;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .btn {
    justify-content: center;
  }
}
</style>
