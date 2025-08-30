<template>
  <div class="page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>正在加载作品详情...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-content">
        <i class="iconfont icon-warning error-icon"></i>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button class="btn btn-primary" @click="fetchShowcaseDetail">重试</button>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="showcase" class="container">
      <!-- Back Button -->
      <div class="back-nav">
        <button class="back-btn" @click="goBack">
          <i class="iconfont icon-arrow-left"></i>
          返回
        </button>
      </div>
      
      <!-- Breadcrumb Navigation -->
      <nav class="breadcrumb-nav" aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link to="/" class="breadcrumb-link">首页</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link to="/showcase" class="breadcrumb-link">作品展示</router-link>
          </li>
          <li class="breadcrumb-item active" aria-current="page">{{ showcase.name }}</li>
        </ol>
      </nav>

      <!-- Showcase Header -->
      <div class="showcase-header">
        <!-- Cover Image Section -->
        <div class="showcase-cover" v-if="showcase.avatar_url">
          <img :src="showcase.avatar_url" :alt="showcase.name" @error="handleImageError" class="cover-image">
        </div>
        
        <!-- Main Info Card -->
        <div class="showcase-main-info">
          <div class="title-section">
            <h1 class="showcase-title">{{ showcase.name }}</h1>
            <div class="title-stats">
              <span class="stat-badge views">
                <i class="iconfont icon-eye"></i>
                {{ showcase.views_count || 0 }}
              </span>
              <button class="stat-badge likes" :class="{ liked: isLiked }" @click="toggleLike">
                <i class="iconfont" :class="isLiked ? 'icon-dianzan' : 'icon-dzs'"></i>
                {{ likeCount }}
              </button>
              <a v-if="showcase.project_url" :href="showcase.project_url" target="_blank" rel="noopener noreferrer" class="stat-badge project-link">
                <i class="iconfont icon-link"></i>
                项目链接
              </a>
            </div>
          </div>
          
          <p class="showcase-summary" v-if="showcase.summary">{{ showcase.summary }}</p>
          
          <!-- Tags -->
          <div v-if="showcase.tags && showcase.tags.length" class="tags-section">
            <div class="tags-container">
              <span v-for="tag in showcase.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
          
          <!-- Author Info Card -->
          <div class="author-card">
            <img src="/images/avatat.png" alt="作者头像" class="author-avatar">
            <div class="author-details">
              <div class="author-name">{{ showcase.author?.username || showcase.author?.real_name || '匿名用户' }}</div>
              <div class="author-meta">
                <span class="publish-time">发布于 {{ formatDate(showcase.created_at) }}</span>
                <span class="author-role" v-if="showcase.author?.role">{{ showcase.author.role === 'manager' ? '管理员' : '学生' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Showcase Content -->
      <div class="showcase-content">
        <div class="content-section" v-if="showcase.detailed_introduction">
          <h3>作品介绍</h3>
          <div class="content-text" v-html="formatContent(showcase.detailed_introduction)"></div>
        </div>

      </div>

      <!-- Comments Section -->
      <div class="comments-section">
        <div class="comments-header">
          <h3>评论 ({{ totalComments }})</h3>
          <div class="comments-controls">
            <div class="sort-dropdown" ref="sortDropdown" :class="{ open: showDropdown }">
              <div 
                class="custom-select"
                @click="toggleDropdown"
                :class="{ active: showDropdown }"
                :title="`当前排序: ${getSortText(sortConfig)}`"
              >
                <span class="selected-text">{{ getSortText(sortConfig) }}</span>
                <i class="iconfont icon-down dropdown-icon" :class="{ rotated: showDropdown }"></i>
              </div>
              <div class="dropdown-menu" v-if="showDropdown">
                <div 
                  class="dropdown-item"
                  :class="{ active: sortConfig === 'created_at_desc' }"
                  @click="selectSort('created_at_desc')"
                >
                  <i class="iconfont icon-time"></i>
                  <span>最新评论</span>
                </div>
                <div 
                  class="dropdown-item"
                  :class="{ active: sortConfig === 'created_at_asc' }"
                  @click="selectSort('created_at_asc')"
                >
                  <i class="iconfont icon-time"></i>
                  <span>最早评论</span>
                </div>
                <div 
                  class="dropdown-item"
                  :class="{ active: sortConfig === 'likes_count_desc' }"
                  @click="selectSort('likes_count_desc')"
                >
                  <i class="iconfont icon-dianzan"></i>
                  <span>点赞最多</span>
                </div>
                <div 
                  class="dropdown-item"
                  :class="{ active: sortConfig === 'likes_count_asc' }"
                  @click="selectSort('likes_count_asc')"
                >
                  <i class="iconfont icon-dzs"></i>
                  <span>点赞最少</span>
                </div>
              </div>
            </div>
            <button v-if="userStore.isAuthenticated" class="btn btn-primary" @click="showCommentForm = !showCommentForm">
              {{ showCommentForm ? '取消评论' : '发表评论' }}
            </button>
          </div>
        </div>

        <!-- Comment Form -->
        <div v-if="showCommentForm && userStore.isAuthenticated" class="comment-form">
          <textarea 
            v-model="newComment"
            class="form-control comment-textarea"
            placeholder="写下你的评论..."
            rows="4"
          ></textarea>
          <div class="comment-actions">
            <button class="btn btn-secondary" @click="showCommentForm = false">取消</button>
            <button 
              class="btn btn-primary" 
              @click="submitComment"
              :disabled="!newComment.trim() || submittingComment"
            >
              {{ submittingComment ? '发布中...' : '发布评论' }}
            </button>
          </div>
        </div>

        <!-- Comments List -->
        <div class="comments-list">
          <div v-if="loadingComments" class="loading-comments">
            <div class="spinner-sm"></div>
            <span>正在加载评论...</span>
          </div>
          
          <div v-else-if="comments.length === 0" class="no-comments">
            <i class="iconfont icon-message"></i>
            <p>暂无评论，快来发表第一条评论吧！</p>
          </div>
          
          <div v-else>
            <transition-group name="comment-item" tag="div">
              <div v-for="comment in comments" :key="comment.uuid" class="comment-item" :class="{ 'new-comment': comment.isNew }">
              <div class="comment-header">
                <img src="/images/avatat.png" alt="用户头像" class="comment-avatar">
                <div class="comment-info">
                  <span class="comment-author">{{ comment.user?.username || comment.user?.real_name || '匿名用户' }}</span>
                  <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                </div>
                <div class="comment-actions">
                  <button class="like-btn" @click="toggleCommentLike(comment)">
                    <i class="iconfont" :class="comment.isLiked ? 'icon-dianzan' : 'icon-dzs'"></i>
                    {{ comment.likes_count || 0 }}
                  </button>
                </div>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
              
              <!-- Reply Button -->
              <div class="comment-footer">
                <button 
                  v-if="userStore.isAuthenticated" 
                  class="reply-btn"
                  @click="toggleReplyForm(comment.uuid)"
                >
                  回复
                </button>
              </div>

              <!-- Reply Form -->
              <div v-if="activeReplyForm === comment.uuid" class="reply-form">
                <textarea 
                  v-model="replyContent[comment.uuid]"
                  class="form-control reply-textarea"
                  placeholder="回复评论..."
                  rows="2"
                ></textarea>
                <div class="reply-actions">
                  <button class="btn btn-secondary btn-sm" @click="activeReplyForm = null">取消</button>
                  <button 
                    class="btn btn-primary btn-sm" 
                    @click="submitReply(comment)"
                    :disabled="!replyContent[comment.uuid]?.trim()"
                  >
                    发布回复
                  </button>
                </div>
              </div>

              <!-- Replies -->
              <div v-if="comment.replies && comment.replies.length" class="replies-list">
                <transition-group name="reply-item" tag="div">
                  <div v-for="reply in comment.replies" :key="reply.uuid" class="reply-item" :class="{ 'new-reply': reply.isNew }">
                  <div class="reply-header">
                    <img src="/images/avatat.png" alt="用户头像" class="reply-avatar">
                    <div class="reply-info">
                      <span class="reply-author">{{ reply.user?.username || reply.user?.real_name || '匿名用户' }}</span>
                      <span class="reply-date">{{ formatDate(reply.created_at) }}</span>
                    </div>
                    <button class="like-btn" @click="toggleReplyLike(reply)">
                      <i class="iconfont" :class="reply.isLiked ? 'icon-dianzan' : 'icon-dzs'"></i>
                      {{ reply.likes_count || 0 }}
                    </button>
                  </div>
                    <div class="reply-content">{{ reply.content }}</div>
                  </div>
                </transition-group>
              </div>
            </div>
            </transition-group>

            <!-- Load More Comments -->
            <div v-if="hasMoreComments" class="load-more-container">
              <button class="btn btn-outline-primary" @click="loadMoreComments" :disabled="loadingComments">
                {{ loadingComments ? '加载中...' : '查看更多评论' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { showcaseAPI } from '@/api/showcase'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const userStore = useAuthStore()

// Showcase data
const showcase = ref(null)
const loading = ref(true)
const error = ref('')
const isLiked = ref(false)
const likeCount = ref(0)

// Comments data
const comments = ref([])
const totalComments = ref(0)
const loadingComments = ref(false)
const hasMoreComments = ref(false)
const commentsPage = ref(1)
const commentsLimit = ref(10)
// 从localStorage恢复用户的排序偏好，默认为最新评论在前
const sortConfig = ref(localStorage.getItem('showcase_comment_sort') || 'created_at_desc')
const showDropdown = ref(false)
const sortDropdown = ref(null)

// Comment form
const showCommentForm = ref(false)
const newComment = ref('')
const submittingComment = ref(false)

// Reply form
const activeReplyForm = ref(null)
const replyContent = ref({})

// Methods
const fetchShowcaseDetail = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await showcaseAPI.getShowcaseByUuid(route.params.uuid)
    console.log('作品详情API响应:', response)
    
    if (response.data && response.data.code === 200) {
      showcase.value = response.data.data
      likeCount.value = response.data.data.likes_count || 0
      
      // Fetch like status if user is logged in
      if (userStore.isAuthenticated) {
        await fetchLikeStatus()
      }
      
      // Fetch comments
      await fetchComments()
    } else if (response.success) {
      // 兼容旧格式
      showcase.value = response.data
      likeCount.value = response.data.likes_count || 0
      
      if (userStore.isAuthenticated) {
        await fetchLikeStatus()
      }
      
      await fetchComments()
    } else {
      error.value = response.message || '获取作品详情失败'
    }
  } catch (err) {
    error.value = '网络错误，请稍后重试'
    console.error('获取作品详情失败:', err)
  } finally {
    loading.value = false
  }
}

const fetchLikeStatus = async () => {
  try {
    const response = await showcaseAPI.getShowcaseLikeStatus(route.params.uuid)
    console.log('点赞状态API响应:', response)
    
    if (response.data && response.data.code === 200) {
      isLiked.value = response.data.data.liked
    } else if (response.success) {
      isLiked.value = response.data.liked
    }
  } catch (err) {
    console.error('获取点赞状态失败:', err)
  }
}

const fetchComments = async (page = 1, append = false) => {
  try {
    loadingComments.value = true
    
    // 后端评论API需要数字ID，不是UUID
    if (!showcase.value || !showcase.value.id) {
      console.error('作品ID不存在，无法获取评论', showcase.value)
      return
    }
    
    const parts = sortConfig.value.split('_')
    const sortBy = parts.slice(0, -1).join('_') // 除了最后一个元素，其余用_连接
    const sortOrder = parts[parts.length - 1] // 最后一个元素是排序方向
    const response = await showcaseAPI.getShowcaseComments(showcase.value.id, {
      skip: (page - 1) * commentsLimit.value,
      limit: commentsLimit.value,
      sort_by: sortBy,
      sort_order: sortOrder
    })
    
    console.log('评论API响应:', response)
    let newComments = []
    
    if (response.data && response.data.code === 200) {
      newComments = response.data.data.items || []
    } else if (response.success) {
      newComments = response.data.items || []
    }
      
    // Fetch like status for each comment and load replies
    if (userStore.isAuthenticated) {
      await Promise.all(newComments.map(async (comment) => {
        const likeResponse = await showcaseAPI.getCommentLikeStatus(comment.uuid)
        if (likeResponse.data && likeResponse.data.code === 200) {
          comment.isLiked = likeResponse.data.data.liked
        } else if (likeResponse.success) {
          comment.isLiked = likeResponse.data.liked
        }
        
        // Load replies for each comment
        let replies = []
        try {
          if (comment.id) {
            const repliesResponse = await showcaseAPI.getCommentReplies(comment.id)
            
            if (repliesResponse.data && repliesResponse.data.code === 200) {
              replies = repliesResponse.data.data.items || []
            } else if (repliesResponse.success) {
              replies = repliesResponse.data.items || []
            }
          }
        } catch (err) {
          console.error('获取评论回复失败:', err)
          replies = []
        }
        
        comment.replies = replies
        
        // Fetch like status for replies
        await Promise.all(comment.replies.map(async (reply) => {
          const replyLikeResponse = await showcaseAPI.getReplyLikeStatus(reply.uuid)
          if (replyLikeResponse.data && replyLikeResponse.data.code === 200) {
            reply.isLiked = replyLikeResponse.data.data.liked
          } else if (replyLikeResponse.success) {
            reply.isLiked = replyLikeResponse.data.liked
          }
        }))
      }))
    } else {
      // Load replies without like status
      await Promise.all(newComments.map(async (comment) => {
        try {
          if (comment.id) {
            const repliesResponse = await showcaseAPI.getCommentReplies(comment.id)
            
            if (repliesResponse.data && repliesResponse.data.code === 200) {
              comment.replies = repliesResponse.data.data.items || []
            } else if (repliesResponse.success) {
              comment.replies = repliesResponse.data.items || []
            } else {
              comment.replies = []
            }
          } else {
            comment.replies = []
          }
        } catch (err) {
          console.error('获取评论回复失败:', err)
          comment.replies = []
        }
      }))
    }
      
    if (append) {
      comments.value.push(...newComments)
    } else {
      comments.value = newComments
    }
    
    let total = 0
    if (response.data && response.data.code === 200) {
      total = response.data.data.total || 0
    } else if (response.success) {
      total = response.data.total || 0
    }
    
    totalComments.value = total
    hasMoreComments.value = (page * commentsLimit.value) < total
    commentsPage.value = page
  } catch (err) {
    console.error('获取评论失败:', err)
  } finally {
    loadingComments.value = false
  }
}

const toggleLike = async () => {
  if (!userStore.isAuthenticated) {
    userStore.showLoginModal()
    return
  }
  
  try {
    const response = await showcaseAPI.toggleShowcaseLike({
      showcase_uuid: route.params.uuid
    })
    
    console.log('点赞API响应:', response)
    let liked = false
    
    if (response.data && response.data.code === 200) {
      liked = response.data.data.liked
    } else if (response.success) {
      liked = response.data.liked
    }
    
    isLiked.value = liked
    likeCount.value += liked ? 1 : -1
  } catch (err) {
    console.error('点赞操作失败:', err)
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    submittingComment.value = true
    
    const response = await showcaseAPI.createShowcaseComment({
      showcase_uuid: route.params.uuid,
      content: newComment.value.trim()
    })
    
    console.log('评论提交响应:', response)
    
    if (response.data && response.data.code === 200) {
      message.success('评论发表成功！')
      
      // 创建新评论对象并添加到评论列表顶部，避免重新获取所有评论
      const newCommentObj = {
        uuid: Date.now().toString(), // 临时ID
        content: newComment.value.trim(),
        user: {
          username: userStore.user?.username || '当前用户',
          real_name: userStore.user?.real_name || '当前用户'
        },
        created_at: new Date().toISOString(),
        likes_count: 0,
        isLiked: false,
        replies: [],
        isNew: true // 标记为新评论
      }
      
      // 将新评论添加到列表顶部
      comments.value.unshift(newCommentObj)
      totalComments.value += 1
      
      // 3秒后移除新评论的高亮状态
      setTimeout(() => {
        newCommentObj.isNew = false
      }, 3000)
      
      // 清理表单
      newComment.value = ''
      showCommentForm.value = false
    } else if (response.success) {
      // 兼容旧格式
      message.success('评论发表成功！')
      
      // 同样的优化逻辑
      const newCommentObj = {
        uuid: Date.now().toString(),
        content: newComment.value.trim(),
        user: {
          username: userStore.user?.username || '当前用户',
          real_name: userStore.user?.real_name || '当前用户'
        },
        created_at: new Date().toISOString(),
        likes_count: 0,
        isLiked: false,
        replies: [],
        isNew: true // 标记为新评论
      }
      
      comments.value.unshift(newCommentObj)
      totalComments.value += 1
      
      // 3秒后移除新评论的高亮状态
      setTimeout(() => {
        newCommentObj.isNew = false
      }, 3000)
      
      newComment.value = ''
      showCommentForm.value = false
    }
  } catch (err) {
    console.error('发布评论失败:', err)
    message.error('发布评论失败，请稍后重试')
  } finally {
    submittingComment.value = false
  }
}

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
  console.log('Toggle dropdown:', showDropdown.value)
}

const selectSort = async (value) => {
  if (value !== sortConfig.value) {
    sortConfig.value = value
    // 保存用户的排序偏好到localStorage
    localStorage.setItem('showcase_comment_sort', value)
    showDropdown.value = false
    commentsPage.value = 1
    comments.value = []
    await fetchComments()
  } else {
    showDropdown.value = false
  }
}

const getSortText = (value) => {
  const sortTexts = {
    'created_at_desc': '最新评论',
    'created_at_asc': '最早评论',
    'likes_count_desc': '点赞最多',
    'likes_count_asc': '点赞最少'
  }
  return sortTexts[value] || '最新评论'
}

const handleClickOutside = (event) => {
  if (sortDropdown.value && !sortDropdown.value.contains(event.target)) {
    showDropdown.value = false
  }
}

const toggleCommentLike = async (comment) => {
  if (!userStore.isAuthenticated) {
    userStore.showLoginModal()
    return
  }
  
  try {
    const response = await showcaseAPI.toggleCommentLike({
      comment_uuid: comment.uuid
    })
    
    let liked = false
    
    if (response.data && response.data.code === 200) {
      liked = response.data.data.liked
    } else if (response.success) {
      liked = response.data.liked
    }
    
    comment.isLiked = liked
    comment.likes_count = (comment.likes_count || 0) + (liked ? 1 : -1)
  } catch (err) {
    console.error('点赞评论失败:', err)
  }
}

const toggleReplyForm = (commentUuid) => {
  activeReplyForm.value = activeReplyForm.value === commentUuid ? null : commentUuid
  if (activeReplyForm.value && !replyContent.value[commentUuid]) {
    replyContent.value[commentUuid] = ''
  }
}

const submitReply = async (comment) => {
  const content = replyContent.value[comment.uuid]?.trim()
  if (!content) return
  
  try {
    const response = await showcaseAPI.createCommentReply({
      comment_uuid: comment.uuid,
      content: content
    })
    
    console.log('回复提交响应:', response)
    
    // 支持两种API响应格式
    if ((response.data && response.data.code === 200) || response.success) {
      message.success('回复发表成功！')
      
      // 创建新回复对象并直接添加到评论的回复列表中
      const newReply = {
        uuid: Date.now().toString(), // 临时ID
        content: content,
        user: {
          username: userStore.user?.username || '当前用户',
          real_name: userStore.user?.real_name || '当前用户'
        },
        created_at: new Date().toISOString(),
        likes_count: 0,
        isLiked: false,
        isNew: true // 标记为新回复
      }
      
      // 确保评论有replies数组
      if (!comment.replies) {
        comment.replies = []
      }
      
      // 将新回复添加到评论的回复列表末尾（按时间顺序）
      comment.replies.push(newReply)
      
      // 3秒后移除新回复的高亮状态
      setTimeout(() => {
        newReply.isNew = false
      }, 3000)
      
      // 清理表单
      replyContent.value[comment.uuid] = ''
      activeReplyForm.value = null
    } else {
      console.error('回复提交失败 - API响应格式错误:', response)
      message.error('回复发布失败，请稍后重试')
    }
  } catch (err) {
    console.error('发布回复失败:', err)
    message.error('发布回复失败，请稍后重试')
  }
}

const toggleReplyLike = async (reply) => {
  if (!userStore.isAuthenticated) {
    userStore.showLoginModal()
    return
  }
  
  try {
    const response = await showcaseAPI.toggleReplyLike({
      reply_uuid: reply.uuid
    })
    
    let liked = false
    
    if (response.data && response.data.code === 200) {
      liked = response.data.data.liked
    } else if (response.success) {
      liked = response.data.liked
    }
    
    reply.isLiked = liked
    reply.likes_count = (reply.likes_count || 0) + (liked ? 1 : -1)
  } catch (err) {
    console.error('点赞回复失败:', err)
  }
}

const loadMoreComments = () => {
  fetchComments(commentsPage.value + 1, true)
}

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/showcase')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString('zh-CN')
}

const formatContent = (content) => {
  return content.replace(/\n/g, '<br>')
}

const handleImageError = (event) => {
  event.target.src = `/images/show${Math.floor(Math.random() * 3) + 1}.png`
}

// Lifecycle
onMounted(() => {
  fetchShowcaseDetail()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  padding: 32px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 返回按钮样式 */
.back-nav {
  margin-bottom: 16px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  color: #2d3748;
  transform: translateX(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #cbd5e0;
}

.back-btn i {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.back-btn:hover i {
  transform: translateX(-2px);
}
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 16px;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.error-content {
  text-align: center;
  max-width: 400px;
}

.error-icon {
  font-size: 48px;
  color: #dc3545;
  margin-bottom: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-sm {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.breadcrumb-nav {
  margin-bottom: 24px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  list-style: none;
  padding: 12px 20px;
  margin: 0;
  font-size: 14px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border: 1px solid #f0f0f0;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-item:not(:last-child)::after {
  content: '>';
  margin: 0 10px;
  color: #d1d5db;
  font-weight: 500;
  font-size: 12px;
}

.breadcrumb-link {
  color: #6366f1;
  text-decoration: none;
  transition: all 0.2s ease;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.breadcrumb-link:hover {
  color: #4f46e5;
  background: #f8fafc;
}

.breadcrumb-item.active {
  color: #374151;
  font-weight: 600;
  padding: 4px 8px;
}

.showcase-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 40px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  overflow: hidden;
}

.showcase-cover {
  width: 100%;
  height: 280px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.cover-image:hover {
  transform: scale(1.05);
}

.showcase-main-info {
  padding: 32px;
}

.title-section {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 20px;
}

.showcase-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
  margin: 0;
  flex: 1;
}

.title-stats {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.stat-badge.views {
  background: #f0f4f8;
  color: #4a5568;
}

.stat-badge.likes {
  background: #fef5e7;
  color: #d69e2e;
  border: 1px solid #f6e05e;
}

.stat-badge.likes.liked {
  background: #fed7d7;
  color: #e53e3e;
  border: 1px solid #feb2b2;
}

.stat-badge.likes:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(214, 158, 46, 0.3);
}

.stat-badge.likes.liked:hover {
  box-shadow: 0 4px 12px rgba(229, 62, 62, 0.3);
}

.stat-badge.project-link {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  text-decoration: none;
  border: 1px solid #4299e1;
}

.stat-badge.project-link:hover {
  background: linear-gradient(135deg, #3182ce, #2c5aa0);
  color: white;
  text-decoration: none;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.4);
}

.showcase-summary {
  font-size: 18px;
  color: #4a5568;
  line-height: 1.6;
  margin-bottom: 28px;
  padding: 20px;
  background: #f7fafc;
  border-radius: 12px;
  border-left: 4px solid #4299e1;
}

.author-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  position: relative;
}

.author-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.author-details {
  flex: 1;
}

.author-name {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
}

.author-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.publish-time {
  font-size: 14px;
  color: #718096;
  display: flex;
  align-items: center;
  gap: 4px;
}

.author-role {
  padding: 4px 12px;
  background: #4299e1;
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tags-section {
  margin-bottom: 28px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tag {
  background: linear-gradient(135deg, #f7fafc, #edf2f7);
  color: #4a5568;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  cursor: pointer;
}

.tag:hover {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
}


.showcase-content {
  margin-bottom: 40px;
}

.content-section {
  margin-bottom: 32px;
  padding: 32px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  border: 1px solid #f0f4f8;
  transition: all 0.3s ease;
}

.content-section:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.content-section h3 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #2d3748;
  position: relative;
  font-weight: 700;
  padding-left: 20px;
}

.content-section h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  border-radius: 2px;
}

.content-text {
  line-height: 1.8;
  color: #4a5568;
  font-size: 16px;
  margin-bottom: 0;
}


.comments-section {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  padding: 32px;
  margin-bottom: 40px;
  border: 1px solid #f0f4f8;
  min-height: 200px; /* 确保评论区有最小高度，避免页面跳动 */
}

.comments-section h3 {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.comments-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sort-dropdown {
  position: relative;
}

.custom-select {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 120px;
  padding: 10px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 40px;
  background-color: #fff;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.custom-select:hover {
  border-color: #545ae7;
  box-shadow: 0 2px 8px rgba(84, 90, 231, 0.15);
}

.custom-select.active {
  border-color: #545ae7;
  box-shadow: 0 0 0 3px rgba(84, 90, 231, 0.1);
}

.selected-text {
  font-weight: 500;
  color: #333;
}

.dropdown-icon {
  margin-left: 8px;
  font-size: 12px;
  color: #666;
  transition: transform 0.3s ease;
}

.dropdown-icon.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  z-index: 1000;
  overflow: hidden;
  border: 1px solid #e1e5e9;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #333;
  border-bottom: 1px solid #f5f5f5;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: #f8f9ff;
  color: #545ae7;
}

.dropdown-item.active {
  background-color: #545ae7;
  color: white;
}

.dropdown-item.active:hover {
  background-color: #4147d1;
}

.dropdown-item i {
  margin-right: 8px;
  font-size: 14px;
  width: 16px;
  text-align: center;
}

.dropdown-item span {
  font-weight: 500;
}

.comment-form {
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #f7fafc, #edf2f7);
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.comment-textarea {
  width: 100%;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  resize: vertical;
  font-size: 16px;
  line-height: 1.5;
  transition: border-color 0.3s ease;
}

.comment-textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.comment-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.loading-comments {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  padding: 40px 20px;
  min-height: 120px; /* 防止页面高度跳动 */
}

.no-comments {
  text-align: center;
  padding: 40px;
  color: #666;
}

.no-comments .iconfont {
  font-size: 48px;
  color: #ddd;
  margin-bottom: 12px;
}

.comment-item {
  padding: 20px 0;
  border-bottom: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  opacity: 1;
  transform: translateY(0);
}

.comment-item:hover {
  background: #f8fafc;
  border-radius: 12px;
  margin: 0 -16px;
  padding: 20px 16px;
}

/* 新评论的进入动画 */
.comment-item-enter-active {
  transition: all 0.6s ease;
}

.comment-item-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.comment-item-enter-to {
  opacity: 1;
  transform: translateY(0);
}

/* 新回复的进入动画 */
.reply-item-enter-active {
  transition: all 0.5s ease;
}

.reply-item-enter-from {
  opacity: 0;
  transform: translateX(-10px) scale(0.95);
}

.reply-item-enter-to {
  opacity: 1;
  transform: translateX(0) scale(1);
}

/* 新添加的评论高亮效果 */
.comment-item.new-comment {
  background: linear-gradient(135deg, #e6fffa, #f0fff4);
  border-left: 3px solid #38b2ac;
  animation: highlightFade 3s ease-out forwards;
}

@keyframes highlightFade {
  0% {
    background: linear-gradient(135deg, #e6fffa, #f0fff4);
    border-left-color: #38b2ac;
  }
  100% {
    background: transparent;
    border-left-color: transparent;
  }
}

/* 新添加的回复高亮效果 */
.reply-item.new-reply {
  background: linear-gradient(135deg, #e6fffa, #f0fff4);
  border-left: 3px solid #38b2ac;
  border-radius: 8px;
  animation: highlightFadeReply 3s ease-out forwards;
  margin: 0 -8px;
  padding: 8px;
}

@keyframes highlightFadeReply {
  0% {
    background: linear-gradient(135deg, #e6fffa, #f0fff4);
    border-left-color: #38b2ac;
  }
  100% {
    background: transparent;
    border-left-color: transparent;
  }
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 12px;
}

.comment-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.comment-author {
  font-weight: 600;
  color: #333;
}

.comment-date {
  font-size: 12px;
  color: #999;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.like-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #f7fafc, #edf2f7);
  border: 1px solid #e2e8f0;
  color: #718096;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  min-width: 60px;
  justify-content: center;
}

.like-btn:hover {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
  border-color: #4299e1;
}

/* Custom button styles override */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-transform: none;
  letter-spacing: 0.3px;
  text-decoration: none;
}

.btn:hover {
  transform: translateY(-1px);
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #4299e1, #3182ce) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
  border: none !important;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #3182ce, #2c5aa0) !important;
  color: white !important;
  box-shadow: 0 6px 16px rgba(66, 153, 225, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #718096, #4a5568) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(113, 128, 150, 0.3);
  border: none !important;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #4a5568, #2d3748) !important;
  color: white !important;
  box-shadow: 0 6px 16px rgba(113, 128, 150, 0.4);
}

.btn-outline-primary {
  background: transparent !important;
  color: #4299e1 !important;
  border: 2px solid #4299e1 !important;
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.15);
}

.btn-outline-primary:hover {
  background: linear-gradient(135deg, #4299e1, #3182ce) !important;
  color: white !important;
  box-shadow: 0 6px 16px rgba(66, 153, 225, 0.4);
}

.btn-sm {
  padding: 8px 16px !important;
  font-size: 13px !important;
  border-radius: 8px !important;
}

.comment-content {
  margin-left: 52px;
  line-height: 1.6;
  color: #555;
}

.comment-footer {
  margin-left: 52px;
  margin-top: 6px;
}

.reply-btn {
  background: linear-gradient(135deg, #ebf8ff, #e6fffa);
  border: 1px solid #4299e1;
  color: #4299e1;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.reply-btn:hover {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3);
  text-decoration: none;
}

.reply-form {
  margin-left: 52px;
  margin-top: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f7fafc, #edf2f7);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.reply-textarea {
  width: 100%;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  resize: vertical;
  font-size: 14px;
  line-height: 1.4;
  transition: border-color 0.3s ease;
}

.reply-textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.reply-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.replies-list {
  margin-left: 52px;
  margin-top: 12px;
  padding-left: 16px;
  border-left: 2px solid #f0f0f0;
}

.reply-item {
  padding: 8px 0;
  border-bottom: 1px solid #f8f8f8;
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.reply-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 8px;
}

.reply-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.reply-author {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.reply-date {
  font-size: 12px;
  color: #999;
}

.reply-content {
  margin-left: 40px;
  color: #555;
  font-size: 14px;
  line-height: 1.5;
}

.load-more-container {
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 768px) {
  .showcase-main-info {
    padding: 24px 20px;
  }
  
  .title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .showcase-title {
    font-size: 24px;
  }
  
  .title-stats {
    width: 100%;
    justify-content: flex-start;
  }
  
  .showcase-summary {
    font-size: 16px;
    padding: 16px;
  }
  
  .author-card {
    padding: 20px 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .author-meta {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .quick-actions {
    margin-left: 0;
    width: 100%;
  }
  
  .project-link-btn {
    width: 100%;
    justify-content: center;
  }
  
  .link-preview {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .visit-btn {
    align-self: flex-start;
  }
  
  .comments-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .comments-controls {
    width: 100%;
    flex-direction: column;
    gap: 12px;
  }
  
  .custom-select {
    width: 100%;
    min-width: auto;
  }
  
  .comment-content,
  .comment-footer,
  .reply-form,
  .replies-list {
    margin-left: 20px;
  }
  
  .reply-content {
    margin-left: 20px;
  }
}
</style>