<template>
  <div class="page">
    <div class="page-section">
      <div class="container">
        <div class="page-title">开源技术blog</div>
        <div class="swiper-mtr">
          <div class="swiper-container blog-swiper">
            <div class="swiper-wrapper">
              <div class="swiper-slide" v-for="n in 6" :key="`blog-${n}`">
                <div class="blog-card">
                  <div class="blog-head">
                    <img src="/images/head.png" alt="">
                    <span class="item">李明·2小时前</span>
                    <span class="tag">Java 开源框架”</span>
                  </div>
                  <div class="blog-body">
                    <div class="blog-title"><a href="">GitHub 趋势榜 - 实时热门项目和开发者追踪</a></div>
                    <div class="blog-desc">GitHub 趋势榜是开发者追踪实时热门项目和开发者的重要工具...</div>
                  </div>
                  <div class="blog-foot">
                    <div class="item">
                      <span class="iconfont icon-eyes"></span>
                      <span class="num">328 阅读</span>
                    </div>
                    <div class="item">
                      <span class="iconfont icon-dzs"></span>
                      <span class="num">24赞</span>
                    </div>
                    <div class="item">
                      <span class="iconfont icon-taolun"></span>
                      <span class="num">8评论</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="blog-pagination"></div>
          </div>
        </div>
      </div>
    </div>
    <div class="page-section">
      <div class="container">
        <div class="page-title">课程讨论互动社区</div>
        <div class="swiper-mtr">
          <div class="swiper-container discuss-swiper">
            <div class="swiper-wrapper">
              <div class="swiper-slide" v-for="n in 12" :key="`discuss-${n}`">
                <a href="" class="discuss-card">
                  <div class="discuss-photo">
                    <img src="/images/photo.png" class="discuss-pic" alt="">
                  </div>
                  <div class="discuss-bd">
                    <div class="discuss-time">2025.06.19</div>
                    <div class="discuss-title">
                      GitHub 趋势榜 - 实时热门项目和开发者追踪
                    </div>
                  </div>
                </a>
              </div>
            </div>
          </div>
          <div class="discuss-nav">
            <div class="discuss-nav-prev">
              <span class="iconfont icon-a-left"></span>
            </div>
            <div class="discuss-nav-next">
              <span class="iconfont icon-a-right"></span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="page-section">
      <div class="container">
        <div class="page-title">学生课程活跃度排名</div>
        <div class="rank-table">
          <div class="rank-table_head">
            <div class="rank-row">
              <div class="table-cell">排名</div>
              <div class="table-cell">头像</div>
              <div class="table-cell">用户昵称</div>
              <div class="table-cell">活跃时间</div>
            </div>
          </div>
          <div class="rank-table_tbody">
            <div class="rank-row" v-for="n in 10" :key="`rank-${n}`">
              <div class="table-cell">
                <div class="cell-num">
                  <img v-if="n <= 3" :src="`/images/rank${n}.png`" alt="">
                  <span v-else>{{ n }}</span>
                </div>
              </div>
              <div class="table-cell">
                <img src="/images/head.png" class="rank-avatar" alt="">
              </div>
              <div class="table-cell">
                张三
              </div>
              <div class="table-cell">
                189小时36分钟
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import Swiper from 'swiper/bundle';

onMounted(() => {
  new Swiper('.blog-swiper', {
    slidesPerView: 1,
    slidesPerColumn: 3,
    spaceBetween: 0,
    pagination: {
      el: '.blog-pagination',
      clickable: true,
    },
  });
  new Swiper('.discuss-swiper', {
    slidesPerView: 3,
    slidesPerColumn: 3,
    spaceBetween: 0,
    navigation: {
      nextEl: '.discuss-nav-next',
      prevEl: '.discuss-nav-prev',
    },
    breakpoints: {
      768: {
        slidesPerView: 1,
        slidesPerColumn: 1,
      },
    },
    pagination: {
      el: '.discuss-swiper .swiper-pagination',
      clickable: true,
    },
  });
});
</script>

<style scoped>
/* Scoped styles for the community page */
</style>
