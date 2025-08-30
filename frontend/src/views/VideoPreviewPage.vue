<template>
  <div class="video-preview-page">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载视频...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchVideoDetail" class="btn btn-secondary">重新加载</button>
    </div>
    
    <div v-else-if="videoDetail" class="video-content">
      <!-- 面包屑导航 -->
      <nav class="breadcrumb-nav">
        <router-link to="/resources" class="breadcrumb-link">课程资源</router-link>
        <span class="breadcrumb-separator">></span>
        <a @click="navigateToVideoSection" class="breadcrumb-link clickable">课程视频</a>
        <span class="breadcrumb-separator">></span>
        <span class="breadcrumb-current">{{ videoDetail?.name }}</span>
      </nav>

      <!-- 主要内容区域 -->
      <div class="main-content">
        <!-- 视频播放区域 -->
        <div class="video-section">
          <!-- 返回按钮 -->
          <button @click="goBack" class="back-button">
            <span class="iconfont icon-l-left"></span>
            <span>返回</span>
          </button>
          <!-- 视频播放器区域 -->
          <div class="video-player-wrapper" style="margin-top: -5px;">
            <div class="video-player">
              <video
                ref="videoRef"
                :src="videoDetail.resource_url"
                :poster="videoDetail.cover_url"
                @timeupdate="handleTimeUpdate"
                @loadedmetadata="handleLoadedMetadata"
                @play="handlePlay"
                @pause="handlePause"
                @click="togglePlay"
                class="video-element"
                controls
              >
                您的浏览器不支持视频播放
              </video>

              <!-- 自定义视频控制条 (可选，现在先使用原生controls) -->
              <div v-if="false" class="video-controls">
                <!-- 播放进度条 -->
                <div class="progress-bar" @click="handleProgressClick">
                  <div class="progress-track">
                    <div 
                      class="progress-fill" 
                      :style="{ width: progressPercent + '%' }"
                    ></div>
                  </div>
                </div>

                <!-- 控制按钮 -->
                <div class="control-buttons">
                  <div class="left-controls">
                    <button @click="togglePlay" class="control-btn">
                      <span v-if="isPlaying">⏸</span>
                      <span v-else>▶</span>
                    </button>
                    <span class="time-display">
                      {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
                    </span>
                  </div>

                  <div class="right-controls">
                    <button @click="toggleMute" class="control-btn">
                      <span v-if="isMuted">🔇</span>
                      <span v-else>🔊</span>
                    </button>
                    <button @click="toggleFullscreen" class="control-btn">
                      ⛶
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 视频信息 -->
          <div class="video-info">
            <div class="video-meta">
              <h2 class="video-title">{{ videoDetail.name }}</h2>
              <div class="video-details">
                <div class="detail-item">
                  <span>发布者:</span>
                  <span class="publisher-info">
                    <img v-if="videoDetail.publisher_avatar" :src="videoDetail.publisher_avatar" class="avatar" alt="头像">
                    {{ videoDetail.publisher_name }}
                  </span>
                </div>
                <div class="detail-item">
                  <span>发布日期:</span>
                  <span>{{ formatDate(videoDetail.created_at) }}</span>
                </div>
                <div class="detail-item">
                  <span>文件大小:</span>
                  <span>{{ formatFileSize(videoDetail.file_size) }}</span>
                </div>
                <div class="detail-item">
                  <span>观看次数:</span>
                  <span>{{ videoDetail.download_count }}</span>
                </div>
              </div>

              <!-- 视频描述 -->
              <div v-if="videoDetail.description" class="video-description">
                <p><strong>视频简介:</strong></p>
                <p>{{ videoDetail.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI助手圆球按钮 -->
    <div class="ai-assistant-button" @click="toggleAIChat">
      <div class="ai-icon">
        <span>AI</span>
      </div>
      <div class="ai-pulse"></div>
    </div>
    
    <!-- 通知组件 -->
    <Notification ref="notificationRef" message="敬请期待" type="success" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getCourseResourceDetail, getVideoResources, incrementViewCount } from '@/api/courseResource.js';
import Notification from '../components/Notification.vue';

const route = useRoute();
const router = useRouter();
const videoDetail = ref(null);
const loading = ref(false);
const error = ref('');
const videoRef = ref(null);

// 视频播放状态
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const isMuted = ref(false);

// 章节和进度相关
const chapters = ref([]);
const currentChapterId = ref('');
const courseProgress = ref(0);

// 进度条百分比
const progressPercent = computed(() => {
  if (duration.value === 0) return 0;
  return (currentTime.value / duration.value) * 100;
});

// 获取视频详情
const fetchVideoDetail = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    const uuid = route.params.id;
    if (!uuid) {
      error.value = '视频ID不存在';
      return;
    }
    
    currentChapterId.value = uuid;
    const response = await getCourseResourceDetail(uuid);
    if (response.success) {
      videoDetail.value = response.data;
      // 增加播放次数统计
      await incrementViewCount(uuid);
    } else {
      error.value = response.message || '获取视频详情失败';
    }
  } catch (err) {
    console.error('获取视频详情失败:', err);
    error.value = '网络错误，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 初始化章节数据（模拟数据）
const initializeChapters = () => {
  chapters.value = [
    {
      id: currentChapterId.value,
      title: videoDetail.value?.name || '当前章节',
      duration: '15:30',
      description: '视频简介与基础知识',
      completed: false
    },
    {
      id: 'chapter-2',
      title: '第二章：核心概念',
      duration: '12:45',
      description: '深入理解核心概念和原理',
      completed: true
    },
    {
      id: 'chapter-3',
      title: '第三章：实践应用',
      duration: '18:20',
      description: '实际案例分析和应用场景',
      completed: true
    },
    {
      id: 'chapter-4',
      title: '第四章：高级技巧',
      duration: '22:15',
      description: '高级技巧和优化方法',
      completed: false
    },
    {
      id: 'chapter-5',
      title: '第五章：项目实战',
      duration: '25:10',
      description: '完整项目开发实战演练',
      completed: false
    }
  ];
  
  // 计算课程进度
  const completedChapters = chapters.value.filter(c => c.completed).length;
  courseProgress.value = (completedChapters / chapters.value.length) * 100;
};

// 切换章节
const switchChapter = (chapter) => {
  if (chapter.id !== currentChapterId.value) {
    currentChapterId.value = chapter.id;
    console.log('切换到章节:', chapter.title);
    // 这里可以添加实际的章节切换逻辑
    if (chapter.id.startsWith('chapter-')) {
      // 模拟章节，暂时不进行实际跳转
      return;
    }
    router.push(`/resource/${chapter.id}/preview`);
  }
};

// 导航到视频区块
const navigateToVideoSection = () => {
  router.push({
    path: '/resources',
    hash: '#video-section'
  });
};

// 返回上一级页面
const goBack = () => {
  // 首先尝试返回浏览器历史
  if (window.history.length > 1) {
    router.go(-1);
  } else {
    // 如果没有历史记录，则跳转到课程资源页面
    router.push('/resources');
  }
};

// 视频事件处理
const handleTimeUpdate = () => {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime;
  }
};

const handleLoadedMetadata = () => {
  if (videoRef.value) {
    duration.value = videoRef.value.duration;
  }
};

const handlePlay = () => {
  isPlaying.value = true;
};

const handlePause = () => {
  isPlaying.value = false;
};

const togglePlay = () => {
  if (videoRef.value) {
    if (isPlaying.value) {
      videoRef.value.pause();
    } else {
      videoRef.value.play();
    }
  }
};

const handleProgressClick = (event) => {
  if (videoRef.value && duration.value > 0) {
    const rect = event.currentTarget.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const progress = clickX / rect.width;
    const newTime = progress * duration.value;
    videoRef.value.currentTime = newTime;
    currentTime.value = newTime;
  }
};

const toggleMute = () => {
  if (videoRef.value) {
    isMuted.value = !isMuted.value;
    videoRef.value.muted = isMuted.value;
  }
};

const toggleFullscreen = () => {
  if (videoRef.value) {
    if (videoRef.value.requestFullscreen) {
      videoRef.value.requestFullscreen();
    } else if (videoRef.value.webkitRequestFullscreen) {
      videoRef.value.webkitRequestFullscreen();
    } else if (videoRef.value.mozRequestFullScreen) {
      videoRef.value.mozRequestFullScreen();
    }
  }
};

// 格式化时间
const formatTime = (seconds) => {
  if (isNaN(seconds)) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '未知';
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
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

// AI助手相关
const notificationRef = ref(null);

const toggleAIChat = () => {
  if (notificationRef.value) {
    notificationRef.value.show();
  }
};

// 组件挂载时获取数据
onMounted(async () => {
  await fetchVideoDetail();
  initializeChapters();
});
</script>

<style scoped>
.video-preview-page {
  padding: 60px;
  min-height: 100vh;
  background: #f9f9f9;
}

/* 返回按钮样式 */
.back-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  margin-bottom: 15px;
  background: rgba(248, 249, 250, 0.8);
  border: 1px solid rgba(233, 236, 239, 0.6);
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  width: fit-content;
}

.back-button:hover {
  color: #5277ff;
  background: rgba(82, 119, 255, 0.05);
}

.back-button:active {
  transform: translateX(-2px);
}

.back-button .iconfont {
  font-size: 16px;
  transition: all 0.2s ease;
}

.back-button:hover .iconfont {
  transform: translateX(-2px);
}

/* 面包屑导航样式 */
.breadcrumb-nav {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
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

/* 加载和错误状态 */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #666;
  gap: 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #5277ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-spinner.small {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 主要内容区域 */
.main-content {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* 视频播放区域 */
.video-section {
  width: 100%;
  max-width: 1200px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  padding: 20px;
}

.video-player-wrapper {
  background: #000;
  position: relative;
}

.video-player {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  min-height: 500px;
  max-height: 70vh;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-element {
  width: 100%;
  height: 100%;
  background: #000;
  object-fit: contain;
  border-radius: 8px;
}

/* 视频信息 */
.video-info {
  padding: 30px;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.video-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0 0 25px 0;
  line-height: 1.4;
}

.video-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 25px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 15px;
  padding: 8px 0;
  border-bottom: 1px solid #f1f3f4;
}

.detail-item > span:first-child {
  font-weight: 600;
  color: #495057;
  width: 90px;
  flex-shrink: 0;
}

.publisher-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
}

.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.video-description {
  padding: 25px;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #5277ff;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.video-description p {
  margin: 0 0 10px 0;
  line-height: 1.6;
  color: #555;
}

.video-description p:last-child {
  margin-bottom: 0;
}


/* AI助手圆球按钮 */
.ai-assistant-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  z-index: 9999;
  overflow: hidden;
}

.ai-assistant-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
}

.ai-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 2;
}

.ai-icon span {
  color: white;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
}

.ai-pulse {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  animation: aiPulse 2s infinite;
}

@keyframes aiPulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.5;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .video-preview-page {
    padding: 20px;
  }
  
  .video-section {
    padding: 15px;
  }
  
  .back-button {
    padding: 10px 12px;
    font-size: 13px;
    margin-bottom: 12px;
  }
  
  .back-button .iconfont {
    font-size: 14px;
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
  
  .main-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .video-section {
    max-width: 100%;
  }
  
  .video-player {
    height: 50vh;
    min-height: 300px;
  }
  
  .video-title {
    font-size: 20px;
  }
  
  .video-info {
    padding: 20px;
  }
  
  .detail-item > span:first-child {
    width: 70px;
  }
  
  .ai-assistant-button {
    width: 50px;
    height: 50px;
    bottom: 20px;
    right: 20px;
  }
  
  .ai-icon span {
    font-size: 12px;
  }
}
</style>