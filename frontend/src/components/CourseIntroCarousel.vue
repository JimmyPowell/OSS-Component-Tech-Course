<template>
  <div class="page-section course-intro">
    <div class="container">
      <div class="page-title text-center">课程简介</div>
      <ul class="nav ci-tabs" role="tablist">
        <li role="presentation" :class="{ active: activeTabIndex === 0 }" @click="switchTab(0)">
          <a>开源基础与入门</a>
        </li>
        <li role="presentation" :class="{ active: activeTabIndex === 1 }" @click="switchTab(1)">
          <a>开发工具与协作</a>
        </li>
        <li role="presentation" :class="{ active: activeTabIndex === 2 }" @click="switchTab(2)">
          <a>构建与测试</a>
        </li>
        <li role="presentation" :class="{ active: activeTabIndex === 3 }" @click="switchTab(3)">
          <a>开源开发实践</a>
        </li>
        <li role="presentation" :class="{ active: activeTabIndex === 4 }" @click="switchTab(4)">
          <a>开源开发实战</a>
        </li>
        <li role="presentation" :class="{ active: activeTabIndex === 5 }" @click="switchTab(5)">
          <a>开源项目管理</a>
        </li>
        <li role="presentation" :class="{ active: activeTabIndex === 6 }" @click="switchTab(6)">
          <a>开源贡献评价体系</a>
        </li>
      </ul>
    </div>

    <div class="ci-card-container">
      <div class="swiper-container course-swiper">
        <div class="swiper-wrapper">
          <div v-for="(course, index) in courseData" :key="index" class="swiper-slide">
            <div class="ci-card" :class="course.cardClass">
              <div class="ci-photo">
                <div class="ci-photo-box">
                  <img :src="course.image" :alt="course.title">
                </div>
              </div>
              <div class="flex-col">
                <div class="ci-title">
                  <a :href="course.link">{{ course.title }}</a>
                </div>
                <div class="ci-desc">{{ course.description }}</div>
                <a :href="course.link" class="btn btn-more">
                  <span>进入课程</span>
                  <span class="iconfont icon-a-right"></span>
                </a>
              </div>
            </div>
          </div>
        </div>
        <div class="swiper-pagination course-pagination"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Swiper from 'swiper/bundle';

const activeTabIndex = ref(0);
const courseSwiper = ref(null);

// 课程数据
const courseData = [
  {
    title: '开源基础与入门',
    description:
      '学习开源软件的基本概念、发展历史和核心理念，了解开源社区的运作模式，掌握开源许可证的基本知识，为后续学习奠定坚实基础。',
    image: '/images/book.png',
    link: '/resources',
    cardClass: 'ci-card-a',
  },
  {
    title: '开发工具与协作',
    description:
      '掌握Git版本控制系统的使用，学习GitHub/GitLab等代码托管平台的协作流程，了解持续集成和持续部署的基本概念和实践。',
    image: '/images/book.png',
    link: '/resources',
    cardClass: 'ci-card-b',
  },
  {
    title: '构建与测试',
    description:
      '学习现代软件构建系统的使用，包括Maven、Gradle、npm等，掌握自动化测试的编写和执行，了解代码质量保证的最佳实践。',
    image: '/images/book.png',
    link: '/resources',
    cardClass: 'ci-card-c',
  },
  {
    title: '开源开发实践',
    description:
      '通过实际项目体验开源开发流程，学习如何提交Pull Request，参与代码审查，遵循开源项目的开发规范和最佳实践。',
    image: '/images/book.png',
    link: '/resources',
    cardClass: 'ci-card-a',
  },
  {
    title: '开源开发实战',
    description:
      '深入实际开源项目，学习如何发现和修复bug，如何添加新功能，如何与全球开发者协作，提升实际开发能力。',
    image: '/images/book.png',
    link: '/resources',
    cardClass: 'ci-card-b',
  },
  {
    title: '开源项目管理',
    description:
      '学习如何创建和维护开源项目，包括项目文档编写、社区建设、版本发布管理、用户支持等项目管理的各个方面。',
    image: '/images/book.png',
    link: '/resources',
    cardClass: 'ci-card-c',
  },
  {
    title: '开源贡献评价体系',
    description:
      '了解开源贡献的评价标准和方法，学习如何建立个人开源档案，掌握开源贡献对职业发展的价值和影响。',
    image: '/images/book.png',
    link: '/resources',
    cardClass: 'ci-card-a',
  },
];

const switchTab = (index) => {
  if (!courseSwiper.value) return;
  courseSwiper.value.slideTo(index, 500);
};

onMounted(() => {
  courseSwiper.value = new Swiper('.course-swiper', {
    centeredSlides: true,
    slidesPerView: 3,
    spaceBetween: 50,
    autoplay: {
      delay: 4000,
      disableOnInteraction: false,
    },
    effect: 'coverflow',
    coverflowEffect: {
      rotate: 15,
      stretch: 0,
      depth: 100,
      modifier: 1,
      slideShadows: true,
    },
    pagination: {
      el: '.course-pagination',
      clickable: true,
    },
    breakpoints: {
      1200: {
        slidesPerView: 3,
        spaceBetween: 50,
        coverflowEffect: { rotate: 15, stretch: 0, depth: 100, modifier: 1 },
      },
      900: {
        slidesPerView: 2.5,
        spaceBetween: 30,
        coverflowEffect: { rotate: 12, stretch: 0, depth: 80, modifier: 0.8 },
      },
      768: {
        slidesPerView: 2,
        spaceBetween: 20,
        coverflowEffect: { rotate: 10, stretch: 0, depth: 60, modifier: 0.7 },
      },
      480: {
        slidesPerView: 1.5,
        spaceBetween: 15,
        coverflowEffect: { rotate: 8, stretch: 0, depth: 40, modifier: 0.6 },
      },
      0: {
        slidesPerView: 1,
        spaceBetween: 10,
        coverflowEffect: { rotate: 5, stretch: 0, depth: 30, modifier: 0.5 },
      },
    },
    on: {
      slideChange() {
        activeTabIndex.value = this.activeIndex;
      },
      reachEnd() {
        setTimeout(() => {
          if (this.activeIndex === courseData.length - 1) this.slideTo(0, 500);
        }, 2000);
      },
    },
  });
});

onUnmounted(() => {
  if (courseSwiper.value && courseSwiper.value.autoplay) {
    courseSwiper.value.autoplay.stop();
  }
});
</script>

<style scoped>
/* Unified responsive scaling for the course intro */
.course-intro {
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
  /* bring back blue background of old course-section */
  background: url('/images/course-bg.jpg') center no-repeat;
  background-size: cover;
  padding-top: calc(var(--pad-y) * 1.2);
  padding-bottom: calc(var(--pad-y) * 1.2);
}

.ci-card-container { padding: 60px 0; position: relative; }

.course-swiper { overflow: visible; padding: 40px 0; }

.course-swiper .swiper-slide {
  width: auto;
  height: auto;
  padding-top: clamp(16px, 3vw, 40px);
  padding-bottom: clamp(16px, 3vw, 40px);
  transition: all 0.4s ease;
  display: flex;
  align-items: stretch;
  justify-content: center;
}

.course-swiper .swiper-slide .ci-card {
  width: 100%;
  height: 100%;
  transition: all 0.4s ease;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  gap: var(--gap);
  padding: var(--pad-y) var(--pad-x) calc(var(--pad-x) * 1.5) var(--pad-x);
  background-repeat: no-repeat;
  background-position: center;
  background-size: 100% 100%;
}

.course-swiper .swiper-slide-active .ci-card {
  transform: scale(1.0);
  opacity: 1;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.course-swiper .swiper-slide:not(.swiper-slide-active) .ci-card {
  transform: scale(0.75);
  opacity: 0.6;
}

/* Background variants */
.ci-card-a { background-image: url('/images/bg1.png'); }
.ci-card-b { background-image: url('/images/bg2.png'); }
.ci-card-c { background-image: url('/images/bg3.png'); }

/* Tabs */
.ci-tabs {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30px;
  gap: clamp(6px, 1.2vw, 16px);
  flex-wrap: wrap;
}

.ci-tabs li { cursor: pointer; transition: all 0.3s ease; }
.ci-tabs li a {
  display: block;
  padding: clamp(6px, 1vw, 10px) clamp(10px, 1.6vw, 16px);
  border-radius: 999px;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.24);
  color: rgba(255,255,255,0.9);
  font-size: clamp(12px, 1.5vw, 16px);
  text-decoration: none;
  transition: all 0.25s ease;
  user-select: none;
}
.ci-tabs li:hover a { filter: brightness(1.1); transform: translateY(-1px); }
.ci-tabs li.active a {
  background: #ffffff;
  color: #5277ff;
  border-color: transparent;
  box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}

.course-pagination { position: relative; margin-top: 30px; text-align: center; }
.course-pagination .swiper-pagination-bullet { width: 12px; height: 12px; background: rgba(255,255,255,0.4); opacity: 0.6; margin: 0 6px; transition: all 0.3s ease; }
.course-pagination .swiper-pagination-bullet-active { background: #fff; opacity: 1; transform: scale(1.2); }

/* Card internals responsive sizing */
.ci-title { font-size: var(--title-fs); color: #fff; font-weight: bold; margin-bottom: 12px; }
.ci-title a { color: #fff; text-decoration: none; }
.ci-desc { font-size: var(--desc-fs); line-height: 1.8; margin-bottom: 16px; color: #fff; }
.ci-card .btn-more { width: var(--btn-w); height: var(--btn-h); font-size: clamp(12px, 1.6vw, 16px); background: #fff; color: #5277ff; border-radius: 50px; font-weight: 600; }

.ci-photo { position: relative; display: flex; align-items: center; justify-content: center; width: var(--photo-w); height: var(--photo-h); border-radius: 20px; background: #fff; }
.ci-photo::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: var(--mask-h); background: url('/images/mask.png') no-repeat; background-size: 100% 100%; }
.ci-photo-box { margin-top: calc(var(--photo-h) * -0.49); }

/* Title color on blue background */
.course-intro :deep(.page-title) { color: #ffffff; }

/* Breakpoints (mild adjustments) */
@media (min-width: 1200px) { .ci-card-container { padding: 80px 0; } }

@media (max-width: 899px) and (min-width: 768px) {
  .ci-card-container { padding: 50px 0; }
  .ci-tabs { flex-wrap: wrap; justify-content: center; }
  .ci-tabs li { margin: 5px; }
}

@media (max-width: 767px) and (min-width: 480px) {
  .ci-card-container { padding: 40px 0; min-height: 320px; }
  .course-swiper { padding: 20px 0; }
  .course-swiper .swiper-slide:not(.swiper-slide-active) .ci-card { transform: scale(0.9); opacity: 0.8; }
  .ci-tabs { flex-wrap: wrap; justify-content: center; padding: 0 10px; }
  .ci-tabs li { margin: 4px; }
}

@media (max-width: 479px) {
  .ci-card-container { padding: 32px 0; min-height: 280px; }
  .course-swiper { padding: 15px 0; }
  .course-swiper .swiper-slide { padding: 15px 0; }
  .course-swiper .swiper-slide .ci-card { border-radius: 15px; }
  .course-swiper .swiper-slide:not(.swiper-slide-active) .ci-card { transform: scale(0.95); opacity: 0.85; }
  .ci-tabs { flex-wrap: wrap; justify-content: center; padding: 0 5px; }
  .ci-tabs li { margin: 2px; font-size: 12px; }
  .ci-tabs li a { padding: 8px 12px; }
}
</style>
