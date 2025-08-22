<template>
  <div class="page">
    <div class="course-detail-wrapper">
    <div v-if="loading" class="loading-state">
      <p>正在加载作业详情...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchHomeworkDetail" class="btn btn-secondary">重新加载</button>
    </div>
    
    <div v-else-if="homeworkDetail" class="homework-detail-content">
      <!-- 作业信息 -->
        <!-- 面包屑导航 -->
        <nav class="breadcrumb-nav">
          <router-link to="/homework" class="breadcrumb-link">作业墙</router-link>
          <span class="breadcrumb-separator">></span>
          <span class="breadcrumb-current">{{ homeworkDetail?.name }}</span>
        </nav>
        
        <div class="homework-header">
          <div class="homework-title-section">
            <h1 class="homework-title">{{ homeworkDetail.name }}</h1>
            <div class="homework-meta">
              <div class="meta-group" v-if="homeworkDetail.publisher_name">
                <span class="meta-label">发布者:</span>
                <span class="publisher-info">
                  <img v-if="homeworkDetail.publisher_avatar" :src="homeworkDetail.publisher_avatar" class="avatar" alt="头像">
                  {{ homeworkDetail.publisher_name }}
                </span>
              </div>
              <div class="meta-group">
                <span class="meta-label">发布日期:</span>
                <span class="meta-value">{{ formatDate(homeworkDetail.created_at) }}</span>
              </div>
              <div class="meta-group" v-if="homeworkDetail.lasting_time">
                <span class="meta-label">持续时间:</span>
                <span class="meta-value">{{ formatDuration(homeworkDetail.lasting_time) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="homework-section" v-if="homeworkDetail.description">
          <h3 class="section-title">作业描述</h3>
          <div class="section-text">
            <p>{{ homeworkDetail.description }}</p>
          </div>
        </div>
        
        <div class="homework-section" v-if="homeworkDetail.content">
          <h3 class="section-title">详细内容</h3>
          <div class="section-text">
            <p>{{ homeworkDetail.content }}</p>
          </div>
        </div>
        
        <div class="course-actions" v-if="homeworkDetail.resource_urls && homeworkDetail.resource_urls.length > 0">
          <button class="btn btn-primary btn-download" @click="downloadResources" :disabled="downloading">
            <span class="iconfont icon-xiazai"></span>
            {{ downloading ? '下载中...' : `下载资源文件 (${homeworkDetail.resource_urls.length}个)` }}
          </button>
        </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getHomeworkDetail, formatDuration, formatDate } from '@/api/homework.js';

const route = useRoute();
const homeworkDetail = ref(null);
const loading = ref(false);
const error = ref('');
const downloading = ref(false);


// 获取作业详情
const fetchHomeworkDetail = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    const uuid = route.params.id; // 从路由参数获取UUID
    if (!uuid) {
      error.value = '作业ID不存在';
      return;
    }
    
    const response = await getHomeworkDetail(uuid);
    if (response.success) {
      homeworkDetail.value = response.data;
    } else {
      error.value = response.message || '获取作业详情失败';
    }
  } catch (err) {
    console.error('获取作业详情失败:', err);
    error.value = '网络错误，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 下载资源文件
const downloadResources = () => {
  if (!homeworkDetail.value?.resource_urls || homeworkDetail.value.resource_urls.length === 0) return;
  
  downloading.value = true;
  
  homeworkDetail.value.resource_urls.forEach((url, index) => {
    setTimeout(() => {
      const link = document.createElement('a');
      link.href = url;
      link.download = `homework_resource_${index + 1}`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // 最后一个文件下载完成后恢复按钮状态
      if (index === homeworkDetail.value.resource_urls.length - 1) {
        setTimeout(() => {
          downloading.value = false;
        }, 500);
      }
    }, index * 500); // 延迟下载，避免浏览器阻止多个下载
  });
};

// 组件挂载时获取数据
onMounted(() => {
  fetchHomeworkDetail();
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

.homework-detail-content {
  width: 100%;
}

/* 头部区域 */
.homework-header {
  margin-bottom: 50px;
  padding-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
}

.homework-title {
  font-size: 42px;
  color: #333;
  margin: 0 0 25px 0;
  font-weight: 700;
  line-height: 1.2;
}

.homework-meta {
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

.publisher-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #333;
  font-weight: 600;
}

.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f0f0f0;
}

/* 内容区域 */
.homework-section {
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

/* 操作按钮区域 */
.course-actions {
  margin-top: 50px;
  padding-top: 30px;
  border-top: 2px solid #f0f0f0;
  text-align: center;
}

.btn-download {
  background: #5277ff;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
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
  
  .homework-title {
    font-size: 32px;
    margin-bottom: 20px;
  }
  
  .homework-meta {
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
  
  .btn-download {
    padding: 12px 24px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .course-detail-wrapper {
    padding: 15px;
  }
  
  .homework-title {
    font-size: 28px;
  }
  
  .homework-meta {
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