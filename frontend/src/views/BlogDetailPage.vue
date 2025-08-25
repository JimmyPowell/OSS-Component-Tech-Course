<template>
  <div class="page">
    <div class="container">
      <!-- Loading state -->
      <div v-if="loading" class="loading-container">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
        <p class="mt-3">正在加载博客内容...</p>
      </div>

      <!-- Blog content -->
      <div v-else-if="blog" class="blog-detail">
        <!-- Blog header -->
        <div class="blog-header">
          <div class="blog-meta-header">
            <nav aria-label="breadcrumb">
              <ol class="breadcrumb">
                <li class="breadcrumb-item">
                  <router-link to="/community">开源社区</router-link>
                </li>
                <li class="breadcrumb-item active" aria-current="page">技术博客</li>
              </ol>
            </nav>
          </div>
          
          <h1 class="blog-title">{{ blog.title }}</h1>
          
          <div class="blog-meta">
            <div class="author-info">
              <img 
                v-if="blog.author && blog.author.avatar_url"
                :src="blog.author.avatar_url" 
                :alt="blog.author.username"
                class="author-avatar"
              >
              <div class="author-placeholder" v-else>
                <i class="bi bi-person-circle"></i>
              </div>
              <div class="author-details">
                <span class="author-name">
                  {{ blog.author ? (blog.author.real_name || blog.author.username) : '未知作者' }}
                </span>
                <span class="publish-time">{{ formatTime(blog.created_at) }}</span>
              </div>
            </div>
            
            <div class="blog-stats">
              <span class="stat-item">
                <i class="bi bi-eye"></i>
                {{ blog.view_count || 0 }} 阅读
              </span>
              <span class="stat-item">
                <i class="bi bi-heart"></i>
                {{ blog.like_count || 0 }} 点赞
              </span>
            </div>
          </div>

          <!-- Tags -->
          <div v-if="blog.tags && blog.tags.length > 0" class="blog-tags">
            <span 
              v-for="tag in blog.tags" 
              :key="tag.id"
              class="blog-tag"
              :style="{ backgroundColor: tag.color || '#007bff' }"
            >
              {{ tag.name }}
            </span>
          </div>
        </div>

        <!-- Blog cover image -->
        <div v-if="blog.cover_url" class="blog-cover">
          <img 
            :src="blog.cover_url" 
            :alt="blog.title"
            class="blog-cover-image"
            @error="handleImageError"
          >
        </div>

        <!-- Blog content -->
        <div class="blog-content">
          <div v-if="blog.summary" class="blog-summary">
            <h3>摘要</h3>
            <p>{{ blog.summary }}</p>
          </div>
          
          <div class="blog-body" v-html="formatContent(blog.content)"></div>
        </div>

        <!-- Blog footer -->
        <div class="blog-footer">
          <div class="footer-left">
            <router-link to="/community/blogs" class="btn btn-outline-secondary">
              <i class="bi bi-arrow-left"></i>
              返回博客列表
            </router-link>
          </div>
          
          <div class="footer-right">
            <div class="like-button" @click="toggleLike" :class="{ liked: isLiked }">
              <span class="like-icon">👍</span>
              <span class="like-count">{{ blog.like_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Error state -->
      <div v-else class="error-container text-center">
        <i class="bi bi-exclamation-triangle display-1 text-warning"></i>
        <h3 class="mt-3">博客不存在</h3>
        <p class="text-muted">抱歉，您访问的博客可能已被删除或不存在。</p>
        <router-link to="/community" class="btn btn-primary">
          返回社区
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { blogApi } from '../api/blog'

const route = useRoute()
const blog = ref(null)
const loading = ref(true)
const isLiked = ref(false)

// 获取博客详情
const fetchBlogDetail = async () => {
  try {
    loading.value = true
    const blogUuid = route.params.uuid
    const response = await blogApi.getBlogByUuid(blogUuid)
    
    if (response.data.code === 200) {
      blog.value = response.data.data
      // 增加阅读量
      await blogApi.incrementViewCount(blogUuid)
    } else {
      console.error('获取博客详情失败:', response.data)
      blog.value = null
    }
  } catch (error) {
    console.error('获取博客详情失败:', error)
    blog.value = null
  } finally {
    loading.value = false
  }
}

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化内容（简单的HTML处理）
const formatContent = (content) => {
  if (!content) return ''
  // 这里可以添加更复杂的内容格式化逻辑
  return content.replace(/\n/g, '<br>')
}

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.src = '/images/blog-default.png'
}

// 切换点赞状态
const toggleLike = () => {
  // TODO: 实现点赞功能
  isLiked.value = !isLiked.value
  if (isLiked.value) {
    blog.value.like_count = (blog.value.like_count || 0) + 1
  } else {
    blog.value.like_count = Math.max(0, (blog.value.like_count || 0) - 1)
  }
}


onMounted(() => {
  fetchBlogDetail()
})
</script>

<style scoped>
.loading-container,
.error-container {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.blog-detail {
  max-width: 800px;
  margin: 0 auto;
}

.blog-header {
  margin-bottom: 2rem;
}

.blog-meta-header .breadcrumb {
  background: none;
  padding: 0;
  margin-bottom: 1rem;
}

.blog-title {
  font-size: 3.2rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.2;
  margin-bottom: 2rem;
}

.blog-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.author-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.author-placeholder {
  width: 60px;
  height: 60px;
  font-size: 3rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-size: 1.4rem;
  font-weight: 600;
  color: #5865f2;
}

.publish-time {
  font-size: 1.2rem;
  color: #6c757d;
}

.blog-stats {
  display: flex;
  gap: 2rem;
  font-size: 1.4rem;
  color: #6c757d;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.blog-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.blog-tag {
  font-size: 1.2rem;
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  font-weight: 500;
}

.blog-cover {
  margin-bottom: 2rem;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.blog-cover-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
}

.blog-content {
  line-height: 1.8;
  color: #2c3e50;
}

.blog-summary {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2.5rem;
  border-left: 4px solid #5865f2;
  font-size: 1.3rem;
}

.blog-summary h3 {
  font-size: 1.6rem;
  font-weight: 600;
  color: #5865f2;
  margin-bottom: 1rem;
}

.blog-body {
  font-size: 1.5rem;
  line-height: 1.8;
}

.blog-body h1, .blog-body h2, .blog-body h3, .blog-body h4, .blog-body h5, .blog-body h6 {
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.blog-body p {
  margin-bottom: 1.5rem;
}

.blog-body code {
  background: #f1f3f4;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.9em;
  color: #e83e8c;
}

.blog-footer {
  margin-top: 4rem;
  margin-bottom: 4rem;
  padding-top: 2.5rem;
  padding-bottom: 2rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
}

.footer-right {
  display: flex;
}

.like-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  border-radius: 50px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2rem;
  font-weight: 600;
  color: #6c757d;
}

.like-button:hover {
  background: #e3f2fd;
  border-color: #2196f3;
  color: #1976d2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
}

.like-button.liked {
  background: #e3f2fd;
  border-color: #2196f3;
  color: #1976d2;
}

.like-button.liked:hover {
  background: #bbdefb;
  border-color: #1976d2;
}

.like-icon {
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.like-button:hover .like-icon,
.like-button.liked .like-icon {
  transform: scale(1.2);
}

.like-count {
  font-size: 1.2rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .blog-title {
    font-size: 2rem;
  }
  
  .blog-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .blog-footer {
    flex-direction: column;
    gap: 1.5rem;
    align-items: stretch;
  }
  
  .footer-left,
  .footer-right {
    justify-content: center;
  }
}
</style>