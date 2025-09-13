<template>
  <div class="cc">
    <div class="swiper cc-swiper" ref="containerEl">
      <div class="swiper-wrapper">
        <div v-for="(c, i) in courses" :key="i" class="swiper-slide">
          <div class="cc-card" :class="bgClass(i)">
            <div class="cc-inner">
              <div class="cc-photo">
                <img :src="c.image || '/images/book.png'" :alt="c.title" />
              </div>
              <div class="cc-text">
                <div class="cc-title">{{ c.title }}</div>
                <div class="cc-desc">{{ c.description }}</div>
                <a class="cc-btn" :href="c.link">进入课程</a>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="swiper-pagination"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineExpose, onMounted, onBeforeUnmount, defineEmits } from 'vue'
import Swiper from 'swiper/bundle'
import 'swiper/css'

const props = defineProps({
  courses: { type: Array, default: () => [] }
})
const containerEl = ref(null)
let swiper = null
const emit = defineEmits(['slideChange'])

const bgClass = (i) => ['cc-bg-a','cc-bg-b','cc-bg-c'][i % 3]

onMounted(() => {
  swiper = new Swiper(containerEl.value, {
    slidesPerView: 1,
    spaceBetween: 16,
    loop: true,
    centeredSlides: true,
    centeredSlidesBounds: true,
    autoplay: { delay: 4000, disableOnInteraction: false },
    pagination: { el: '.swiper-pagination', clickable: true },
    breakpoints: {
      900: { slidesPerView: 2, spaceBetween: 20 },
      1280: { slidesPerView: 3, spaceBetween: 24 },
    },
    on: {
      slideChange(sw) { emit('slideChange', sw.realIndex) }
    }
  })
})

onBeforeUnmount(() => { if (swiper) swiper.destroy(true, false) })

function slideTo(index, speed = 400) { if (swiper) swiper.slideToLoop(index, speed) }

defineExpose({ slideTo })
</script>

<style scoped>
.cc { position: relative; }
.cc-swiper { overflow: visible; padding: 10px 0; }
.swiper-slide { display: flex; justify-content: center; }

/* 卡片等比，随列数自适应；无书本图片，仅背景+文本 */
.cc-card {
  position: relative;
  width: 100%;
  max-width: 520px;
  aspect-ratio: 5 / 6;
  border-radius: 16px;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
}
.cc-bg-a { background-image: url('/images/bg1.png'); }
.cc-bg-b { background-image: url('/images/bg2.png'); }
.cc-bg-c { background-image: url('/images/bg3.png'); }

.cc-card::before{ content:""; position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,0.06), rgba(0,0,0,0.35)); }
.cc-inner { position: relative; z-index:1; height:100%; padding: clamp(16px, 2.2vw, 24px); display:flex; flex-direction: column; justify-content:flex-end; gap: clamp(12px, 1.2vw, 16px); }
.cc-photo{ align-self:center; background:#fff; border-radius: 16px; width: min(68%, 420px); aspect-ratio: 5 / 4; display:flex; align-items:center; justify-content:center; box-shadow: 0 8px 20px rgba(0,0,0,0.08); }
.cc-photo img{ width:70%; height:auto; object-fit: contain; display:block; }
.cc-text{ color:#fff; }
.cc-title{ font-weight:700; font-size: clamp(18px, 2vw, 24px); margin-bottom:8px; }
.cc-desc{ font-size: clamp(12px, 1.2vw, 14px); line-height:1.6; margin-bottom:12px; max-height: 4.6em; overflow:hidden; }
.cc-btn{ display:inline-block; background:#fff; color:#5277ff; border-radius:999px; padding:8px 16px; font-weight:600; text-decoration:none; }

/* 中间卡片突出、两侧弱化 */
.swiper-slide .cc-card { transform: scale(0.92); opacity: 0.85; transition: transform .35s ease, opacity .35s ease, box-shadow .35s ease; }
.swiper-slide-prev .cc-card, .swiper-slide-next .cc-card { transform: scale(0.95); opacity: 0.9; }
.swiper-slide-active .cc-card { transform: scale(1.04); opacity: 1; box-shadow: 0 18px 44px rgba(0,0,0,0.18); }
</style>
