<template>
  <div class="admin-panel-page">
    <div class="container">
      <div class="section-header">
        <h2>管理面板</h2>
        <p class="section-desc">本页面仅对管理员开放，用于系统管理和配置</p>
      </div>
      
      <div class="admin-dashboard">
        <div class="admin-stats-row">
          <div class="admin-stat-card">
            <div class="stat-icon">
              <i class="iconfont icon-user"></i>
            </div>
            <div class="stat-content">
              <h3>用户管理</h3>
              <div class="stat-number">324</div>
              <div class="stat-desc">注册用户</div>
            </div>
          </div>
          
          <div class="admin-stat-card">
            <div class="stat-icon">
              <i class="iconfont icon-book"></i>
            </div>
            <div class="stat-content">
              <h3>课程资源</h3>
              <div class="stat-number">47</div>
              <div class="stat-desc">资源总数</div>
            </div>
          </div>
          
          <div class="admin-stat-card">
            <div class="stat-icon">
              <i class="iconfont icon-homework"></i>
            </div>
            <div class="stat-content">
              <h3>作业管理</h3>
              <div class="stat-number">12</div>
              <div class="stat-desc">待批阅</div>
            </div>
          </div>
          
          <div class="admin-stat-card">
            <div class="stat-icon">
              <i class="iconfont icon-chart"></i>
            </div>
            <div class="stat-content">
              <h3>系统日志</h3>
              <div class="stat-number">198</div>
              <div class="stat-desc">今日日志</div>
            </div>
          </div>
        </div>
        
        <div class="admin-panel-section">
          <h3>快速操作</h3>
          <div class="admin-actions">
            <button class="btn btn-primary">添加用户</button>
            <button class="btn btn-primary">上传资源</button>
            <button class="btn btn-primary">发布公告</button>
            <button class="btn btn-primary">系统设置</button>
          </div>
        </div>
        
        <div class="admin-panel-section">
          <h3>最近活动</h3>
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-time">10:32</div>
              <div class="activity-content">
                <strong>张三</strong> 提交了新的作业
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-time">09:15</div>
              <div class="activity-content">
                <strong>李四</strong> 上传了新的课程资源
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-time">昨天</div>
              <div class="activity-content">
                <strong>系统</strong> 自动备份完成
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-time">昨天</div>
              <div class="activity-content">
                <strong>王五</strong> 注册成为新用户
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
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// 确保只有管理员才能访问此页面
onMounted(() => {
  if (!authStore.isManager) {
    console.log('非管理员用户尝试访问管理面板');
    router.push('/');
  }
  console.log('管理面板加载，当前用户角色:', authStore.userRole);
});
</script>

<style scoped>
.admin-panel-page {
  padding: 40px 0;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-header h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.section-desc {
  color: #666;
  font-size: 16px;
}

.admin-stats-row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -15px;
  margin-bottom: 30px;
}

.admin-stat-card {
  flex: 1;
  min-width: 200px;
  margin: 15px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.admin-stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  background-color: #f0f3ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.stat-icon i {
  font-size: 24px;
  color: #545ae7;
}

.stat-content h3 {
  margin: 0 0 5px;
  font-size: 16px;
  color: #666;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-desc {
  font-size: 14px;
  color: #999;
}

.admin-panel-section {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.admin-panel-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 18px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.admin-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.btn-primary {
  background-color: #545ae7;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #4147b8;
}

.activity-list {
  display: flex;
  flex-direction: column;
}

.activity-item {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  width: 80px;
  color: #999;
}

.activity-content {
  flex: 1;
}

@media (max-width: 768px) {
  .admin-stats-row {
    flex-direction: column;
  }
  
  .admin-stat-card {
    width: 100%;
    margin: 10px 0;
  }
  
  .admin-actions {
    flex-direction: column;
  }
  
  .btn-primary {
    width: 100%;
    margin-bottom: 10px;
  }
}
</style>
