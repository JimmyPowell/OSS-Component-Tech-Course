<template>
  <div class="page">
    <div class="page-section">
      <div class="container">
        <div class="page-title">开源技术博客</div>
        
        <!-- 加载状态 -->
        <div v-if="blogsLoading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>
        
        <!-- Blog列表 -->
        <div v-else-if="latestBlogs.length > 0" class="blog-list-vertical">
          <div 
            v-for="blog in latestBlogs.slice(0, 3)" 
            :key="blog.uuid" 
            class="blog-item-row mb-3"
            @click="goToBlogDetail(blog.uuid)"
          >
            <div class="row g-0 align-items-center">
              <!-- 封面图片 -->
              <div class="col-md-3" v-if="blog.cover_url">
                <div class="blog-cover-small">
                  <img 
                    :src="blog.cover_url" 
                    :alt="blog.title"
                    class="img-fluid rounded"
                  >
                </div>
              </div>
              
              <!-- 内容区域 -->
              <div :class="blog.cover_url ? 'col-md-9' : 'col-12'">
                <div class="blog-content-compact">
                  <div class="blog-header-info mb-2">
                    <div class="d-flex align-items-center">
                      <img 
                        v-if="blog.author && blog.author.avatar_url"
                        :src="blog.author.avatar_url" 
                        :alt="blog.author.username"
                        class="author-avatar-small me-2"
                      >
                      <div class="author-placeholder-small me-2" v-else>
                        <i class="bi bi-person-circle"></i>
                      </div>
                      <span class="author-name">
                        {{ blog.author ? (blog.author.real_name || blog.author.username) : '未知作者' }}
                      </span>
                      <span class="text-muted ms-2">·</span>
                      <span class="post-time text-muted ms-2">{{ formatTime(blog.created_at) }}</span>
                      <!-- 标签 -->
                      <span 
                        v-if="blog.tags && blog.tags.length > 0"
                        class="badge tag-small ms-2"
                        :style="{ backgroundColor: blog.tags[0].color }"
                      >
                        {{ blog.tags[0].name }}
                      </span>
                    </div>
                  </div>
                  
                  <h6 class="blog-title-compact mb-2">
                    <a href="#" @click.prevent="goToBlogDetail(blog.uuid)" class="text-decoration-none">
                      {{ blog.title }}
                    </a>
                  </h6>
                  
                  <p class="blog-desc-compact text-muted mb-2" v-if="blog.summary">
                    {{ blog.summary }}
                  </p>
                  
                  <div class="blog-stats-compact">
                    <span class="stat-item">
                      <i class="bi bi-eye"></i>
                      <span class="num">{{ blog.view_count }} 阅读</span>
                    </span>
                    <span class="stat-item ms-3">
                      <i class="bi bi-heart"></i>
                      <span class="num">{{ blog.like_count }} 赞</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 查看更多按钮 -->
          <div class="text-center mt-4">
            <router-link to="/blogs" class="btn btn-outline-primary btn-lg">
              查看更多博客
              <i class="bi bi-arrow-right ms-1"></i>
            </router-link>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="empty-state text-center py-5">
          <i class="bi bi-journal-x display-4 text-muted"></i>
          <p class="text-muted mt-3">暂无博客文章</p>
        </div>
      </div>
    </div>
    <div class="page-section">
      <div class="container">
        <div class="page-title">课程讨论互动社区</div>
        
        <!-- 热门帖子展示区域 -->
        <div class="forum-hot-posts" v-if="hotPosts.length > 0">
          <div class="post-grid">
            <div 
              v-for="post in hotPosts.slice(0, 6)" 
              :key="post.uuid"
              class="post-card"
              @click="navigateToPost(post.uuid)"
            >
              <div class="post-header">
                <div class="post-category" v-if="post.category">
                  <i class="category-icon" v-if="post.category.icon">{{ post.category.icon }}</i>
                  <span class="category-name">{{ post.category.name }}</span>
                </div>
                <div class="post-stats">
                  <span class="view-count">
                    <i class="icon">👀</i>
                    {{ post.view_count }}
                  </span>
                  <span class="reply-count">
                    <i class="icon">💬</i>
                    {{ post.reply_count }}
                  </span>
                </div>
              </div>
              
              <div class="post-title">{{ post.title }}</div>
              
              <div class="post-meta">
                <div class="post-author" v-if="post.author">
                  <img 
                    :src="post.author.avatar_url || '/images/head.png'" 
                    alt="头像" 
                    class="author-avatar"
                  >
                  <span class="author-name">
                    {{ post.author.username || post.author.real_name }}
                  </span>
                </div>
                <div class="post-time">
                  {{ formatTime(post.created_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else-if="!loading" class="empty-state">
          <p>暂无热门讨论，成为第一个发起讨论的人吧！</p>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <p>加载中...</p>
        </div>

        <!-- 进入论坛中心按钮 -->
        <div class="forum-actions">
          <button 
            class="btn-forum-center"
            @click="navigateToForumCenter"
          >
            <i class="icon">🚀</i>
            进入讨论中心
          </button>
        </div>
      </div>
    </div>
    <div class="page-section">
      <div class="container">
        <div class="page-title">学生课程活跃度排名</div>
        <div class="rank-coming-soon">
          <div class="coming-soon-content">
            <div class="coming-soon-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <h3 class="coming-soon-title">数据正在统计中</h3>
            <p class="coming-soon-subtitle">我们正在收集和分析学生的课程活跃度数据</p>
            <p class="coming-soon-message">敬请期待！</p>
            <div class="coming-soon-features">
              <div class="feature-item">
                <i class="fas fa-trophy"></i>
                <span>实时排行榜</span>
              </div>
              <div class="feature-item">
                <i class="fas fa-star"></i>
                <span>活跃度评分</span>
              </div>
              <div class="feature-item">
                <i class="fas fa-medal"></i>
                <span>成就徽章</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Swiper from 'swiper/bundle'
import { forumApi } from '../api/forum'
import { blogUtils } from '../api/blog'

const router = useRouter()

// 响应式数据
const hotPosts = ref([])
const loading = ref(false)
const latestBlogs = ref([])
const blogsLoading = ref(false)

// 获取热门帖子
const fetchHotPosts = async () => {
  loading.value = true
  try {
    const response = await forumApi.post.getHotPosts({ limit: 8, days: 30 })
    hotPosts.value = response.data.data || []
  } catch (error) {
    console.error('获取热门帖子失败:', error)
    hotPosts.value = []
  } finally {
    loading.value = false
  }
}

// 获取最新Blog文章
const fetchLatestBlogs = async () => {
  blogsLoading.value = true
  try {
    const response = await blogUtils.getLatestBlogs(3)
    if (response.data.code === 200) {
      latestBlogs.value = response.data.data || []
    }
  } catch (error) {
    console.error('获取最新博客失败:', error)
    latestBlogs.value = []
  } finally {
    blogsLoading.value = false
  }
}

// 格式化时间
const formatTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  }
}

// 导航到帖子详情
const navigateToPost = (uuid) => {
  router.push(`/community/forum/post/${uuid}`)
}

// 导航到论坛中心
const navigateToForumCenter = () => {
  router.push('/community/forum')
}

// 导航到Blog详情
const goToBlogDetail = (blogUuid) => {
  router.push(`/blog/${blogUuid}`)
}

onMounted(async () => {
  // 加载最新博客和热门帖子
  await Promise.all([
    fetchLatestBlogs(),
    fetchHotPosts()
  ])
})
</script>

<style scoped>
/* Discord风格论坛帖子样式 */
.forum-hot-posts {
  margin-bottom: 2rem;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.post-card {
  background: #ffffff;
  border: 1px solid #e3e5e8;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.post-card:hover {
  border-color: #5865f2;
  box-shadow: 0 4px 12px rgba(88, 101, 242, 0.15);
  transform: translateY(-2px);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.post-category {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f2f3f5;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
}

.category-icon {
  font-size: 1rem;
}

.category-name {
  font-weight: 500;
  color: #4f545c;
}

.post-stats {
  display: flex;
  gap: 1rem;
  font-size: 1rem;
  color: #72767d;
}

.view-count, .reply-count {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.post-title {
  font-size: 1.375rem;
  font-weight: 600;
  color: #2c2f33;
  line-height: 1.4;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.author-name {
  font-size: 1rem;
  font-weight: 500;
  color: #5865f2;
}

.post-time {
  font-size: 0.9375rem;
  color: #72767d;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #72767d;
  font-size: 1.1rem;
}

.forum-actions {
  text-align: center;
  margin-top: 2rem;
}

.btn-forum-center {
  background: linear-gradient(135deg, #5865f2, #7289da);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.875rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-forum-center:hover {
  background: linear-gradient(135deg, #4752c4, #677bc4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(88, 101, 242, 0.4);
}

.btn-forum-center .icon {
  font-size: 1.1rem;
}

/* 排行榜敬请期待样式 */
.rank-coming-soon {
  background: #ffffff;
  border: 2px solid #e9ecef;
  border-radius: 20px;
  padding: 0;
  margin: 2rem 0 4rem 0; /* 增加底部边距 */
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.rank-coming-soon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g fill="%23f8f9fa" fill-opacity="0.5"><circle cx="30" cy="30" r="2"/></g></svg>') repeat;
  pointer-events: none;
}

.coming-soon-content {
  text-align: center;
  padding: 4rem 2rem;
  color: #2c3e50;
  position: relative;
  z-index: 1;
}

.coming-soon-icon {
  margin-bottom: 2rem;
}

.coming-soon-icon i {
  font-size: 4rem;
  color: #667eea;
  opacity: 0.9;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.9;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

.coming-soon-title {
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.coming-soon-subtitle {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  opacity: 0.8;
  color: #6c757d;
}

.coming-soon-message {
  font-size: 1.5rem;
  font-weight: 500;
  margin-bottom: 2rem;
  color: #667eea;
}

.coming-soon-features {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
  margin-top: 2rem;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 15px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
  min-width: 120px;
}

.feature-item:hover {
  background: #e9ecef;
  transform: translateY(-5px);
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.feature-item i {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  color: #ffd700;
}

.feature-item span {
  font-size: 1rem;
  font-weight: 500;
  color: #495057;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .post-card {
    padding: 1rem;
  }
  
  .post-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .post-stats {
    align-self: flex-end;
  }
  
  .coming-soon-content {
    padding: 3rem 1rem;
  }
  
  .coming-soon-title {
    font-size: 2rem;
  }
  
  .coming-soon-subtitle {
    font-size: 1rem;
  }
  
  .coming-soon-message {
    font-size: 1.2rem;
  }
  
  .coming-soon-features {
    gap: 1rem;
  }
  
  .feature-item {
    min-width: 100px;
    padding: 1rem;
  }
}
/* Blog列表样式 */
.blog-list-vertical {
  max-width: 800px;
  margin: 0 auto;
}

.blog-item-row {
  background: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.blog-item-row:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #007bff;
}

.blog-cover-small {
  height: 120px;
  overflow: hidden;
  border-radius: 0.375rem;
}

.blog-cover-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.blog-content-compact {
  padding-left: 1rem;
}

.author-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.author-placeholder-small {
  width: 24px;
  height: 24px;
  font-size: 1.2rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
}

.author-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #495057;
}

.post-time {
  font-size: 0.875rem;
}

.tag-small {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.blog-title-compact {
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.4;
  margin: 0;
}

.blog-title-compact a {
  color: #2c3e50;
  transition: color 0.2s;
}

.blog-title-compact a:hover {
  color: #007bff;
}

.blog-desc-compact {
  font-size: 0.9rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}

.blog-stats-compact {
  font-size: 0.8rem;
  color: #6c757d;
}

.blog-stats-compact .stat-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

@media (max-width: 768px) {
  .blog-content-compact {
    padding-left: 0;
    margin-top: 1rem;
  }
  
  .blog-cover-small {
    height: 100px;
  }
  
  .blog-header-info {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .blog-title-compact {
    font-size: 1rem;
  }
}
</style>
