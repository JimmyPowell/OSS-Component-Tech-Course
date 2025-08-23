<template>
  <div class="forum-center">
    <!-- 页面头部 -->
    <div class="forum-header">
      <div class="container">
        <div class="header-content">
          <div class="header-info">
            <h1 class="forum-title">
              <i class="title-icon">💬</i>
              讨论中心
            </h1>
            <p class="forum-description">欢迎来到课程讨论社区，在这里分享想法、提出问题、互相学习</p>
          </div>
          <button 
            class="btn-create-post" 
            @click="showCreatePostModal = true"
          >
            <i class="icon">✏️</i>
            发表讨论
          </button>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="forum-main">
      <div class="container">
        <div class="forum-layout">
          <!-- 左侧边栏 - 分类列表 -->
          <aside class="forum-sidebar">
            <div class="sidebar-section">
              <h3 class="section-title">讨论分类</h3>
              <div class="category-list">
                <div 
                  v-for="category in categories" 
                  :key="category.uuid"
                  class="category-item"
                  :class="{ active: selectedCategory === category.uuid }"
                  @click="selectCategory(category.uuid)"
                >
                  <div class="category-info">
                    <span class="category-icon" v-if="category.icon">{{ category.icon }}</span>
                    <span class="category-name">{{ category.name }}</span>
                  </div>
                  <span class="post-count">{{ category.post_count }}</span>
                </div>
                <div 
                  class="category-item"
                  :class="{ active: selectedCategory === null }"
                  @click="selectCategory(null)"
                >
                  <div class="category-info">
                    <span class="category-icon">📋</span>
                    <span class="category-name">全部讨论</span>
                  </div>
                  <span class="post-count">{{ totalPosts }}</span>
                </div>
              </div>
            </div>

            <!-- 热门讨论 -->
            <div class="sidebar-section">
              <h3 class="section-title">热门讨论</h3>
              <div class="hot-posts-list">
                <div 
                  v-for="post in hotPosts.slice(0, 5)" 
                  :key="post.uuid"
                  class="hot-post-item"
                  @click="navigateToPost(post.uuid)"
                >
                  <div class="hot-post-title">{{ post.title }}</div>
                  <div class="hot-post-stats">
                    <span class="stat">👀 {{ post.view_count }}</span>
                    <span class="stat">💬 {{ post.reply_count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </aside>

          <!-- 主内容区 - 帖子列表 -->
          <main class="forum-content">
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
                    placeholder="搜索讨论..."
                    @keyup.enter="searchPosts"
                    class="search-input"
                  >
                  <button @click="searchPosts" class="search-btn">🔍</button>
                </div>
              </div>
            </div>

            <!-- 帖子列表 -->
            <div class="posts-list">
              <div 
                v-for="post in posts" 
                :key="post.uuid"
                class="post-item"
                @click="navigateToPost(post.uuid)"
              >
                <!-- 帖子头部 -->
                <div class="post-header">
                  <div class="post-category" v-if="post.category">
                    <span class="category-tag">{{ post.category.name }}</span>
                  </div>
                  <div class="post-badges">
                    <span v-if="post.is_pinned" class="badge pinned">📌 置顶</span>
                    <span v-if="post.is_locked" class="badge locked">🔒 锁定</span>
                  </div>
                </div>

                <!-- 帖子内容 -->
                <div class="post-content">
                  <h3 class="post-title">{{ post.title }}</h3>
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
                    <span class="post-time">{{ formatTime(post.created_at) }}</span>
                  </div>
                </div>

                <!-- 帖子统计 -->
                <div class="post-stats">
                  <div class="stat-item">
                    <span class="stat-icon">👀</span>
                    <span class="stat-value">{{ post.view_count }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-icon">💬</span>
                    <span class="stat-value">{{ post.reply_count }}</span>
                  </div>
                  <div class="last-reply" v-if="post.last_reply_at">
                    <span class="reply-time">{{ formatTime(post.last_reply_at) }}</span>
                    <span class="reply-author" v-if="post.last_reply_user">
                      {{ post.last_reply_user.username || post.last_reply_user.real_name }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 加载更多 -->
              <div v-if="hasMore" class="load-more">
                <button 
                  @click="loadMorePosts"
                  :disabled="loading"
                  class="btn-load-more"
                >
                  {{ loading ? '加载中...' : '加载更多' }}
                </button>
              </div>

              <!-- 空状态 -->
              <div v-if="posts.length === 0 && !loading" class="empty-state">
                <div class="empty-icon">📝</div>
                <h3>暂无讨论</h3>
                <p>成为第一个发起讨论的人吧！</p>
                <button @click="showCreatePostModal = true" class="btn-create-first">
                  发表第一个讨论
                </button>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>

    <!-- 创建帖子弹窗 -->
    <CreatePostModal 
      v-if="showCreatePostModal"
      :categories="categories"
      @close="showCreatePostModal = false"
      @created="handlePostCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { forumApi } from '../api/forum'
import CreatePostModal from '../components/forum/CreatePostModal.vue'

const router = useRouter()

// 响应式数据
const categories = ref([])
const posts = ref([])
const hotPosts = ref([])
const loading = ref(false)
const showCreatePostModal = ref(false)

// 筛选和搜索
const selectedCategory = ref(null)
const searchQuery = ref('')
const currentSort = ref('latest')

// 分页
const currentPage = ref(1)
const pageSize = 20
const totalPosts = ref(0)

// 排序选项
const sortOptions = [
  { value: 'latest', label: '最新回复' },
  { value: 'created', label: '发布时间' },
  { value: 'views', label: '浏览数' },
  { value: 'replies', label: '回复数' }
]

// 计算属性
const hasMore = computed(() => {
  return posts.value.length < totalPosts.value
})

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await forumApi.category.getActiveCategories()
    categories.value = response.data.data || []
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

// 获取热门帖子
const fetchHotPosts = async () => {
  try {
    const response = await forumApi.post.getHotPosts({ limit: 10 })
    hotPosts.value = response.data.data || []
  } catch (error) {
    console.error('获取热门帖子失败:', error)
  }
}

// 获取帖子列表
const fetchPosts = async (isLoadMore = false) => {
  loading.value = true
  try {
    const params = {
      skip: isLoadMore ? posts.value.length : 0,
      limit: pageSize,
      category_id: selectedCategory.value,
      title: searchQuery.value || undefined
    }

    const response = await forumApi.post.getPosts(params)
    const data = response.data.data
    
    if (isLoadMore) {
      posts.value.push(...(data.items || []))
    } else {
      posts.value = data.items || []
    }
    
    totalPosts.value = data.total || 0
  } catch (error) {
    console.error('获取帖子失败:', error)
    posts.value = []
  } finally {
    loading.value = false
  }
}

// 选择分类
const selectCategory = (categoryUuid) => {
  selectedCategory.value = categoryUuid
  currentPage.value = 1
  fetchPosts()
}

// 改变排序
const changeSort = (sortValue) => {
  currentSort.value = sortValue
  currentPage.value = 1
  // TODO: 实现排序逻辑
  fetchPosts()
}

// 搜索帖子
const searchPosts = () => {
  currentPage.value = 1
  fetchPosts()
}

// 加载更多
const loadMorePosts = () => {
  fetchPosts(true)
}

// 导航到帖子详情
const navigateToPost = (uuid) => {
  router.push(`/community/forum/post/${uuid}`)
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

// 处理帖子创建成功
const handlePostCreated = () => {
  showCreatePostModal.value = false
  fetchPosts() // 刷新帖子列表
  fetchCategories() // 刷新分类计数
}

// 监听分类变化
watch(selectedCategory, () => {
  fetchPosts()
})

// 页面加载
onMounted(async () => {
  await Promise.all([
    fetchCategories(),
    fetchHotPosts(),
    fetchPosts()
  ])
})
</script>

<style scoped>
.forum-center {
  min-height: 100vh;
  background: #f6f7f9;
  padding-top: 80px; /* 避免被导航栏遮挡 */
}

.forum-header {
  background: #ffffff;
  border-bottom: 1px solid #e3e5e8;
  padding: 2rem 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info {
  flex: 1;
}

.forum-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c2f33;
  margin: 0 0 0.5rem 0;
}

.title-icon {
  font-size: 2.25rem;
}

.forum-description {
  color: #72767d;
  font-size: 1.5rem;
  margin: 0;
}

.btn-create-post {
  background: linear-gradient(135deg, #5865f2, #7289da);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.875rem 1.5rem;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-create-post:hover {
  background: linear-gradient(135deg, #4752c4, #677bc4);
  transform: translateY(-1px);
}

.forum-main {
  padding: 2rem 0;
}

.forum-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
}

/* 侧边栏样式 */
.forum-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sidebar-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #2c2f33;
  margin: 0 0 1rem 0;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-item:hover {
  background: #f2f3f5;
}

.category-item.active {
  background: #5865f2;
  color: white;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-icon {
  font-size: 1.25rem;
}

.category-name {
  font-weight: 500;
  font-size: 1.5rem;
}

.post-count {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 1.25rem;
  font-weight: 600;
}

.hot-posts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.hot-post-item {
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e3e5e8;
}

.hot-post-item:hover {
  background: #f8f9fa;
  border-color: #5865f2;
}

.hot-post-title {
  font-weight: 500;
  color: #2c2f33;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  font-size: 1.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hot-post-stats {
  display: flex;
  gap: 0.75rem;
  font-size: 1rem;
  color: #72767d;
}

/* 主内容区样式 */
.forum-content {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.content-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e3e5e8;
  background: #f8f9fa;
}

.sort-options {
  display: flex;
  gap: 0.5rem;
}

.sort-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e3e5e8;
  background: #ffffff;
  color: #4f545c;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 1.125rem;
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
  gap: 0.5rem;
}

.search-input {
  padding: 0.5rem 1rem;
  border: 1px solid #e3e5e8;
  border-radius: 6px;
  width: 200px;
  font-size: 1.125rem;
}

.search-input:focus {
  outline: none;
  border-color: #5865f2;
}

.search-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid #5865f2;
  background: #5865f2;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  background: #4752c4;
  border-color: #4752c4;
}

/* 帖子列表样式 */
.posts-list {
  padding: 0;
}

.post-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-bottom: 1px solid #e3e5e8;
  cursor: pointer;
  transition: all 0.3s ease;
}

.post-item:hover {
  background: #f8f9fa;
}

.post-item:last-child {
  border-bottom: none;
}

.post-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 80px;
}

.category-tag {
  background: #f2f3f5;
  color: #4f545c;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
}

.post-badges {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  border-radius: 10px;
  font-weight: 600;
}

.badge.pinned {
  background: #fef3cd;
  color: #856404;
}

.badge.locked {
  background: #f8d7da;
  color: #721c24;
}

.post-content {
  flex: 1;
  min-width: 0;
}

.post-title {
  font-size: 1.875rem;
  font-weight: 600;
  color: #2c2f33;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.375rem;
  color: #72767d;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.author-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
}

.author-name {
  font-weight: 500;
  color: #5865f2;
}

.post-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  min-width: 120px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 1.25rem;
  color: #72767d;
}

.last-reply {
  text-align: right;
  font-size: 1rem;
  color: #72767d;
  line-height: 1.3;
}

.reply-author {
  display: block;
  color: #5865f2;
  font-weight: 500;
}

/* 其他样式 */
.load-more {
  padding: 2rem;
  text-align: center;
}

.btn-load-more {
  padding: 0.75rem 2rem;
  border: 1px solid #5865f2;
  background: transparent;
  color: #5865f2;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.btn-load-more:hover:not(:disabled) {
  background: #5865f2;
  color: white;
}

.btn-load-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  padding: 4rem 2rem;
  text-align: center;
  color: #72767d;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.75rem;
  color: #2c2f33;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  font-size: 1.25rem;
  margin: 0 0 1.5rem 0;
}

.btn-create-first {
  background: linear-gradient(135deg, #5865f2, #7289da);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.875rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-create-first:hover {
  background: linear-gradient(135deg, #4752c4, #677bc4);
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .forum-layout {
    grid-template-columns: 240px 1fr;
  }
}

@media (max-width: 768px) {
  .forum-layout {
    grid-template-columns: 1fr;
  }
  
  .forum-sidebar {
    order: 2;
  }
  
  .forum-content {
    order: 1;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .content-toolbar {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .post-item {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .post-stats {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}
</style>