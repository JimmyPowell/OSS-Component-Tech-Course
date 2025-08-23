<template>
  <div class="blog-list-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="container">
        <h1>开源技术博客</h1>
        <p class="lead">探索最新的开源技术趋势和实践经验</p>
      </div>
    </div>

    <div class="container mt-4">
      <div class="row">
        <!-- 主要内容区域 -->
        <div class="col-lg-8">
          <!-- 搜索区域 -->
          <div class="search-section mb-4">
            <div class="input-group">
              <input
                v-model="searchKeyword"
                type="text"
                class="form-control"
                placeholder="搜索博客文章..."
                @keyup.enter="handleSearch"
              >
              <button class="btn btn-primary" @click="handleSearch">
                <i class="bi bi-search"></i> 搜索
              </button>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">加载中...</span>
            </div>
            <div class="mt-2">加载中...</div>
          </div>

          <!-- Blog列表 -->
          <div v-else-if="blogs.length > 0" class="blog-list">
            <div
              v-for="blog in blogs"
              :key="blog.uuid"
              class="blog-item mb-4"
            >
              <div class="card">
                <div class="row g-0">
                  <!-- 封面图片 -->
                  <div class="col-md-4" v-if="blog.cover_url">
                    <img
                      :src="blog.cover_url"
                      :alt="blog.title"
                      class="blog-cover img-fluid rounded-start h-100 object-fit-cover"
                      @click="goToBlogDetail(blog.uuid)"
                    >
                  </div>
                  
                  <!-- 内容区域 -->
                  <div :class="blog.cover_url ? 'col-md-8' : 'col-12'">
                    <div class="card-body">
                      <!-- 标题 -->
                      <h5 class="card-title">
                        <a
                          href="#"
                          @click.prevent="goToBlogDetail(blog.uuid)"
                          class="text-decoration-none"
                        >
                          {{ blog.title }}
                        </a>
                      </h5>
                      
                      <!-- 摘要 -->
                      <p class="card-text" v-if="blog.summary">
                        {{ blog.summary }}
                      </p>
                      
                      <!-- 标签 -->
                      <div class="blog-tags mb-2" v-if="blog.tags && blog.tags.length > 0">
                        <span
                          v-for="tag in blog.tags"
                          :key="tag.id"
                          class="badge me-1"
                          :style="{ backgroundColor: tag.color }"
                        >
                          {{ tag.name }}
                        </span>
                      </div>
                      
                      <!-- 元信息 -->
                      <div class="blog-meta">
                        <small class="text-muted">
                          <i class="bi bi-person"></i>
                          {{ blog.author ? (blog.author.real_name || blog.author.username) : '未知作者' }}
                          <span class="ms-2">
                            <i class="bi bi-calendar"></i>
                            {{ formatDate(blog.created_at) }}
                          </span>
                          <span class="ms-2">
                            <i class="bi bi-eye"></i>
                            {{ blog.view_count }} 阅读
                          </span>
                          <span class="ms-2">
                            <i class="bi bi-heart"></i>
                            {{ blog.like_count }} 点赞
                          </span>
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state text-center py-5">
            <i class="bi bi-journal-x display-1 text-muted"></i>
            <h3 class="mt-3">暂无博客文章</h3>
            <p class="text-muted">{{ searchKeyword ? '没有找到相关文章' : '还没有发布任何博客文章' }}</p>
          </div>

          <!-- 分页 -->
          <nav v-if="totalPages > 1" aria-label="Blog pagination">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: currentPage <= 1 }">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">上一页</a>
              </li>
              
              <li
                v-for="page in visiblePages"
                :key="page"
                class="page-item"
                :class="{ active: page === currentPage }"
              >
                <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
              </li>
              
              <li class="page-item" :class="{ disabled: currentPage >= totalPages }">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">下一页</a>
              </li>
            </ul>
          </nav>
        </div>

        <!-- 侧边栏 -->
        <div class="col-lg-4">
          <!-- 热门标签 -->
          <div class="sidebar-section">
            <h5 class="sidebar-title">热门标签</h5>
            <div class="tag-cloud">
              <span
                v-for="tag in popularTags"
                :key="tag.id"
                class="badge tag-item me-2 mb-2"
                :style="{ backgroundColor: tag.color }"
                @click="filterByTag(tag.id)"
                style="cursor: pointer;"
              >
                {{ tag.name }}
                <span class="badge bg-light text-dark ms-1">{{ tag.blog_count }}</span>
              </span>
            </div>
          </div>

          <!-- 最新文章 -->
          <div class="sidebar-section mt-4">
            <h5 class="sidebar-title">最新文章</h5>
            <div class="latest-blogs">
              <div
                v-for="blog in latestBlogs"
                :key="blog.uuid"
                class="latest-blog-item mb-3"
              >
                <h6>
                  <a
                    href="#"
                    @click.prevent="goToBlogDetail(blog.uuid)"
                    class="text-decoration-none"
                  >
                    {{ blog.title }}
                  </a>
                </h6>
                <small class="text-muted">
                  {{ formatDate(blog.created_at) }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { blogApi, blogTagApi } from '@/api/blog'

export default {
  name: 'BlogListPage',
  setup() {
    const router = useRouter()
    const route = useRoute()

    // 响应式数据
    const loading = ref(false)
    const blogs = ref([])
    const popularTags = ref([])
    const latestBlogs = ref([])
    const searchKeyword = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalBlogs = ref(0)
    const selectedTagIds = ref([])

    // 计算属性
    const totalPages = computed(() => Math.ceil(totalBlogs.value / pageSize.value))
    
    const visiblePages = computed(() => {
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)
      const pages = []
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    // 方法
    const loadBlogs = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          size: pageSize.value,
          status: 'published'
        }

        if (searchKeyword.value.trim()) {
          params.keyword = searchKeyword.value.trim()
        }

        if (selectedTagIds.value.length > 0) {
          params.tag_ids = selectedTagIds.value
        }

        const response = await blogApi.searchBlogs(params)
        
        if (response.data.success) {
          const data = response.data.data
          blogs.value = data.items || []
          totalBlogs.value = data.total || 0
          currentPage.value = data.page || 1
        }
      } catch (error) {
        console.error('加载博客失败:', error)
        blogs.value = []
        totalBlogs.value = 0
      } finally {
        loading.value = false
      }
    }

    const loadPopularTags = async () => {
      try {
        const response = await blogTagApi.getPopularTags(10)
        if (response.data.success) {
          popularTags.value = response.data.data || []
        }
      } catch (error) {
        console.error('加载热门标签失败:', error)
      }
    }

    const loadLatestBlogs = async () => {
      try {
        const response = await blogApi.getBlogs({ skip: 0, limit: 5 })
        if (response.data.success) {
          latestBlogs.value = response.data.data || []
        }
      } catch (error) {
        console.error('加载最新文章失败:', error)
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadBlogs()
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadBlogs()
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }

    const filterByTag = (tagId) => {
      selectedTagIds.value = [tagId]
      searchKeyword.value = ''
      currentPage.value = 1
      loadBlogs()
    }

    const goToBlogDetail = (blogUuid) => {
      router.push(`/blog/${blogUuid}`)
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    // 监听路由变化
    watch(() => route.query, (newQuery) => {
      if (newQuery.keyword) {
        searchKeyword.value = newQuery.keyword
        handleSearch()
      }
    }, { immediate: true })

    // 生命周期
    onMounted(() => {
      loadBlogs()
      loadPopularTags()
      loadLatestBlogs()
    })

    return {
      loading,
      blogs,
      popularTags,
      latestBlogs,
      searchKeyword,
      currentPage,
      totalPages,
      visiblePages,
      loadBlogs,
      handleSearch,
      changePage,
      filterByTag,
      goToBlogDetail,
      formatDate
    }
  }
}
</script>

<style scoped>
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60px 0;
  margin-bottom: 0;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.search-section .input-group {
  max-width: 600px;
}

.blog-item {
  transition: transform 0.2s ease-in-out;
}

.blog-item:hover {
  transform: translateY(-2px);
}

.blog-cover {
  height: 200px;
  cursor: pointer;
}

.card-title a {
  color: #333;
  transition: color 0.2s;
}

.card-title a:hover {
  color: #007bff;
}

.blog-tags .badge {
  font-size: 0.75rem;
}

.blog-meta {
  border-top: 1px solid #eee;
  padding-top: 0.5rem;
}

.sidebar-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 0.375rem;
}

.sidebar-title {
  color: #495057;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #007bff;
}

.tag-cloud .tag-item {
  font-size: 0.875rem;
  transition: opacity 0.2s;
}

.tag-cloud .tag-item:hover {
  opacity: 0.8;
}

.latest-blog-item {
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #eee;
}

.latest-blog-item:last-child {
  border-bottom: none;
}

.latest-blog-item h6 a {
  color: #333;
  font-size: 0.9rem;
  line-height: 1.4;
}

.latest-blog-item h6 a:hover {
  color: #007bff;
}

.empty-state {
  color: #6c757d;
}

.pagination .page-link {
  color: #007bff;
  border: 1px solid #dee2e6;
}

.pagination .page-item.active .page-link {
  background-color: #007bff;
  border-color: #007bff;
}

.pagination .page-link:hover {
  background-color: #e9ecef;
  border-color: #adb5bd;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .page-header {
    padding: 40px 0;
  }
  
  .sidebar-section {
    margin-top: 2rem;
  }
}
</style>