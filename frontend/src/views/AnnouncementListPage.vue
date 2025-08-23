<template>
  <div class="announcement-list-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <h1 class="page-title">
            <i class="title-icon">📢</i>
            最新公告
          </h1>
          <p class="page-desc">了解最新的课程动态和重要通知</p>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="container">
      <div class="announcement-list">
        <div 
          v-for="announcement in announcements" 
          :key="announcement.uuid"
          class="announcement-item"
          @click="goToAnnouncement(announcement.uuid)"
        >
          <div class="item-image">
            <img 
              :src="announcement.cover_url || '/images/gonggao.png'" 
              :alt="announcement.name"
              @error="handleImageError"
            >
          </div>
          <div class="item-content">
            <div class="item-date">{{ formatDate(announcement.created_at) }}</div>
            <h3 class="item-title">{{ announcement.name }}</h3>
            <p class="item-summary">{{ announcement.summary || '暂无摘要' }}</p>
          </div>
          <div class="item-action">
            <span class="read-more">阅读更多 →</span>
          </div>
        </div>
      </div>
      
      <!-- 分页组件 -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          上一页
        </button>
        
        <div class="page-numbers">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            class="page-number"
            :class="{ active: page === currentPage }"
            @click="changePage(page)"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          class="page-btn" 
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          下一页
        </button>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <!-- 空状态 -->
      <div v-if="!loading && announcements.length === 0" class="empty-state">
        <div class="empty-icon">📢</div>
        <h3>暂无公告</h3>
        <p>目前还没有发布任何公告，请稍后再来查看。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api';

const router = useRouter();

// 状态管理
const announcements = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(12);
const total = ref(0);

// 计算属性
const totalPages = computed(() => Math.ceil(total.value / pageSize.value));
const visiblePages = computed(() => {
  const pages = [];
  const start = Math.max(1, currentPage.value - 2);
  const end = Math.min(totalPages.value, currentPage.value + 2);
  
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  
  return pages;
});

// 获取公告列表
const fetchAnnouncements = async (page = 1) => {
  loading.value = true;
  try {
    const response = await apiClient.get('/announcements', {
      params: {
        skip: (page - 1) * pageSize.value,
        limit: pageSize.value
      }
    });
    
    if (response.data && response.data.code === 200) {
      announcements.value = response.data.data.items || [];
      total.value = response.data.data.total || 0;
      console.log('获取公告列表成功:', announcements.value.length, '条记录');
    } else {
      console.error('获取公告列表失败:', response.data);
      announcements.value = [];
      total.value = 0;
    }
  } catch (error) {
    console.error('获取公告列表出错:', error);
    announcements.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

// 切换页面
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// 跳转到公告详情
const goToAnnouncement = (uuid) => {
  router.push(`/announcements/${uuid}`);
};

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.src = '/images/gonggao.png';
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
};

// 监听页面变化
watch(currentPage, (newPage) => {
  fetchAnnouncements(newPage);
});

// 组件挂载
onMounted(() => {
  fetchAnnouncements(1);
});
</script>

<style scoped>
.announcement-list-page {
  min-height: 100vh;
  background: #f6f7f9; /* 与讨论中心保持一致的背景色 */
  padding-top: 80px; /* 避免被导航栏遮挡 */
}

/* 页面头部 */
.page-header {
  background: #ffffff; /* 白色背景 */
  border-bottom: 1px solid #e3e5e8; /* 与讨论中心一致的底边框 */
  padding: 2rem 0; /* 与讨论中心一致的padding */
  margin-bottom: 0; /* 无底边距，紧贴内容 */
  margin-top: -80px; /* 抵消页面的padding-top，使头部紧贴导航栏 */
  padding-top: calc(2rem + 80px); /* 在原有padding基础上加上80px以保持内容位置 */
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 12px; /* 增加间距 */
}

.page-title {
  display: flex;
  align-items: center;
  gap: 15px; /* 增加图标和文字间距 */
  font-size: 2.8rem; /* 显著增大标题字体 */
  font-weight: 700; /* 增加字重 */
  color: #333;
  margin: 0;
}

.title-icon {
  font-size: 2.5rem; /* 增大图标 */
}

.page-desc {
  font-size: 1.3rem; /* 增大描述字体 */
  color: #666;
  margin: 0;
  font-weight: 500;
}

/* 确保主要内容区域与页面头部紧挨着 */
.announcement-list-page .container {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

/* 公告列表 */
.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 50px;
  margin-top: 30px; /* 适当增加顶部边距，与公告标题栏保持合适距离 */
}

.announcement-item {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 15px; /* 增大圆角 */
  padding: 30px; /* 增大内边距 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 增强阴影 */
  transition: all 0.3s ease;
  cursor: pointer;
  min-height: 150px; /* 增加最小高度 */
}

.announcement-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.item-image {
  flex-shrink: 0;
  width: 180px; /* 增大图片宽度 */
  height: 110px; /* 增大图片高度 */
  border-radius: 10px;
  overflow: hidden;
  margin-right: 30px; /* 增大右边距 */
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.announcement-item:hover .item-image img {
  transform: scale(1.05);
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px; /* 增加间距 */
  min-height: 110px;
  justify-content: center;
}

.item-date {
  font-size: 1.1rem; /* 显著增大日期字体 */
  color: #888;
  font-weight: 600;
}

.item-title {
  font-size: 1.8rem; /* 大幅增大标题字体 */
  font-weight: 700; /* 增加字重 */
  color: #333;
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-summary {
  color: #666;
  font-size: 1.2rem; /* 增大摘要字体 */
  line-height: 1.6;
  margin: 0;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-action {
  flex-shrink: 0;
  margin-left: 25px; /* 增大左边距 */
}

.read-more {
  color: #545ae7;
  font-weight: 600;
  font-size: 1.1rem; /* 增大按钮字体 */
  transition: all 0.3s ease;
  padding: 12px 20px; /* 增大按钮padding */
  border-radius: 25px;
  background: rgba(84, 90, 231, 0.1);
}

.announcement-item:hover .read-more {
  color: #4146d8;
  background: rgba(84, 90, 231, 0.15);
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin: 40px 0;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  color: #666;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #545ae7;
  color: white;
  border-color: #545ae7;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 5px;
}

.page-number {
  width: 36px;
  height: 36px;
  border: 1px solid #ddd;
  background: white;
  color: #666;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-number:hover {
  background: #545ae7;
  color: white;
  border-color: #545ae7;
}

.page-number.active {
  background: #545ae7;
  color: white;
  border-color: #545ae7;
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #545ae7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #333;
  margin-bottom: 10px;
}

.empty-state p {
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .announcement-list-page {
    padding-top: 70px; /* 移动端减少顶部padding */
  }
  
  .page-header {
    padding: 20px 0;
  }
  
  .page-title {
    font-size: 2.2rem; /* 移动端稍微减小但仍然较大 */
  }
  
  .title-icon {
    font-size: 2rem;
  }
  
  .page-desc {
    font-size: 1.1rem;
  }
  
  .announcement-item {
    flex-direction: column;
    align-items: stretch;
    padding: 25px; /* 保持较大的padding */
    min-height: auto;
  }
  
  .item-image {
    width: 100%;
    height: 150px; /* 移动端增大图片高度 */
    margin-right: 0;
    margin-bottom: 20px;
  }
  
  .item-content {
    min-height: auto;
    text-align: center;
    gap: 15px;
  }
  
  .item-date {
    font-size: 1rem;
  }
  
  .item-title {
    font-size: 1.6rem; /* 移动端保持较大字体 */
  }
  
  .item-summary {
    font-size: 1.1rem; /* 移动端保持较大字体 */
  }
  
  .item-action {
    margin-left: 0;
    margin-top: 15px;
    text-align: center;
  }
  
  .read-more {
    font-size: 1rem;
    padding: 10px 18px;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .page-btn {
    padding: 8px 15px;
    font-size: 1rem; /* 增大分页按钮字体 */
  }
}
</style>