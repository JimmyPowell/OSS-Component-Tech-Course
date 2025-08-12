<template>
  <div class="page">
    <div class="container">
      <div class="page-title">优秀作品展示</div>
      <div class="card-cels">
        <ul class="row card-row">
          <li class="col-md-4" v-for="n in 15" :key="n">
            <div class="card-cell">
              <a href="" class="card-img scale">
                <img :src="`/images/show${(n % 3) + 1}.png`" alt="">
              </a>
              <div class="card-grid mb-10">
                <div class="card-title"><a href="">AI办公开源项目</a></div>
                <div class="card-time">2025-01-17</div>
              </div>
              <div class="card-meta">
                <img src="/images/avatat.png" alt="">
                <span>计算机学院·张子轩</span>
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
// Logic for the showcase page
</script>

<style scoped>
/* Scoped styles for the showcase page */
</style>
