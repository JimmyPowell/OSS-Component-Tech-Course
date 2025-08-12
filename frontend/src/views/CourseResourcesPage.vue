<template>
  <div class="page page-bg">
    <div class="container">
      <div class="page-title">课程课件</div>
      <div class="card-cels">
        <ul class="row card-row">
          <li class="col-md-4" v-for="n in 6" :key="`ppt-${n}`">
            <router-link :to="`/resource/${n}`">
              <div class="ppt-cell">
                <div class="ppt-img scale">
                  <img src="/images/ppt.png" alt="">
                </div>
                <div class="ppt-body">
                  <div class="card-grid mb-10">
                    <div class="card-title">第三章 开源软件版本控制管理</div>
                  </div>
                  <div class="card-desc">开源凭借集众智、采众长的特性，不断加速产业选代升级，促进产用</div>
                </div>
              </div>
            </router-link>
          </li>
        </ul>
        <div class="pagination-cell flex-center">
          <a href="" class="pagination-btn">
            <span class="iconfont icon-l-left"></span>
          </a>
          <a href="" class="pagination-btn active">1</a>
          <a href="" class="pagination-btn">2</a>
          <a href="" class="pagination-btn">3</a>
          <a href="" class="pagination-btn">4</a>
          <a href="" class="pagination-btn">5</a>
          <a href="" class="pagination-btn">
            <span class="iconfont icon-l-right"></span>
          </a>
          <div class="pagination-info flex-center">
            <span>跳至</span>
            <input type="text" class="form-control pagination-input">
            <span>页</span>
          </div>
        </div>
      </div>
      <div class="attachment-cells">
        <div class="attachment-title">附件</div>
        <ul class="row">
          <li class="col-md-6" v-for="n in 2" :key="`attachment-${n}`">
            <router-link :to="`/resource/attachment-${n}`" class="attachment-cell">
              <div class="attachment-icon">
                <img src="/images/pdf.png" alt="">
              </div>
              <div class="flex-col">
                <div class="card-grid mb-10">
                  <div class="card-title">附录A 以贡献为导向的开源人才评价机制</div>
                </div>
                <div class="card-desc">介绍高校开源贡献导向人才评价机制。该机制由工业和信息化部所属中国电子技术标准化研究院联合开放原子...</div>
              </div>
            </router-link>
          </li>
        </ul>
      </div>
      <div class="page-title">在线课程视频</div>
      <div class="card-cels">
        <ul class="row card-row">
          <li class="col-md-4" v-for="n in 9" :key="`video-${n}`">
            <div class="card-cell">
              <router-link :to="`/resource/video-${n}`" class="card-img scale">
                <img :src="`/images/show${(n % 3) + 2}.png`" alt="">
                <span class="v-icon"></span>
              </router-link>
              <div class="card-grid mb-10">
                <div class="card-title"><router-link :to="`/resource/video-${n}`">开源代码管理与持续集成</router-link></div>
              </div>
              <div class="card-desc">
                分析开源代码管理中的常见问题，介绍代码管理 全景常见问题，介绍代码管理 全景
              </div>
            </div>
          </li>
        </ul>
        <div class="pagination-cell flex-center">
          <a href="" class="pagination-btn">
            <span class="iconfont icon-l-left"></span>
          </a>
          <a href="" class="pagination-btn active">1</a>
          <a href="" class="pagination-btn">2</a>
          <a href="" class="pagination-btn">3</a>
          <a href="" class="pagination-btn">4</a>
          <a href="" class="pagination-btn">5</a>
          <a href="" class="pagination-btn">
            <span class="iconfont icon-l-right"></span>
          </a>
          <div class="pagination-info flex-center">
            <span>跳至</span>
            <input type="text" class="form-control pagination-input">
            <span>页</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Logic for the course resources page
</script>

<style scoped>
/* Scoped styles for the course resources page */
</style>
