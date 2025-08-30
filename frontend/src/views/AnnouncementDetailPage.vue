<template>
  <div class="page">
    <div class="course-detail-wrapper">
    <div v-if="loading" class="loading-state">
      <p>正在加载公告详情...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchAnnouncementDetail" class="btn btn-secondary">重新加载</button>
    </div>
    
    <div v-else-if="announcementDetail" class="announcement-detail-content">
      <!-- 公告信息 -->
        <!-- 面包屑导航 -->
        <nav class="breadcrumb-nav">
          <router-link to="/announcements" class="breadcrumb-link">公告</router-link>
          <span class="breadcrumb-separator">></span>
          <span class="breadcrumb-current">{{ announcementDetail?.name }}</span>
        </nav>
        
        <div class="announcement-header">
          <div class="announcement-title-section">
            <h1 class="announcement-title">{{ announcementDetail.name }}</h1>
            <div class="announcement-meta">
              <div class="meta-group">
                <span class="meta-label">发布日期:</span>
                <span class="meta-value">{{ formatDate(announcementDetail.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="announcement-section" v-if="announcementDetail.summary">
          <h3 class="section-title">公告摘要</h3>
          <div class="section-text">
            <p>{{ announcementDetail.summary }}</p>
          </div>
        </div>
        
        <div class="announcement-section" v-if="announcementDetail.detail_info">
          <h3 class="section-title">详细内容</h3>
          <div class="section-text">
            <div v-html="formatContent(announcementDetail.detail_info)"></div>
          </div>
        </div>
        
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../api';

const route = useRoute();
const announcementDetail = ref(null);
const loading = ref(false);
const error = ref('');

// 获取公告详情
const fetchAnnouncementDetail = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    const uuid = route.params.uuid; // 从路由参数获取UUID
    if (!uuid) {
      error.value = '公告ID不存在';
      return;
    }
    
    const response = await apiClient.get(`/announcements/${uuid}`);
    if (response.data && response.data.code === 200) {
      announcementDetail.value = response.data.data;
      console.log('获取公告详情成功:', announcementDetail.value);
    } else {
      error.value = response.data?.message || '获取公告详情失败';
    }
  } catch (err) {
    console.error('获取公告详情失败:', err);
    if (err.response?.status === 404) {
      error.value = '公告不存在或已被删除';
    } else {
      error.value = '网络连接失败，请稍后重试';
    }
  } finally {
    loading.value = false;
  }
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

// 组件挂载时获取数据
onMounted(() => {
  fetchAnnouncementDetail();
});
</script>

<style scoped>
.page {
  background: #ffffff;
  min-height: 100vh;
}

.course-detail-wrapper {
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
}

/* 面包屑导航样式 */
.breadcrumb-nav {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
  font-size: 14px;
  color: #666;
  gap: 8px;
}

.breadcrumb-link {
  color: #666;
  text-decoration: none;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: #5277ff;
  text-decoration: none;
}

.breadcrumb-separator {
  color: #ccc;
  margin: 0 4px;
}

.breadcrumb-current {
  color: #333;
  font-weight: 500;
}

.loading-state, .error-state {
  text-align: center;
  padding: 80px 20px;
  color: #666;
}

.error-state p {
  margin-bottom: 20px;
  color: #e74c3c;
}

.announcement-detail-content {
  width: 100%;
}

/* 头部区域 */
.announcement-header {
  margin-bottom: 50px;
  padding-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
}

.announcement-title {
  font-size: 42px;
  color: #333;
  margin: 0 0 25px 0;
  font-weight: 700;
  line-height: 1.2;
}

.announcement-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  align-items: center;
}

.meta-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  font-size: 15px;
  color: #666;
  font-weight: 500;
}

.meta-value {
  font-size: 15px;
  color: #333;
  font-weight: 600;
}

/* 内容区域 */
.announcement-section {
  margin-bottom: 45px;
}

.section-title {
  font-size: 24px;
  color: #333;
  font-weight: 600;
  margin: 0 0 20px 0;
  padding-left: 15px;
  border-left: 4px solid #5277ff;
}

.section-text {
  margin-left: 19px;
}

.section-text p {
  color: #555;
  line-height: 1.8;
  margin: 0;
  font-size: 16px;
  text-align: justify;
}

.section-text :deep(p) {
  color: #555;
  line-height: 1.8;
  margin-bottom: 15px;
  font-size: 16px;
  text-align: justify;
}

.section-text :deep(h1),
.section-text :deep(h2),
.section-text :deep(h3) {
  margin: 30px 0 20px;
  color: #333;
  font-weight: 600;
}

.section-text :deep(ul),
.section-text :deep(ol) {
  margin: 20px 0;
  padding-left: 30px;
}

.section-text :deep(blockquote) {
  border-left: 4px solid #5277ff;
  padding-left: 20px;
  margin: 20px 0;
  color: #666;
  font-style: italic;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.btn-secondary:hover {
  background: #5a6268;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .course-detail-wrapper {
    padding: 20px;
  }
  
  .announcement-title {
    font-size: 32px;
    margin-bottom: 20px;
  }
  
  .announcement-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .section-title {
    font-size: 20px;
    margin-bottom: 15px;
  }
  
  .section-text {
    margin-left: 15px;
  }
  
  .breadcrumb-nav {
    margin-bottom: 30px;
    font-size: 13px;
    flex-wrap: wrap;
    gap: 4px;
  }
}

@media (max-width: 480px) {
  .course-detail-wrapper {
    padding: 15px;
  }
  
  .announcement-title {
    font-size: 28px;
  }
  
  .announcement-meta {
    gap: 12px;
  }
  
  .meta-group {
    font-size: 14px;
  }
  
  .section-title {
    font-size: 18px;
    padding-left: 12px;
  }
  
  .section-text {
    margin-left: 12px;
  }
}
</style>