<template>
  <div class="page">
    <div class="container">
      <div class="page-title">作业任务发布墙</div>
      <div class="card-cels">
        <ul class="row card-row">
          <li class="col-md-4" v-for="n in 12" :key="n">
            <div class="card-cell">
              <a href="" class="card-img scale">
                <img :src="`/images/work${(n % 4) + 1}.png`" alt="">
              </a>
              <div class="card-grid mb-10">
                <div class="card-title"><a href="">接口开发教程</a></div>
                <div class="card-time">2025-01-17</div>
              </div>
              <div class="card-desc mb-10">
                Rust 语言的《The Rust Programming Langu，我每年还会推出一个符合当下教育趋势而...
              </div>
              <div class="card-items mb-15">
                12课时 | 164人看过
              </div>
              <a href="" class="btn btn-primary">立即学习</a>
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
// Logic for the homework page
</script>

<style scoped>
/* Scoped styles for the homework page */
</style>
