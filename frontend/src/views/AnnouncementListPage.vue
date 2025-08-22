<template>
  <div class="announcement-list-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">最新公告</h1>
        <p class="page-desc">了解最新的课程动态和重要通知</p>
      </div>
      
      <div class="announcement-grid">
        <div 
          v-for="announcement in announcements" 
          :key="announcement.uuid"
          class="announcement-card"
          @click="goToAnnouncement(announcement.uuid)"
        >
          <div class="card-image">
            <img 
              :src="announcement.cover_url || '/images/gonggao.png'" 
              :alt="announcement.name"
              @error="handleImageError"
            >
          </div>
          <div class="card-content">
            <div class="card-date">{{ formatDate(announcement.created_at) }}</div>
            <h3 class="card-title">{{ announcement.name }}</h3>
            <p class="card-summary">{{ announcement.summary || '暂无摘要' }}</p>
            <div class="card-footer">
              <span class="read-more">阅读更多 →</span>
            </div>
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
  background-color: #f8f9fa;
  padding: 120px 0 40px; /* 增加顶部padding避免导航栏遮挡 */
}

.page-header {
  text-align: center;
  margin-bottom: 50px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.page-desc {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
}

.announcement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 40px;
  margin-bottom: 50px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.announcement-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.announcement-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-image {
  width: 100%;
  height: 250px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.announcement-card:hover .card-image img {
  transform: scale(1.05);
}

.card-content {
  padding: 25px;
}

.card-date {
  font-size: 0.9rem;
  color: #888;
  margin-bottom: 8px;
}

.card-title {
  font-size: 1.4rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-summary {
  color: #666;
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 18px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.read-more {
  color: #545ae7;
  font-weight: 500;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.announcement-card:hover .read-more {
  color: #4146d8;
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
    padding: 100px 0 20px; /* 移动端减少底部padding */
  }
  
  .announcement-grid {
    grid-template-columns: 1fr;
    gap: 25px;
    margin-bottom: 30px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 5px;
  }
  
  .page-btn {
    padding: 6px 12px;
    font-size: 0.9rem;
  }
  
  .card-image {
    height: 200px; /* 移动端稍微减小图片高度 */
  }
  
  .card-content {
    padding: 20px; /* 移动端减少padding */
  }
}
</style>