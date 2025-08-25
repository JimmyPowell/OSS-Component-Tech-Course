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
              <div class="show-title">{{ currentShowcase?.name || '暂无作品展示' }}</div>
              <div class="show-item" v-if="currentShowcase?.summary">{{ currentShowcase.summary }}</div>
              <div class="show-item" v-if="currentShowcase?.detailed_introduction">{{ currentShowcase.detailed_introduction }}</div>
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
    <div class="page-section course-section">
      <div class="container">
        <div class="page-title text-center">课程简介</div>
        <ul class="nav kc-tabs" role="tablist" >
          <li role="presentation" class="active"><a href="#tab1" aria-controls="tab1" role="tab" data-toggle="tab">开源基础与入门</a></li>
          <li role="presentation"><a href="#tab2" aria-controls="tab2" role="tab" data-toggle="tab">开发工具与协作</a></li>
          <li role="presentation"><a href="#tab3" aria-controls="tab3" role="tab" data-toggle="tab">构建与测试</a></li>
          <li role="presentation"><a href="#tab4" aria-controls="tab4" role="tab" data-toggle="tab">开源开发实践</a></li>
          <li role="presentation"><a href="#tab5" aria-controls="tab5" role="tab" data-toggle="tab">开源开发实践</a></li>
          <li role="presentation"><a href="#tab6" aria-controls="tab6" role="tab" data-toggle="tab">开源开发实践</a></li>
          <li role="presentation"><a href="#tab7" aria-controls="tab7" role="tab" data-toggle="tab">开源贡献评价体系</a></li>
        </ul>
      </div>
      <div class="tab-content">
        <div role="tabpanel" class="tab-pane active" id="cad-tab1">
          <ul class="nav cad-tabs" role="tablist" >
            <li role="presentation" class="active"><a href="#cad-tab1" aria-controls="cad-tab1" role="tab" data-toggle="tab">基础入门</a></li>
            <li role="presentation"><a href="#cad-tab2" aria-controls="cad-tab2" role="tab" data-toggle="tab">版本控制</a></li>
            <li role="presentation"><a href="#cad-tab3" aria-controls="cad-tab3" role="tab" data-toggle="tab">项目实战</a></li>
            <li role="presentation"><a href="#cad-tab4" aria-controls="cad-tab4" role="tab" data-toggle="tab">团队协作</a></li>
          </ul>
          <div class="swiper-container kc-swiper">
            <div class="swiper-wrapper">
              <div class="swiper-slide">
                <div class="kc-card kc-card-a">
                  <div class="kc-photo">
                    <div class="photo-box">
                      <img src="/images/book.png" alt="">
                    </div>
                  </div>
                  <div class="flex-col">
                    <div class="kc-title"><a href="">开源软件构建技术 </a></div>
                    <div class="kc-desc">学习分析仪表盘是教育技术领域的一个重要工具，它通过数据可视化的方式，帮助教师和学生理解学习过程中的各种数据指标。对于您的《开源软件构建技术》课程网站。</div>
                    <a href="" class="btn btn-more">
                      <span>进入课程</span>
                      <span class="iconfont icon-a-right"></span>
                    </a>
                  </div>
                </div>
              </div>
              <div class="swiper-slide">
                <div class="kc-card kc-card-b">
                  <div class="kc-photo">
                    <div class="photo-box">
                      <img src="/images/book.png" alt="">
                    </div>
                  </div>
                  <div class="flex-col">
                    <div class="kc-title"><a href="">开源软件构建技术 </a></div>
                    <div class="kc-desc">学习分析仪表盘是教育技术领域的一个重要工具，它通过数据可视化的方式，帮助教师和学生理解学习过程中的各种数据指标。对于您的《开源软件构建技术》课程网站。</div>
                    <a href="" class="btn btn-more">
                      <span>进入课程</span>
                      <span class="iconfont icon-a-right"></span>
                    </a>
                  </div>
                </div>
              </div>
              <div class="swiper-slide">
                <div class="kc-card kc-card-c">
                  <div class="kc-photo">
                    <div class="photo-box">
                      <img src="/images/book.png" alt="">
                    </div>
                  </div>
                  <div class="flex-col">
                    <div class="kc-title"><a href="">开源软件构建技术 </a></div>
                    <div class="kc-desc">学习分析仪表盘是教育技术领域的一个重要工具，它通过数据可视化的方式，帮助教师和学生理解学习过程中的各种数据指标。对于您的《开源软件构建技术》课程网站。</div>
                    <a href="" class="btn btn-more">
                      <span>进入课程</span>
                      <span class="iconfont icon-a-right"></span>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div role="tabpanel" class="tab-pane" id="tab2">
          <p></p>
        </div>
        <div role="tabpanel" class="tab-pane" id="tab3">
          <p></p>
        </div>
        <div role="tabpanel" class="tab-pane" id="tab4">
          <p></p>
        </div>
        <div role="tabpanel" class="tab-pane" id="tab5">
          <p></p>
        </div>
        <div role="tabpanel" class="tab-pane" id="tab6">
          <p></p>
        </div>
        <div role="tabpanel" class="tab-pane" id="tab7">
          <p></p>
        </div>
      </div>
    </div>
    <div class="page-section">
      <div class="container">
        <div class="section-head">
          <div class="page-title">最新公告</div>
          <router-link to="/announcements" class="btn-more"><span>更多</span><span class="iconfont icon-a-right"></span></router-link>
        </div>
        <div class="notice-panel">
          <div class="notice-focus" v-if="featuredAnnouncement">
            <div class="notice-time mb-20">{{ formatDate(featuredAnnouncement.created_at) }}</div>
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
            <div class="notice-desc">{{ featuredAnnouncement.summary || '暂无摘要' }}</div>
          </div>
          <div class="flex-col">
            <ul class="notice-list">
              <li class="notice-item" v-for="announcement in announcements.slice(1, 4)" :key="announcement.uuid">
                <div class="notice-time">{{ formatDate(announcement.created_at) }}</div>
                <div class="flex-col">
                  <div class="notice-title mb-10">
                    <router-link :to="`/announcements/${announcement.uuid}`">
                      {{ announcement.name }}
                    </router-link>
                  </div>
                  <div class="notice-desc">
                    {{ announcement.summary || '暂无摘要' }}
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import Swiper from 'swiper/bundle';
import apiClient from '../api';

// 作品展示相关状态
const showcases = ref([]);
const currentIndex = ref(0);
const isSliding = ref(false);
const isFading = ref(false);

// 公告相关状态
const announcements = ref([]);
const featuredAnnouncement = computed(() => announcements.value.length > 0 ? announcements.value[0] : null);


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
    console.log('开始获取作品数据...');
    // 先尝试不带status参数的请求
    const response = await apiClient.get('/showcases', {
      params: {
        limit: 10
      }
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
      showcases.value = [];
    }
  } catch (error) {
    console.error('获取作品数据失败，错误详情:', error);
    console.error('错误响应:', error.response?.data);
    console.error('错误状态码:', error.response?.status);
    // 如果获取失败，可以使用默认数据
    showcases.value = [];
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
        limit: 4 // 获取4条公告，一条作为主要展示，三条作为列表
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
  new Swiper('.kc-swiper', {
    slidesPerView: 'auto',
    spaceBetween: 80,
    centeredSlides: true,
    pagination: {
      el: '.kc-swiper .swiper-pagination',
      clickable: true,
    },
  });
});
</script>

<style scoped>
.banner-index .banner-pagination {
  left: 50%;
  transform: translateX(-50%);
  width: auto;
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
</style>
