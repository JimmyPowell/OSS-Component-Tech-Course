<template>
  <div class="welcome-container">
    <h1>管理员欢迎页</h1>
    <p>欢迎来到管理员控制面板。您可以在左侧菜单中管理网站的各项内容。</p>
    <div class="info-cards">
      <div class="card">
        <h3>用户管理</h3>
        <p>查看和管理网站用户信息。</p>
      </div>
      <div class="card">
        <h3>内容管理</h3>
        <p>管理PPT、视频、作业等课程资源。</p>
      </div>
      <div class="card">
        <h3>社区管理</h3>
        <p>管理作品展示和论坛帖子。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// Welcome page logic can be added here if needed
</script>

<style scoped>
.welcome-container {
  padding: 2rem;
}

.welcome-container h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.welcome-container p {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin-bottom: 2rem;
}

.info-cards {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex: 1;
  min-width: 250px;
}

.card h3 {
  margin-top: 0;
  color: #3498db;
}

.card p {
  margin-bottom: 0;
  color: #555;
}
</style>
