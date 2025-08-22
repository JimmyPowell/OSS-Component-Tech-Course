<template>
  <div class="announcement-detail-page">
    <div class="container">
      <!-- 返回按钮 -->
      <div class="back-nav">
        <button class="back-btn" @click="goBack">
          <span class="iconfont icon-a-left"></span>
          返回公告列表
        </button>
      </div>
      
      <!-- 公告详情 -->
      <article class="announcement-detail" v-if="announcement">
        <header class="article-header">
          <h1 class="article-title">{{ announcement.name }}</h1>
          <div class="article-meta">
            <span class="publish-date">{{ formatDate(announcement.created_at) }}</span>
            <span class="publisher">发布者：管理员</span>
          </div>
        </header>
        
        <div class="article-cover" v-if="announcement.cover_url">
          <img 
            :src="announcement.cover_url" 
            :alt="announcement.name"
            @error="handleImageError"
          >
        </div>
        
        <div class="article-summary" v-if="announcement.summary">
          <p>{{ announcement.summary }}</p>
        </div>
        
        <div class="article-content">
          <div v-if="announcement.detail_info" v-html="formatContent(announcement.detail_info)"></div>
          <div v-else class="no-content">
            <p>暂无详细内容</p>
          </div>
        </div>
        
        <footer class="article-footer">
          <div class="update-time">
            最后更新：{{ formatDate(announcement.updated_at) }}
          </div>
        </footer>
      </article>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="fetchAnnouncement">重试</button>
      </div>
      
      <!-- 推荐公告 -->
      <section class="related-announcements" v-if="announcement && relatedAnnouncements.length > 0">
        <h2 class="section-title">相关公告</h2>
        <div class="related-grid">
          <div 
            v-for="related in relatedAnnouncements" 
            :key="related.uuid"
            class="related-card"
            @click="goToAnnouncement(related.uuid)"
          >
            <div class="related-image">
              <img 
                :src="related.cover_url || '/images/gonggao.png'" 
                :alt="related.name"
                @error="handleImageError"
              >
            </div>
            <div class="related-content">
              <h4 class="related-title">{{ related.name }}</h4>
              <p class="related-date">{{ formatDate(related.created_at) }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../api';

const route = useRoute();
const router = useRouter();

// 状态管理
const announcement = ref(null);
const relatedAnnouncements = ref([]);
const loading = ref(false);
const error = ref('');

// 获取公告详情
const fetchAnnouncement = async () => {
  const uuid = route.params.uuid;
  if (!uuid) {
    error.value = '公告ID不能为空';
    return;
  }
  
  loading.value = true;
  error.value = '';
  
  try {
    const response = await apiClient.get(`/announcements/${uuid}`);
    
    if (response.data && response.data.code === 200) {
      announcement.value = response.data.data;
      console.log('获取公告详情成功:', announcement.value);
      
      // 获取相关公告
      fetchRelatedAnnouncements();
    } else {
      error.value = response.data?.message || '获取公告详情失败';
    }
  } catch (err) {
    console.error('获取公告详情出错:', err);
    if (err.response?.status === 404) {
      error.value = '公告不存在或已被删除';
    } else {
      error.value = '网络连接失败，请稍后重试';
    }
  } finally {
    loading.value = false;
  }
};

// 获取相关公告
const fetchRelatedAnnouncements = async () => {
  try {
    const response = await apiClient.get('/announcements', {
      params: {
        limit: 3
      }
    });
    
    if (response.data && response.data.code === 200 && response.data.data.items) {
      // 过滤掉当前公告
      relatedAnnouncements.value = response.data.data.items
        .filter(item => item.uuid !== announcement.value?.uuid)
        .slice(0, 3);
    }
  } catch (err) {
    console.error('获取相关公告失败:', err);
  }
};

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1);
  } else {
    router.push('/announcements');
  }
};

// 跳转到其他公告
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
  return `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月${String(date.getDate()).padStart(2, '0')}日`;
};

// 格式化内容（简单的换行处理）
const formatContent = (content) => {
  if (!content) return '';
  return content.replace(/\n/g, '<br>');
};

// 组件挂载
onMounted(() => {
  fetchAnnouncement();
});
</script>

<style scoped>
.announcement-detail-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 100px 0 40px; /* 增加顶部padding避免导航栏遮挡 */
}

/* 返回导航 */
.back-nav {
  margin-bottom: 30px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border: 2px solid #545ae7;
  border-radius: 8px;
  color: #545ae7;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  box-shadow: 0 2px 8px rgba(84, 90, 231, 0.1);
}

.back-btn:hover {
  background: #545ae7;
  color: white;
  border-color: #545ae7;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(84, 90, 231, 0.2);
}

/* 公告详情 */
.announcement-detail {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 40px;
}

.article-header {
  padding: 50px 50px 30px;
  border-bottom: 1px solid #eee;
}

.article-title {
  font-size: 2.8rem;
  font-weight: bold;
  color: #333;
  line-height: 1.3;
  margin-bottom: 25px;
}

.article-meta {
  display: flex;
  gap: 30px;
  color: #666;
  font-size: 1.1rem;
}

.article-cover {
  width: 100%;
  max-height: 500px;
  overflow: hidden;
}

.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.article-summary {
  padding: 40px 50px;
  background: #f8f9fa;
  border-left: 6px solid #545ae7;
  margin: 0;
}

.article-summary p {
  font-size: 1.3rem;
  line-height: 1.7;
  color: #333;
  margin: 0;
  font-style: italic;
  font-weight: 500;
}

.article-content {
  padding: 50px;
  line-height: 1.8;
  color: #333;
  font-size: 1.2rem;
}

.article-content :deep(p) {
  margin-bottom: 20px;
  font-size: 1.2rem;
  line-height: 1.8;
}

.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3) {
  margin: 40px 0 20px;
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 20px 0;
  padding-left: 30px;
  font-size: 1.2rem;
  line-height: 1.8;
}

.article-content :deep(blockquote) {
  border-left: 6px solid #545ae7;
  padding-left: 24px;
  margin: 30px 0;
  color: #666;
  font-style: italic;
  font-size: 1.2rem;
}

.no-content {
  text-align: center;
  color: #999;
  padding: 60px 0;
  font-size: 1.2rem;
}

.article-footer {
  padding: 30px 50px;
  border-top: 1px solid #eee;
  background: #f8f9fa;
}

.update-time {
  color: #888;
  font-size: 1rem;
}

/* 加载和错误状态 */
.loading,
.error-state {
  text-align: center;
  padding: 80px 20px;
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

.error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.error-state h3 {
  color: #333;
  margin-bottom: 10px;
}

.error-state p {
  color: #666;
  margin-bottom: 20px;
}

.retry-btn {
  padding: 10px 20px;
  background: #545ae7;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.retry-btn:hover {
  background: #4146d8;
}

/* 相关公告 */
.related-announcements {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 3px solid #545ae7;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.related-card {
  display: flex;
  gap: 20px;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.related-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.related-image {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-content {
  flex: 1;
}

.related-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.related-date {
  color: #888;
  font-size: 0.95rem;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .announcement-detail-page {
    padding: 80px 0 20px; /* 移动端减少顶部padding */
  }
  
  .article-header,
  .article-content,
  .article-footer {
    padding: 30px 25px;
  }
  
  .article-summary {
    padding: 30px 25px;
  }
  
  .article-title {
    font-size: 2.2rem;
  }
  
  .article-meta {
    flex-direction: column;
    gap: 10px;
    font-size: 1rem;
  }
  
  .article-content {
    font-size: 1.1rem;
  }
  
  .article-content :deep(p) {
    font-size: 1.1rem;
  }
  
  .article-content :deep(h1),
  .article-content :deep(h2),
  .article-content :deep(h3) {
    font-size: 1.3rem;
  }
  
  .article-summary p {
    font-size: 1.2rem;
  }
  
  .related-announcements {
    padding: 30px 20px;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .related-grid {
    grid-template-columns: 1fr;
  }
  
  .related-card {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }
  
  .related-image {
    width: 100%;
    height: 180px;
    align-self: center;
  }
  
  .back-btn {
    padding: 10px 16px;
    font-size: 0.9rem;
  }
}
</style>