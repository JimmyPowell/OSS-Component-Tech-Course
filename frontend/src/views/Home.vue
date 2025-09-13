<template>
  <div class="index-page">
    <div class="swiper-container banner-index">
      <div class="swiper-wrapper">
        <div class="swiper-slide">
          <div class="container">
            <div class="slide-grid ">
              <div class="banner-desc">实战出真知</div>
              <div class="banner-title webfont">
                《开源软件构建技术：理论与实践》<br>
                ——课程助你玩转开源
              </div>
              <div class="banner-foot">
                <a href="" class="btn btn-primary btn-more">
                  <span>了解更多</span>
                  <span class="iconfont icon-a-right"></span>
                </a>
              </div>
            </div>
          </div>
        </div>
        <div class="swiper-slide">
          <div class="container">
            <div class="slide-grid ">
              <div class="banner-desc">实战出真知</div>
              <div class="banner-title webfont">
                《开源软件构建技术：理论与实践》<br>
                ——课程助你玩转开源
              </div>
              <div class="banner-foot">
                <a href="" class="btn btn-more btn-primary">
                  <span>了解更多</span>
                  <span class="iconfont icon-a-right"></span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="swiper-pagination banner-pagination"></div>
    </div>
    <div class="page-section show-section">
      <div class="container">
        <div class="page-title">作品展示</div>
        <div class="show-panel">
          <div class="show-left-show">
            <div class="showcase-image-container">
              <div class="showcase-image-wrapper" :class="{ 'slide-in': isSliding }">
                <img 
                  v-if="currentShowcase" 
                  :src="currentShowcase.avatar_url || '/images/wk-pic.png'" 
                  :alt="currentShowcase.name"
                  class="showcase-image"
                  @error="handleImageError"
                />
                <img 
                  v-else 
                  src="/images/wk-pic.png" 
                  alt="默认展示图"
                  class="showcase-image"
                />
              </div>
            </div>
            <div class="show-prev" @click="previousShowcase">
              <span class="iconfont icon-l-left"></span>
            </div>
            <div class="show-next" @click="nextShowcase">
              <span class="iconfont icon-l-right"></span>
            </div>
          </div>
          <div class="show-cell">
            <div class="showcase-text-content" :class="{ 'fade-in': isFading }">
              <!-- 加载状态 -->
              <div v-if="isLoadingShowcases" class="show-title">正在加载作品...</div>
              <!-- 错误状态 -->
              <div v-else-if="showcaseError" class="show-title">{{ showcaseError }}</div>
              <!-- 无作品状态 -->
              <div v-else-if="!currentShowcase" class="show-title">暂无优秀作品展示</div>
              <!-- 正常显示作品 -->
              <template v-else>
                <div class="show-title">{{ currentShowcase.name }}</div>
                <div class="show-item" v-if="currentShowcase.summary">{{ currentShowcase.summary }}</div>
                <div class="show-item" v-if="currentShowcase.detailed_introduction">{{ currentShowcase.detailed_introduction }}</div>
              </template>
            </div>
          </div>
        </div>
        <div class="section-foot">
          <router-link to="/showcase" class="btn btn-more ">
            <span>进入作品展示中心</span>
            <span class="iconfont icon-a-right"></span>
          </router-link>
        </div>
      </div>
    </div>
    <CourseIntroCarousel />
    <div class="page-section">
      <div class="container">
        <!-- 面包屑导航 -->
        <nav class="breadcrumb-nav">
          <span class="breadcrumb-current">首页</span>
          <span class="breadcrumb-separator">></span>
          <span class="breadcrumb-current">公告</span>
        </nav>
        
        <div class="section-head">
          <div class="page-title">最新公告</div>
          <router-link to="/announcements" class="btn-more"><span>更多</span><span class="iconfont icon-a-right"></span></router-link>
        </div>
        <div class="notice-panel">
          <div class="notice-focus" v-if="featuredAnnouncement">
            <div class="notice-photo mb-20">
              <router-link :to="`/announcements/${featuredAnnouncement.uuid}`" class="scale">
                <img :src="featuredAnnouncement.cover_url || '/images/gonggao.png'" 
                     :alt="featuredAnnouncement.name"
                     @error="handleAnnouncementImageError">
              </router-link>
            </div>
            <div class="notice-title mb-10">
              <router-link :to="`/announcements/${featuredAnnouncement.uuid}`">
                {{ featuredAnnouncement.name }}
              </router-link>
            </div>
            <div class="notice-desc mb-10">{{ featuredAnnouncement.summary || '暂无摘要' }}</div>
            <div class="notice-time">{{ formatDate(featuredAnnouncement.created_at) }}</div>
          </div>
          <div class="flex-col">
            <ul class="notice-list">
              <router-link 
                v-for="announcement in announcements.slice(1, 3)" 
                :key="announcement.uuid"
                :to="`/announcements/${announcement.uuid}`"
                class="notice-item-link"
              >
                <li class="notice-item">
                  <div class="notice-content">
                    <div class="notice-title mb-10">
                      {{ announcement.name }}
                    </div>
                    <div class="notice-desc">
                      {{ announcement.summary || '暂无摘要' }}
                    </div>
                    <div class="notice-time-right">{{ formatDate(announcement.created_at) }}</div>
                  </div>
                </li>
              </router-link>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue';
import Swiper from 'swiper/bundle';
import apiClient from '../api';
import { showcaseAPI } from '../api/showcase';
import CourseIntroCarousel from '@/components/CourseIntroCarousel.vue';

// 作品展示相关状态
const showcases = ref([]);
const currentIndex = ref(0);
const isSliding = ref(false);
const isFading = ref(false);
const isLoadingShowcases = ref(true);
const showcaseError = ref(null);

// 公告相关状态
const announcements = ref([]);
const featuredAnnouncement = computed(() => announcements.value.length > 0 ? announcements.value[0] : null);

// Home 其他区域状态（课程简介已抽离为独立组件）


// 当前展示的作品
const currentShowcase = computed(() => {
  console.log('计算当前展示作品 - 作品数组长度:', showcases.value.length);
  console.log('当前索引:', currentIndex.value);
  const result = showcases.value.length > 0 ? showcases.value[currentIndex.value] : null;
  console.log('当前展示的作品:', result);
  return result;
});

// 获取作品数据
const fetchShowcases = async () => {
  try {
    isLoadingShowcases.value = true;
    showcaseError.value = null;
    console.log('开始获取前端展示作品数据...');
    
    // 使用专用的前端展示API端点，只获取优秀作品
    const response = await showcaseAPI.getFrontendShowcases({
      limit: 10
    });
    
    console.log('API响应:', response);
    console.log('响应数据:', response.data);
    
    if (response.data && response.data.code === 200) {
      console.log('API调用成功，数据结构:', response.data.data);
      if (response.data.data && response.data.data.items) {
        showcases.value = response.data.data.items;
        console.log('成功设置作品数组，长度:', showcases.value.length);
        console.log('作品详情:', showcases.value);
      } else {
        console.log('数据中没有items字段，完整数据:', response.data.data);
        showcases.value = [];
      }
    } else {
      console.log('API调用返回失败状态:', response.data);
      showcaseError.value = '获取作品数据失败';
      showcases.value = [];
    }
  } catch (error) {
    console.error('获取前端展示作品数据失败，错误详情:', error);
    console.error('错误响应:', error.response?.data);
    console.error('错误状态码:', error.response?.status);
    showcaseError.value = '网络错误，请稍后重试';
    showcases.value = [];
  } finally {
    isLoadingShowcases.value = false;
  }
};

// 切换到下一个作品
const nextShowcase = () => {
  if (showcases.value.length <= 1) return;
  
  animateTransition(() => {
    currentIndex.value = (currentIndex.value + 1) % showcases.value.length;
  });
};

// 切换到上一个作品
const previousShowcase = () => {
  if (showcases.value.length <= 1) return;
  
  animateTransition(() => {
    currentIndex.value = currentIndex.value === 0 ? showcases.value.length - 1 : currentIndex.value - 1;
  });
};

// 动画过渡
const animateTransition = (callback) => {
  // 开始动画
  isSliding.value = true;
  isFading.value = true;
  
  // 延迟执行回调
  setTimeout(() => {
    callback();
    
    // 动画结束
    setTimeout(() => {
      isSliding.value = false;
      isFading.value = false;
    }, 50);
  }, 300);
};

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.src = '/images/wk-pic.png';
};

// 获取公告数据
const fetchAnnouncements = async () => {
  try {
    console.log('开始获取公告数据...');
    const response = await apiClient.get('/announcements', {
      params: {
        limit: 3 // 获取3条公告，一条作为主要展示，两条作为列表
      }
    });
    
    console.log('公告API响应:', response.data);
    
    if (response.data && response.data.code === 200) {
      if (response.data.data && response.data.data.items) {
        announcements.value = response.data.data.items;
        console.log('成功获取公告数据，数量:', announcements.value.length);
      } else {
        console.log('公告数据中没有items字段');
        announcements.value = [];
      }
    } else {
      console.log('获取公告失败:', response.data);
      announcements.value = [];
    }
  } catch (error) {
    console.error('获取公告数据失败:', error);
    announcements.value = [];
  }
};

// 处理公告图片加载错误
const handleAnnouncementImageError = (event) => {
  event.target.src = '/images/gonggao.png';
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
};


onMounted(() => {
  // 获取作品数据
  fetchShowcases();
  
  // 获取公告数据
  fetchAnnouncements();
  
  // 初始化横幅轮播
  new Swiper('.banner-index', {
    pagination: {
      el: '.swiper-pagination',
      clickable: true,
    },
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    loop: true,
    loopAdditionalSlides: 1,
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },
  });
  
});

onUnmounted(() => {
  // 页面卸载清理逻辑（课程简介轮播由子组件负责清理）
});
</script>

<style scoped>
.banner-index .banner-pagination {
  left: 50%;
  transform: translateX(-50%);
  width: auto;
}

/* 课程卡片容器样式 */
/* Course section responsive scaling */
.course-section {
  /* Unified scaling variables for this section */
  --pad-y: clamp(24px, 5vw, 80px);
  --pad-x: clamp(16px, 3.5vw, 40px);
  --gap: clamp(16px, 3vw, 40px);
  --title-fs: clamp(18px, 2.4vw, 36px);
  --desc-fs: clamp(13px, 1.6vw, 16px);
  --btn-h: clamp(38px, 4.2vw, 50px);
  --btn-w: clamp(120px, 12vw, 160px);
  --photo-w: clamp(120px, 16vw, 226px);
  --photo-h: clamp(130px, 17vw, 244px);
  --mask-h: calc(var(--photo-h) * 0.47);
}

.course-card-container {
  padding: 60px 0;
  position: relative;
}

.course-swiper {
  overflow: visible;
  padding: 40px 0;
}

.course-swiper .swiper-slide {
  /* Let Swiper compute slide width from slidesPerView */
  width: auto;
  height: auto;
  padding-top: clamp(16px, 3vw, 40px);
  padding-bottom: clamp(16px, 3vw, 40px);
  transition: all 0.4s ease;
  display: flex;
  align-items: stretch;
  justify-content: center;
}

.course-swiper .swiper-slide .kc-card {
  width: 100%;
  height: 100%;
  transition: all 0.4s ease;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  gap: var(--gap);
  padding: var(--pad-y) var(--pad-x) calc(var(--pad-x) * 1.5) var(--pad-x);
}

/* 中心卡片效果 */
.course-swiper .swiper-slide-active .kc-card {
  transform: scale(1.0);
  opacity: 1;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

/* 非中心卡片效果 */
.course-swiper .swiper-slide:not(.swiper-slide-active) .kc-card {
  transform: scale(0.75);
  opacity: 0.6;
}

/* Tab基础样式 */
.kc-tabs {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30px;
}

/* Tab点击动画效果 */
.kc-tabs li {
  cursor: pointer;
  transition: all 0.3s ease;
}

.kc-tabs li a {
  transition: all 0.3s ease;
  user-select: none;
}

.kc-tabs li:hover a {
  opacity: 0.8;
  transform: translateY(-2px);
}

.kc-tabs li.active a {
  opacity: 1;
}

/* 课程轮播分页器样式 */
.course-pagination {
  position: relative;
  margin-top: 30px;
  text-align: center;
}

.course-pagination .swiper-pagination-bullet {
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.4);
  opacity: 0.6;
  margin: 0 6px;
  transition: all 0.3s ease;
}

.course-pagination .swiper-pagination-bullet-active {
  background: #ffffff;
  opacity: 1;
  transform: scale(1.2);
}

/* Card internals responsive sizing */
.course-section .kc-title {
  font-size: var(--title-fs) !important;
}

.course-section .kc-desc {
  font-size: var(--desc-fs) !important;
}

.course-section .kc-photo {
  width: var(--photo-w) !important;
  height: var(--photo-h) !important;
}

.course-section .kc-photo::after {
  height: var(--mask-h) !important;
}

.course-section .photo-box {
  /* Keep the book image floating proportionally */
  margin-top: calc(var(--photo-h) * -0.49);
}

.course-section .kc-card .btn-more {
  width: var(--btn-w);
  height: var(--btn-h);
  font-size: clamp(12px, 1.6vw, 16px);
}

/* 响应式优化 */
/* 大屏幕优化 */
@media (min-width: 1200px) {
  .course-card-container { padding: 80px 0; }
}

/* 中等屏幕优化 */
@media (max-width: 1199px) and (min-width: 900px) {
  .course-card-container {
    padding: 60px 0;
  }
  
  .course-swiper .swiper-slide:not(.swiper-slide-active) .kc-card {
    transform: scale(0.8);
    opacity: 0.7;
  }
}

/* 平板屏幕优化 */
@media (max-width: 899px) and (min-width: 768px) {
  .course-card-container {
    padding: 50px 0;
  }
  
  .course-swiper .swiper-slide:not(.swiper-slide-active) .kc-card {
    transform: scale(0.85);
    opacity: 0.75;
  }
  
  .kc-tabs {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .kc-tabs li {
    margin: 5px;
  }
}

/* 小平板和大手机屏幕优化 */
@media (max-width: 767px) and (min-width: 480px) {
  .course-card-container {
    padding: 40px 0;
    min-height: 320px;
  }
  
  .course-swiper {
    padding: 20px 0;
  }
  
  .course-swiper .swiper-slide { padding: 20px 0; }
  
  .course-swiper .swiper-slide:not(.swiper-slide-active) .kc-card {
    transform: scale(0.9);
    opacity: 0.8;
  }
  
  .kc-tabs {
    flex-wrap: wrap;
    justify-content: center;
    padding: 0 10px;
  }
  
  .kc-tabs li {
    margin: 3px;
    font-size: 14px;
  }
}

/* 手机屏幕优化 */
@media (max-width: 479px) {
  .course-card-container {
    padding: 30px 0;
    min-height: 280px;
  }
  
  .course-swiper {
    padding: 15px 0;
  }
  
  .course-swiper .swiper-slide { padding: 15px 0; }
  
  .course-swiper .swiper-slide .kc-card {
    border-radius: 15px;
  }
  
  .course-swiper .swiper-slide-active .kc-card {
    transform: scale(1.0);
  }
  
  .course-swiper .swiper-slide:not(.swiper-slide-active) .kc-card {
    transform: scale(0.95);
    opacity: 0.85;
  }
  
  .kc-tabs {
    flex-wrap: wrap;
    justify-content: center;
    padding: 0 5px;
  }
  
  .kc-tabs li {
    margin: 2px;
    font-size: 12px;
  }
  
  .kc-tabs li a {
    padding: 8px 12px;
  }
  
  .page-title {
    font-size: 24px;
    margin-bottom: 20px;
  }
}

/* 3D轮播增强效果 */
.course-swiper .swiper-slide-shadow-left,
.course-swiper .swiper-slide-shadow-right {
  background-image: none;
}

.course-swiper .swiper-slide {
  transform-style: preserve-3d;
}

/* 卡片切换动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 作品展示动画效果 */
.showcase-image-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.showcase-image-wrapper {
  transition: transform 0.4s ease-in-out;
  width: 100%;
  height: 100%;
}

.showcase-image-wrapper.slide-in {
  transform: translateX(100%);
}

.showcase-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.showcase-text-content {
  transition: opacity 0.3s ease-in-out;
}

.showcase-text-content.fade-in {
  opacity: 0;
}

/* 按钮悬停效果优化 */
.show-prev,
.show-next {
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0.8;
}

.show-prev:hover,
.show-next:hover {
  opacity: 1;
  transform: scale(1.1);
}

/* 响应式优化 */
@media (max-width: 768px) {
  .showcase-image-wrapper.slide-in {
    transform: translateX(50%);
  }
  
  .showcase-text-content {
    padding: 10px 0;
  }
}

/* 公告区域样式调整 */
.notice-photo {
  margin-bottom: 15px !important;
}

.notice-photo img {
  height: 190px !important;
  width: 400px !important;
  max-width: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.notice-focus {
  display: flex;
  flex-direction: column;
  height: fit-content;
  max-width: 400px;
}

.notice-list {
  padding-top: 0 !important;
}

.notice-item-link {
  display: block;
  text-decoration: none !important;
  color: inherit;
  transition: all 0.3s ease;
  border-radius: 8px;
  margin-bottom: 2px;
}

.notice-item-link:hover {
  background-color: #f8f9fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-decoration: none !important;
  color: inherit;
}

.notice-item {
  padding: 20px 15px;
  border-bottom: 1px solid #f0f0f0;
  margin: 0;
  list-style: none;
  height: 100px;
  display: flex;
  align-items: stretch;
  position: relative;
}

.notice-item-link:last-child .notice-item {
  border-bottom: none;
}

.notice-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  padding-bottom: 25px;
}

.notice-item .notice-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px !important;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.notice-item .notice-desc {
  font-size: 14px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  line-height: 1.5;
}

.notice-time-right {
  position: absolute;
  bottom: 0;
  right: 0;
  font-size: 12px;
  color: #a8a9b1;
}

/* 调整公告区与底部的间距 */
.page-section {
  margin-bottom: 80px;
}

.page-section:last-child {
  margin-bottom: 120px;
}

/* 面包屑导航样式 */
.breadcrumb-nav {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
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
</style>
