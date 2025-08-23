<template>
  <div class="blog-detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="container text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
        <div class="mt-2">加载中...</div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="container text-center py-5">
        <i class="bi bi-exclamation-triangle display-1 text-warning"></i>
        <h3 class="mt-3">文章未找到</h3>
        <p class="text-muted">{{ error }}</p>
        <router-link to="/blogs" class="btn btn-primary">返回博客列表</router-link>
      </div>
    </div>

    <!-- 文章内容 -->
    <div v-else-if="blog" class="blog-content">
      <div class="container">
        <div class="row">
          <!-- 主要内容区域 -->
          <div class="col-lg-8">
            <!-- 文章头部 -->
            <div class="blog-header">
              <!-- 面包屑导航 -->
              <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                  <li class="breadcrumb-item">
                    <router-link to="/">首页</router-link>
                  </li>
                  <li class="breadcrumb-item">
                    <router-link to="/blogs">博客</router-link>
                  </li>
                  <li class="breadcrumb-item active">{{ blog.title }}</li>
                </ol>
              </nav>

              <!-- 文章标题 -->
              <h1 class="blog-title">{{ blog.title }}</h1>

              <!-- 文章元信息 -->
              <div class="blog-meta mb-4">
                <div class="row align-items-center">
                  <div class="col-md-8">
                    <div class="author-info d-flex align-items-center">
                      <img
                        v-if="blog.author && blog.author.avatar_url"
                        :src="blog.author.avatar_url"
                        :alt="blog.author.username"
                        class="author-avatar me-3"
                      >
                      <div class="author-placeholder me-3" v-else>
                        <i class="bi bi-person-circle"></i>
                      </div>
                      <div>
                        <div class="author-name">
                          {{ blog.author ? (blog.author.real_name || blog.author.username) : '未知作者' }}
                        </div>
                        <small class="text-muted">
                          发布于 {{ formatDate(blog.created_at) }}
                          <span v-if="blog.updated_at !== blog.created_at">
                            · 更新于 {{ formatDate(blog.updated_at) }}
                          </span>
                        </small>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4 text-md-end">
                    <div class="blog-stats">
                      <span class="stat-item">
                        <i class="bi bi-eye"></i>
                        {{ blog.view_count }} 阅读
                      </span>
                      <span class="stat-item ms-3">
                        <i class="bi bi-heart"></i>
                        {{ blog.like_count }} 点赞
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 标签 -->
              <div class="blog-tags mb-4" v-if="blog.tags && blog.tags.length > 0">
                <span
                  v-for="tag in blog.tags"
                  :key="tag.id"
                  class="badge tag-badge me-2"
                  :style="{ backgroundColor: tag.color }"
                >
                  {{ tag.name }}
                </span>
              </div>

              <!-- 封面图片 -->
              <div class="blog-cover mb-4" v-if="blog.cover_url">
                <img
                  :src="blog.cover_url"
                  :alt="blog.title"
                  class="img-fluid rounded"
                >
              </div>
            </div>

            <!-- 文章内容 -->
            <div class="blog-body">
              <!-- 摘要 -->
              <div class="blog-summary mb-4" v-if="blog.summary">
                <div class="alert alert-info">
                  <strong>摘要：</strong>{{ blog.summary }}
                </div>
              </div>

              <!-- 正文内容 -->
              <div class="blog-content-body" v-html="renderedContent"></div>
            </div>

            <!-- 文章底部 -->
            <div class="blog-footer mt-5 pt-4 border-top">
              <div class="row">
                <div class="col-md-6">
                  <div class="author-card">
                    <h6>关于作者</h6>
                    <div class="d-flex align-items-center">
                      <img
                        v-if="blog.author && blog.author.avatar_url"
                        :src="blog.author.avatar_url"
                        :alt="blog.author.username"
                        class="author-avatar-large me-3"
                      >
                      <div class="author-placeholder-large me-3" v-else>
                        <i class="bi bi-person-circle"></i>
                      </div>
                      <div>
                        <div class="fw-semibold">
                          {{ blog.author ? (blog.author.real_name || blog.author.username) : '未知作者' }}
                        </div>
                        <small class="text-muted">技术分享者</small>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-6 text-md-end">
                  <div class="share-section">
                    <h6>分享文章</h6>
                    <div class="share-buttons">
                      <button class="btn btn-outline-primary btn-sm me-2" @click="copyLink">
                        <i class="bi bi-link-45deg"></i> 复制链接
                      </button>
                      <button class="btn btn-outline-success btn-sm" @click="shareToWeChat">
                        <i class="bi bi-wechat"></i> 微信分享
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 侧边栏 -->
          <div class="col-lg-4">
            <div class="blog-sidebar">
              <!-- 目录 -->
              <div class="sidebar-section toc-section" v-if="tableOfContents.length > 0">
                <h6 class="sidebar-title">文章目录</h6>
                <div class="table-of-contents">
                  <a
                    v-for="(item, index) in tableOfContents"
                    :key="index"
                    :href="`#${item.id}`"
                    :class="`toc-item toc-level-${item.level}`"
                    @click="scrollToHeading(item.id)"
                  >
                    {{ item.text }}
                  </a>
                </div>
              </div>

              <!-- 相关文章 -->
              <div class="sidebar-section related-section">
                <h6 class="sidebar-title">相关文章</h6>
                <div v-if="relatedBlogs.length > 0" class="related-blogs">
                  <div
                    v-for="relatedBlog in relatedBlogs"
                    :key="relatedBlog.uuid"
                    class="related-blog-item mb-3"
                  >
                    <h6>
                      <router-link
                        :to="`/blog/${relatedBlog.uuid}`"
                        class="text-decoration-none"
                      >
                        {{ relatedBlog.title }}
                      </router-link>
                    </h6>
                    <small class="text-muted">
                      {{ formatDate(relatedBlog.created_at) }}
                    </small>
                  </div>
                </div>
                <div v-else class="text-muted small">暂无相关文章</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { blogApi } from '@/api/blog'
import { marked } from 'marked'

export default {
  name: 'BlogDetailPage',
  setup() {
    const route = useRoute()
    const router = useRouter()

    // 响应式数据
    const loading = ref(true)
    const error = ref('')
    const blog = ref(null)
    const relatedBlogs = ref([])
    const tableOfContents = ref([])

    // 计算属性
    const renderedContent = computed(() => {
      if (!blog.value || !blog.value.content) return ''
      
      // 配置marked
      marked.setOptions({
        highlight: function(code, lang) {
          // 这里可以集成代码高亮库，比如highlight.js
          return code
        },
        breaks: true,
        gfm: true
      })
      
      return marked(blog.value.content)
    })

    // 方法
    const loadBlog = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const blogUuid = route.params.uuid
        const response = await blogApi.getBlogDetail(blogUuid)
        
        if (response.data.success) {
          blog.value = response.data.data
          
          // 增加浏览次数
          await blogApi.incrementViewCount(blogUuid, 1)
          
          // 生成目录
          await nextTick()
          generateTableOfContents()
          
          // 加载相关文章
          loadRelatedBlogs()
        } else {
          error.value = response.data.message || '文章加载失败'
        }
      } catch (err) {
        console.error('加载文章失败:', err)
        if (err.response && err.response.status === 404) {
          error.value = '文章不存在或已被删除'
        } else {
          error.value = '网络错误，请稍后重试'
        }
      } finally {
        loading.value = false
      }
    }

    const loadRelatedBlogs = async () => {
      if (!blog.value || !blog.value.tags || blog.value.tags.length === 0) return
      
      try {
        const tagIds = blog.value.tags.map(tag => tag.id)
        const response = await blogApi.searchBlogs({
          tag_ids: tagIds,
          size: 5
        })
        
        if (response.data.success) {
          // 排除当前文章
          relatedBlogs.value = (response.data.data.items || [])
            .filter(item => item.uuid !== blog.value.uuid)
            .slice(0, 4)
        }
      } catch (error) {
        console.error('加载相关文章失败:', error)
      }
    }

    const generateTableOfContents = () => {
      const content = document.querySelector('.blog-content-body')
      if (!content) return

      const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6')
      const toc = []
      
      headings.forEach((heading, index) => {
        const level = parseInt(heading.tagName.charAt(1))
        const text = heading.textContent.trim()
        const id = `heading-${index}`
        
        heading.id = id
        
        toc.push({
          id,
          text,
          level
        })
      })
      
      tableOfContents.value = toc
    }

    const scrollToHeading = (id) => {
      const element = document.getElementById(id)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const copyLink = async () => {
      try {
        await navigator.clipboard.writeText(window.location.href)
        // 这里可以添加一个toast提示
        alert('链接已复制到剪贴板')
      } catch (error) {
        console.error('复制链接失败:', error)
      }
    }

    const shareToWeChat = () => {
      // 这里可以集成微信分享SDK
      alert('请复制链接手动分享到微信')
    }

    // 生命周期
    onMounted(() => {
      loadBlog()
    })

    return {
      loading,
      error,
      blog,
      relatedBlogs,
      tableOfContents,
      renderedContent,
      formatDate,
      scrollToHeading,
      copyLink,
      shareToWeChat
    }
  }
}
</script>

<style scoped>
.loading-container, .error-container {
  min-height: 60vh;
  display: flex;
  align-items: center;
}

.blog-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.3;
  margin-bottom: 1.5rem;
}

.blog-meta {
  padding: 1.5rem 0;
  border-bottom: 2px solid #e9ecef;
}

.author-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.author-placeholder {
  width: 48px;
  height: 48px;
  font-size: 2.5rem;
  color: #6c757d;
}

.author-name {
  font-weight: 600;
  color: #495057;
}

.blog-stats .stat-item {
  color: #6c757d;
  font-size: 0.9rem;
}

.tag-badge {
  font-size: 0.85rem;
  padding: 0.5rem 0.75rem;
}

.blog-cover img {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
}

.blog-summary .alert {
  border-left: 4px solid #17a2b8;
  background-color: #f8f9fa;
  border-color: #bee5eb;
}

.blog-content-body {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #2c3e50;
}

/* Markdown内容样式 */
.blog-content-body :deep(h1),
.blog-content-body :deep(h2),
.blog-content-body :deep(h3),
.blog-content-body :deep(h4),
.blog-content-body :deep(h5),
.blog-content-body :deep(h6) {
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.blog-content-body :deep(p) {
  margin-bottom: 1.5rem;
}

.blog-content-body :deep(code) {
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.9em;
}

.blog-content-body :deep(pre) {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.blog-content-body :deep(blockquote) {
  border-left: 4px solid #007bff;
  padding-left: 1rem;
  margin-left: 0;
  color: #6c757d;
}

.author-card {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 0.375rem;
}

.author-avatar-large {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.author-placeholder-large {
  width: 60px;
  height: 60px;
  font-size: 3rem;
  color: #6c757d;
}

.blog-sidebar {
  position: sticky;
  top: 2rem;
}

.sidebar-section {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 0.375rem;
  margin-bottom: 1.5rem;
}

.sidebar-title {
  color: #495057;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #007bff;
}

.table-of-contents {
  max-height: 300px;
  overflow-y: auto;
}

.toc-item {
  display: block;
  padding: 0.25rem 0;
  color: #495057;
  text-decoration: none;
  font-size: 0.9rem;
  line-height: 1.4;
}

.toc-level-1 { padding-left: 0; }
.toc-level-2 { padding-left: 1rem; }
.toc-level-3 { padding-left: 2rem; }
.toc-level-4 { padding-left: 3rem; }
.toc-level-5 { padding-left: 4rem; }
.toc-level-6 { padding-left: 5rem; }

.toc-item:hover {
  color: #007bff;
  text-decoration: none;
}

.related-blog-item {
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #dee2e6;
}

.related-blog-item:last-child {
  border-bottom: none;
}

.related-blog-item h6 a {
  color: #495057;
  font-size: 0.9rem;
  line-height: 1.4;
}

.related-blog-item h6 a:hover {
  color: #007bff;
}

.share-buttons .btn {
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .blog-title {
    font-size: 2rem;
  }
  
  .blog-content-body {
    font-size: 1rem;
  }
  
  .blog-sidebar {
    margin-top: 2rem;
    position: static;
  }
  
  .author-card {
    margin-bottom: 1rem;
  }
}
</style>