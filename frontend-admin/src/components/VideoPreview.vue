<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { LoadingOutlined, UserOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import request from '../utils/request';

const route = useRoute();
const loading = ref(true);
const videoDetail = ref(null);
const videoRef = ref(null);

// 视频播放状态
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(1);
const isMuted = ref(false);

// 课程章节列表
const chapters = ref([]);
const currentChapter = ref(null);
const loadingChapters = ref(false);

const API_BASE_URL = 'http://localhost:8000/api/v1/course-resources';

// 获取视频详情
const fetchVideoDetail = async () => {
  const uuid = route.params.uuid;
  if (!uuid) {
    message.error('视频ID无效');
    return;
  }

  try {
    loading.value = true;
    const response = await request.get(`${API_BASE_URL}/${uuid}/detail`);
    
    if (response.data.code === 200) {
      videoDetail.value = response.data.data;
      
      // 增加播放次数统计
      incrementViewCount(uuid);
      
      // 等待视频元素加载
      setTimeout(() => {
        if (videoRef.value) {
          videoRef.value.load();
        }
      }, 100);
    } else {
      message.error(response.data.message || '获取视频详情失败');
    }
  } catch (error) {
    console.error('获取视频详情失败:', error);
    message.error('获取视频详情失败');
  } finally {
    loading.value = false;
  }
};

// 增加播放次数
const incrementViewCount = async (uuid) => {
  try {
    await request.post(`${API_BASE_URL}/${uuid}/increment-view`);
    console.log('播放次数统计成功');
  } catch (error) {
    console.error('播放次数统计失败:', error);
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
  if (!bytes) return '-';
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'numeric', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
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

const handleVolumeChange = (value) => {
  volume.value = value / 100;
  if (videoRef.value) {
    videoRef.value.volume = volume.value;
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

// 进度条百分比
const progressPercent = computed(() => {
  if (duration.value === 0) return 0;
  return (currentTime.value / duration.value) * 100;
});

// 获取课程章节列表
const fetchChapters = async () => {
  try {
    loadingChapters.value = true;
    const response = await request.get(`${API_BASE_URL}?resource_type=video&limit=50`);
    
    if (response.data.code === 200) {
      chapters.value = response.data.data.items.map(item => ({
        id: item.uuid,
        title: item.name,
        duration: '0:00-0:45', // 这里先写死，后续从后端获取
        description: item.description || '体验结构的定义'
      }));
      
      // 设置当前章节
      if (route.params.uuid) {
        currentChapter.value = chapters.value.find(c => c.id === route.params.uuid);
      }
    }
  } catch (error) {
    console.error('获取章节列表失败:', error);
  } finally {
    loadingChapters.value = false;
  }
};

// 切换章节
const switchChapter = (chapter) => {
  if (chapter.id !== route.params.uuid) {
    // 这里可以跳转到新的视频
    console.log('切换到章节:', chapter.title);
    // 更新当前章节
    currentChapter.value = chapter;
  }
};

// AI助手相关
const aiChatVisible = ref(false);

const toggleAIChat = () => {
  aiChatVisible.value = !aiChatVisible.value;
  console.log('切换AI对话:', aiChatVisible.value ? '开启' : '关闭');
  // 这里后续可以添加AI对话界面的显示/隐藏逻辑
};

onMounted(() => {
  fetchVideoDetail();
  fetchChapters();
});
</script>

<template>
  <div class="video-preview-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large">
        <template #indicator>
          <LoadingOutlined style="font-size: 24px" spin />
        </template>
      </a-spin>
      <p>加载中...</p>
    </div>

    <!-- 主要内容区域 -->
    <div v-else-if="videoDetail" class="main-content">
      <!-- 左侧视频播放区域 -->
      <div class="video-section">
        <!-- 视频播放器区域 -->
        <div class="video-player-wrapper">
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
            >
              视频将在预览时播放
            </video>

            <!-- 视频控制条 -->
            <div class="video-controls">
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
                  <!-- 播放/暂停按钮 -->
                  <a-button 
                    type="text" 
                    size="small"
                    @click="togglePlay"
                    class="control-btn"
                  >
                    <template #icon>
                      <i v-if="isPlaying" class="control-icon">⏸</i>
                      <i v-else class="control-icon">▶</i>
                    </template>
                  </a-button>

                  <!-- 时间显示 -->
                  <span class="time-display">
                    {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
                  </span>
                </div>

                <div class="right-controls">
                  <!-- 音量控制 -->
                  <a-button 
                    type="text" 
                    size="small"
                    @click="toggleMute"
                    class="control-btn"
                  >
                    <template #icon>
                      <i v-if="isMuted" class="control-icon">🔇</i>
                      <i v-else class="control-icon">🔊</i>
                    </template>
                  </a-button>

                  <!-- 音量滑块 -->
                  <div class="volume-slider">
                    <a-slider
                      :value="volume * 100"
                      @change="handleVolumeChange"
                      :tip-formatter="null"
                      style="width: 60px;"
                    />
                  </div>

                  <!-- 全屏按钮 -->
                  <a-button 
                    type="text" 
                    size="small"
                    @click="toggleFullscreen"
                    class="control-btn"
                  >
                    <template #icon>
                      <i class="control-icon">⛶</i>
                    </template>
                  </a-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 视频信息 -->
        <div class="video-info">
          <div class="video-meta">
            <h2 class="chapter-title">{{ videoDetail.name }}</h2>
            <div class="video-details">
              <div class="detail-item">
                <UserOutlined />
                <span>{{ videoDetail.publisher_name || '发布者' }}</span>
              </div>
            </div>
          </div>

          <!-- 视频描述 -->
          <div v-if="videoDetail.description" class="video-description">
            <p>{{ videoDetail.description }}</p>
          </div>
        </div>
      </div>

      <!-- 右侧章节列表 -->
      <div class="chapters-section">
        <div class="chapters-header">
          <h3>课程章节</h3>
        </div>
        
        <div class="chapters-list">
          <div v-if="loadingChapters" class="chapters-loading">
            <a-spin size="small" />
            <span>加载中...</span>
          </div>
          
          <div v-else>
            <div 
              v-for="(chapter, index) in chapters" 
              :key="chapter.id"
              :class="['chapter-item', { 'active': currentChapter?.id === chapter.id }]"
              @click="switchChapter(chapter)"
            >
              <div class="chapter-content">
                <div class="chapter-header">
                  <span class="chapter-duration">{{ chapter.duration }}</span>
                </div>
                <div class="chapter-description">
                  {{ chapter.description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <a-empty description="视频未找到或加载失败" />
    </div>

    <!-- AI助手圆球按钮 -->
    <div class="ai-assistant-button" @click="toggleAIChat">
      <div class="ai-icon">
        <span>AI</span>
      </div>
      <div class="ai-pulse"></div>
    </div>
  </div>
</template>

<style scoped>
.video-preview-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 0;
  margin: 0;
  position: relative;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.main-content {
  display: flex;
  gap: 20px;
  width: 100%;
  margin: 0;
  padding: 20px;
  align-items: flex-start;
  min-height: 100vh;
  box-sizing: border-box;
}

.video-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 0; /* 确保flex子项可以缩小 */
}

.video-player-wrapper {
  background: #000;
  position: relative;
}

.video-player {
  position: relative;
  width: 100%;
  height: 70vh; /* 使用视口高度，让视频更大 */
  min-height: 500px;
}

.video-element {
  width: 100%;
  height: 100%;
  cursor: pointer;
  background: #555;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  object-fit: contain; /* 保持宽高比 */
}

.video-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  padding: 10px;
  color: white;
}

.progress-bar {
  margin-bottom: 8px;
  cursor: pointer;
}

.progress-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: #1890ff;
  border-radius: 2px;
  transition: width 0.1s;
}

.control-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left-controls,
.right-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-btn {
  color: white !important;
  border: none !important;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.control-icon {
  font-size: 14px;
  font-style: normal;
}

.time-display {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.volume-slider {
  display: flex;
  align-items: center;
}

.volume-slider :deep(.ant-slider) {
  margin: 0;
}

.volume-slider :deep(.ant-slider-rail) {
  background: rgba(255, 255, 255, 0.3);
}

.volume-slider :deep(.ant-slider-track) {
  background: #1890ff;
}

.volume-slider :deep(.ant-slider-handle) {
  border-color: #1890ff;
}

.video-info {
  padding: 24px;
}

.video-meta {
  margin-bottom: 16px;
}

.chapter-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #262626;
}

.video-details {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #595959;
  font-size: 14px;
}

.video-description {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.video-description p {
  margin: 0;
  line-height: 1.6;
  color: #595959;
}

/* 右侧章节列表样式 */
.chapters-section {
  width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: fit-content;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chapters-header {
  padding: 20px 20px 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.chapters-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.chapters-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.chapters-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #8c8c8c;
}

.chapter-item {
  padding: 16px 20px;
  cursor: pointer;
  border-bottom: 1px solid #f5f5f5;
  transition: background-color 0.2s ease;
}

.chapter-item:hover {
  background-color: #f8f9fa;
}

.chapter-item.active {
  background-color: #e6f7ff;
  border-left: 3px solid #1890ff;
}

.chapter-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-duration {
  font-size: 12px;
  color: #1890ff;
  font-weight: 500;
  background: #f0f8ff;
  padding: 2px 8px;
  border-radius: 12px;
}

.chapter-description {
  font-size: 14px;
  color: #595959;
  line-height: 1.4;
}

.chapter-item.active .chapter-description {
  color: #262626;
  font-weight: 500;
}

/* 滚动条样式 */
.chapters-list::-webkit-scrollbar {
  width: 6px;
}

.chapters-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chapters-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chapters-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* AI助手圆球按钮 */
.ai-assistant-button {
  position: fixed !important;
  bottom: 80px !important;
  right: 30px !important;
  left: auto !important;
  top: auto !important;
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
  z-index: 9999 !important;
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
@media (max-width: 1200px) {
  .chapters-section {
    width: 350px;
  }
}

@media (max-width: 768px) {
  .video-preview-container {
    padding: 10px;
  }
  
  .main-content {
    flex-direction: column;
    gap: 16px;
    padding: 10px;
  }
  
  .chapters-section {
    width: 100%;
    max-height: 400px;
  }
  
  .chapter-title {
    font-size: 18px;
  }
  
  .video-info {
    padding: 16px;
  }
  
  .right-controls .volume-slider {
    display: none;
  }
  
  .video-player {
    height: 50vh;
    min-height: 300px;
  }
  
  .ai-assistant-button {
    width: 50px !important;
    height: 50px !important;
    bottom: 60px !important;
    right: 20px !important;
    left: auto !important;
  }
  
  .ai-icon span {
    font-size: 12px;
  }
}
</style>