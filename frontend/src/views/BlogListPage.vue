<template>
  <div class="blog-center">
    <!-- 页面头部 -->
    <div class="blog-header">
      <div class="container">
        <!-- 面包屑导航 -->
        <nav aria-label="breadcrumb" class="breadcrumb-nav">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/community">开源社区</router-link>
            </li>
            <li class="breadcrumb-item active" aria-current="page">技术博客</li>
          </ol>
        </nav>
        
        <div class="header-content">
          <div class="header-info">
            <h1 class="blog-title">
              <i class="title-icon">📚</i>
              技术博客
            </h1>
            <p class="blog-description">探索最新的技术趋势和开发实践，分享开源项目经验</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="blog-main">
      <div class="container">
        <div class="blog-layout">
          <!-- 左侧边栏 - 标签分类 -->
          <aside class="blog-sidebar">
            <div class="sidebar-section">
              <h3 class="section-title">博客分类</h3>
              <div class="tag-list">
                <div 
                  class="tag-item"
                  :class="{ active: selectedTagId === null }"
                  @click="selectTag(null)"
                >
                  <div class="tag-info">
                    <span class="tag-icon">📋</span>
                    <span class="tag-name">全部博客</span>
                  </div>
                  <span class="blog-count">{{ totalBlogs }}</span>
                </div>
                <div 
                  v-for="tag in popularTags" 
                  :key="tag.id"
                  class="tag-item"
                  :class="{ active: selectedTagId === tag.id }"
                  @click="selectTag(tag.id)"
                >
                  <div class="tag-info">
                    <span class="tag-icon">🏷️</span>
                    <span class="tag-name">{{ tag.name }}</span>
                  </div>
                  <span class="blog-count">{{ tag.blog_count || 0 }}</span>
                </div>
              </div>
            </div>

            <!-- 热门博客 -->
            <div class="sidebar-section">
              <h3 class="section-title">热门博客</h3>
              <div class="hot-blogs-list">
                <div 
                  v-for="blog in hotBlogs.slice(0, 5)" 
                  :key="blog.uuid"
                  class="hot-blog-item"
                  @click="goToBlogDetail(blog.uuid)"
                >
                  <div class="hot-blog-title">{{ blog.title }}</div>
                  <div class="hot-blog-stats">
                    <span class="stat">👀 {{ blog.view_count }}</span>
                    <span class="stat">💖 {{ blog.like_count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </aside>

          <!-- 主内容区 - 博客列表 -->
          <main class="blog-content">
            <!-- 工具栏 -->
            <div class="content-toolbar">
              <div class="toolbar-left">
                <div class="sort-options">
                  <button 
                    v-for="option in sortOptions" 
                    :key="option.value"
                    class="sort-btn"
                    :class="{ active: currentSort === option.value }"
                    @click="changeSort(option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>
              <div class="toolbar-right">
                <div class="search-box">
                  <input 
                    v-model="searchQuery"
                    type="text" 
                    placeholder="搜索博客..."
                    @keyup.enter="searchBlogs"
                    class="search-input"
                  >
                  <button @click="searchBlogs" class="search-btn">🔍</button>
                </div>
              </div>
            </div>

            <!-- 博客列表 -->
            <div class="blogs-list">
              <div 
                v-for="blog in blogs" 
                :key="blog.uuid"
                class="blog-item"
                @click="goToBlogDetail(blog.uuid)"
              >
                <!-- 博客头部 -->
                <div class="blog-header-item">
                  <div class="blog-category" v-if="blog.tags && blog.tags.length > 0">
                    <span class="category-tag">{{ blog.tags[0].name }}</span>
                  </div>
                </div>

                <!-- 博客内容 -->
                <div class="blog-content-item">
                  <h3 class="blog-title-item">{{ blog.title }}</h3>
                  <p class="blog-summary-item" v-if="blog.summary">
                    {{ truncateText(blog.summary, 120) }}
                  </p>
                  <div class="blog-meta">
                    <div class="blog-author" v-if="blog.author">
                      <img 
                        :src="blog.author.avatar_url || '/images/head.png'" 
                        alt="头像"
                        class="author-avatar"
                      >
                      <span class="author-name">
                        {{ blog.author.username || blog.author.real_name }}
                      </span>
                    </div>
                    <span class="blog-time">{{ formatTime(blog.created_at) }}</span>
                  </div>
                </div>

                <!-- 博客统计 -->
                <div class="blog-stats">
                  <div class="stat-item">
                    <span class="stat-icon">👀</span>
                    <span class="stat-value">{{ blog.view_count }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-icon">💖</span>
                    <span class="stat-value">{{ blog.like_count }}</span>
                  </div>
                  <div class="last-update">
                    <span class="update-time">{{ formatTime(blog.created_at) }}</span>
                    <span class="update-author" v-if="blog.author">
                      {{ blog.author.username || blog.author.real_name }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 加载更多 -->
              <div v-if="hasMore" class="load-more">
                <button 
                  @click="loadMoreBlogs"
                  :disabled="loading"
                  class="btn-load-more"
                >
                  {{ loading ? '加载中...' : '加载更多' }}
                </button>
              </div>

              <!-- 空状态 -->
              <div v-if="blogs.length === 0 && !loading" class="empty-state">
                <div class="empty-icon">📝</div>
                <h3>暂无博客文章</h3>
                <p>{{ searchQuery ? '没有找到匹配的博客' : '还没有发布任何博客文章' }}</p>
                <router-link to="/community" class="btn-back-community">
                  返回开源社区
                </router-link>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { blogApi } from '../api/blog'

const router = useRouter()

// 响应式数据
const blogs = ref([])
const popularTags = ref([])
const hotBlogs = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedTagId = ref(null)
const currentSort = ref('created_at')
const currentPage = ref(1)
const totalBlogs = ref(0)
const pageSize = 12

// 排序选项
const sortOptions = [
  { label: '最新回复', value: 'created_at' },
  { label: '发布时间', value: 'created_at' },
  { label: '浏览数', value: 'view_count' },
  { label: '回复数', value: 'like_count' }
]

// 计算属性
const hasMore = computed(() => blogs.value.length < totalBlogs.value)

// 获取博客列表
const fetchBlogs = async (loadMore = false) => {
  try {
    loading.value = true
    
    const params = {
      page: loadMore ? currentPage.value + 1 : 1,
      size: pageSize,
      keyword: searchQuery.value || undefined,
      tag_ids: selectedTagId.value ? [selectedTagId.value] : []
    }
    
    const response = await blogApi.searchBlogs(params)
    if (response.data.code === 200) {
      const data = response.data.data
      if (loadMore) {
        blogs.value = [...blogs.value, ...(data.items || [])]
        currentPage.value++
      } else {
        blogs.value = data.items || []
        currentPage.value = 1
      }
      totalBlogs.value = data.total || 0
    } else {
      console.error('获取博客列表失败:', response.data)
      if (!loadMore) {
        blogs.value = []
        totalBlogs.value = 0
      }
    }
  } catch (error) {
    console.error('获取博客列表失败:', error)
    if (!loadMore) {
      blogs.value = []
      totalBlogs.value = 0
    }
  } finally {
    loading.value = false
  }
}

// 获取热门标签
const fetchPopularTags = async () => {
  try {
    const response = await blogApi.getPopularTags({ limit: 10 })
    if (response.data.code === 200) {
      popularTags.value = response.data.data || []
    }
  } catch (error) {
    console.error('获取热门标签失败:', error)
  }
}

// 获取热门博客
const fetchHotBlogs = async () => {
  try {
    const response = await blogApi.getBlogs({ limit: 10, skip: 0 })
    if (response.data.code === 200) {
      hotBlogs.value = (response.data.data || []).sort((a, b) => (b.view_count || 0) - (a.view_count || 0))
    }
  } catch (error) {
    console.error('获取热门博客失败:', error)
  }
}

// 选择标签
const selectTag = (tagId) => {
  selectedTagId.value = tagId
  fetchBlogs()
}

// 改变排序
const changeSort = (sortValue) => {
  currentSort.value = sortValue
  fetchBlogs()
}

// 搜索博客
const searchBlogs = () => {
  fetchBlogs()
}

// 加载更多博客
const loadMoreBlogs = () => {
  fetchBlogs(true)
}

// 跳转到博客详情
const goToBlogDetail = (uuid) => {
  router.push(`/blog/${uuid}`)
}

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return ''
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

// 截取文本
const truncateText = (text, maxLength = 120) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

onMounted(async () => {
  await Promise.all([
    fetchBlogs(),
    fetchPopularTags(),
    fetchHotBlogs()
  ])
})
</script>

<style scoped>
/* 页面整体布局 */
.blog-center {
  min-height: 100vh;
  background: #f5f6fa;
}

/* 页面头部 */
.blog-header {
  background: white;
  color: #2c3e50;
  padding: 2rem 0;
  margin-top: 80px; /* 为导航栏留出空间 */
  border-bottom: 1px solid #e9ecef;
}

.breadcrumb-nav {
  margin-bottom: 1rem;
}

.breadcrumb {
  background: none;
  padding: 0;
  margin: 0;
}

.breadcrumb-item a {
  color: #5865f2;
  text-decoration: none;
}

.breadcrumb-item a:hover {
  color: #4752c4;
  text-decoration: underline;
}

.breadcrumb-item.active {
  color: #6c757d;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.blog-title {
  font-size: 3rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.title-icon {
  font-size: 2.5rem;
}

.blog-description {
  font-size: 1.2rem;
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
}

/* 主要内容区域 */
.blog-main {
  padding: 2rem 0;
}

.blog-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  align-items: start;
}

/* 左侧边栏 */
.blog-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sidebar-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #f1f3f4;
}

.tag-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tag-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.tag-item:hover {
  background: #f8f9fa;
  border-color: #e9ecef;
}

.tag-item.active {
  background: #5865f2;
  color: white;
}

.tag-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.tag-icon {
  font-size: 1.25rem;
}

.tag-name {
  font-weight: 500;
  font-size: 1.125rem;
}

.blog-count {
  background: #f1f3f4;
  color: #6c757d;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  min-width: 24px;
  text-align: center;
}

.tag-item.active .blog-count {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.hot-blogs-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.hot-blog-item {
  padding: 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #f1f3f4;
}

.hot-blog-item:hover {
  background: #f8f9fa;
  border-color: #5865f2;
}

.hot-blog-title {
  font-size: 1.125rem;
  font-weight: 500;
  color: #2c3e50;
  line-height: 1.4;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hot-blog-stats {
  display: flex;
  gap: 1rem;
  font-size: 1rem;
  color: #6c757d;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* 主内容区 */
.blog-content {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.content-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #f1f3f4;
  background: #fafbfc;
}

.sort-options {
  display: flex;
  gap: 0.5rem;
}

.sort-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e9ecef;
  background: white;
  color: #6c757d;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sort-btn:hover {
  border-color: #5865f2;
  color: #5865f2;
}

.sort-btn.active {
  background: #5865f2;
  border-color: #5865f2;
  color: white;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  overflow: hidden;
  min-width: 280px;
}

.search-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: none;
  outline: none;
  font-size: 0.875rem;
}

.search-btn {
  padding: 0.5rem 0.75rem;
  background: #5865f2;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.3s ease;
}

.search-btn:hover {
  background: #4752c4;
}

/* 博客列表 */
.blogs-list {
  padding: 0;
}

.blog-item {
  display: flex;
  align-items: center;
  padding: 2rem;
  border-bottom: 1px solid #f1f3f4;
  cursor: pointer;
  transition: all 0.3s ease;
}

.blog-item:hover {
  background: #f8f9fa;
}

.blog-item:last-child {
  border-bottom: none;
}

.blog-header-item {
  margin-right: 1rem;
}

.blog-category {
  margin-bottom: 0.5rem;
}

.category-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.375rem 1rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 500;
}

.blog-content-item {
  flex: 1;
  min-width: 0;
}

.blog-title-item {
  font-size: 1.75rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-summary-item {
  font-size: 1.25rem;
  color: #6c757d;
  line-height: 1.5;
  margin: 0 0 1rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.blog-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.author-name {
  font-size: 1.125rem;
  font-weight: 500;
  color: #5865f2;
}

.blog-time {
  font-size: 1rem;
  color: #6c757d;
}

.blog-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  margin-left: 1rem;
  min-width: 120px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  color: #6c757d;
}

.stat-icon {
  font-size: 1.25rem;
}

.last-update {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 0.75rem;
  color: #99aab5;
  line-height: 1.3;
}

.update-time {
  font-weight: 500;
}

.update-author {
  color: #5865f2;
}

/* 加载更多和空状态 */
.load-more {
  padding: 2rem;
  text-align: center;
}

.btn-load-more {
  background: #5865f2;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.75rem 2rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s ease;
}

.btn-load-more:hover:not(:disabled) {
  background: #4752c4;
}

.btn-load-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.empty-state p {
  font-size: 1rem;
  margin-bottom: 2rem;
}

.btn-back-community {
  background: #5865f2;
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: background 0.3s ease;
}

.btn-back-community:hover {
  background: #4752c4;
  color: white;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .blog-layout {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .blog-sidebar {
    order: 2;
  }
  
  .blog-content {
    order: 1;
  }
}

@media (max-width: 768px) {
  .blog-title {
    font-size: 2.5rem;
  }
  
  .content-toolbar {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .blog-item {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .blog-stats {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-left: 0;
    min-width: auto;
  }
  
  .last-update {
    align-items: flex-start;
  }
}
</style>