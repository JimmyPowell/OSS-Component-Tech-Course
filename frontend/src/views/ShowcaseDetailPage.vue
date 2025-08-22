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
        <div class="showcase-info">
          <h1 class="showcase-title">{{ showcase.name }}</h1>
          <p class="showcase-description" v-if="showcase.summary">{{ showcase.summary }}</p>
          
          <div class="showcase-meta">
            <div class="author-info">
              <img src="/images/avatat.png" alt="作者头像" class="author-avatar">
              <div class="author-details">
                <span class="author-name">{{ showcase.author?.name || '匿名用户' }}</span>
                <span class="publish-date">{{ formatDate(showcase.created_at) }}</span>
              </div>
            </div>
            
            <div class="showcase-stats">
              <span class="stat-item">
                <i class="iconfont icon-eye"></i>
                {{ showcase.views_count || 0 }} 浏览
              </span>
              <span class="stat-item like-stat" @click="toggleLike">
                <i class="iconfont" :class="isLiked ? 'icon-thumbs-up-fill' : 'icon-thumbs-up'"></i>
                {{ likeCount }} 点赞
              </span>
            </div>
          </div>
        </div>

        <div class="showcase-image" v-if="showcase.avatar_url">
          <img :src="showcase.avatar_url" :alt="showcase.name" @error="handleImageError">
        </div>
      </div>

      <!-- Showcase Content -->
      <div class="showcase-content">
        <div class="content-section" v-if="showcase.detailed_introduction">
          <h3>作品介绍</h3>
          <div class="content-text" v-html="formatContent(showcase.detailed_introduction)"></div>
        </div>

        <!-- Project URL -->
        <div class="content-section" v-if="showcase.project_url">
          <h3>项目链接</h3>
          <a :href="showcase.project_url" target="_blank" rel="noopener noreferrer" class="project-link">
            <i class="iconfont icon-link"></i>
            {{ showcase.project_url }}
          </a>
        </div>

        <!-- Tags -->
        <div class="content-section" v-if="showcase.tags && showcase.tags.length">
          <h3>标签</h3>
          <div class="tags-container">
            <span v-for="tag in showcase.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>

      <!-- Comments Section -->
      <div class="comments-section">
        <div class="comments-header">
          <h3>评论 ({{ totalComments }})</h3>
          <button v-if="userStore.isAuthenticated" class="btn btn-primary" @click="showCommentForm = !showCommentForm">
            {{ showCommentForm ? '取消评论' : '发表评论' }}
          </button>
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
            <div v-for="comment in comments" :key="comment.uuid" class="comment-item">
              <div class="comment-header">
                <img src="/images/avatat.png" alt="用户头像" class="comment-avatar">
                <div class="comment-info">
                  <span class="comment-author">{{ comment.user?.name || '匿名用户' }}</span>
                  <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                </div>
                <div class="comment-actions">
                  <button class="like-btn" @click="toggleCommentLike(comment)">
                    <i class="iconfont" :class="comment.isLiked ? 'icon-thumbs-up-fill' : 'icon-thumbs-up'"></i>
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
                <div v-for="reply in comment.replies" :key="reply.uuid" class="reply-item">
                  <div class="reply-header">
                    <img src="/images/avatat.png" alt="用户头像" class="reply-avatar">
                    <div class="reply-info">
                      <span class="reply-author">{{ reply.user?.name || '匿名用户' }}</span>
                      <span class="reply-date">{{ formatDate(reply.created_at) }}</span>
                    </div>
                    <button class="like-btn" @click="toggleReplyLike(reply)">
                      <i class="iconfont" :class="reply.isLiked ? 'icon-thumbs-up-fill' : 'icon-thumbs-up'"></i>
                      {{ reply.likes_count || 0 }}
                    </button>
                  </div>
                  <div class="reply-content">{{ reply.content }}</div>
                </div>
              </div>
            </div>

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
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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
    
    if (!showcase.value || !showcase.value.id) {
      console.error('作品ID不存在，无法获取评论')
      return
    }
    
    const response = await showcaseAPI.getShowcaseComments(showcase.value.id, {
      skip: (page - 1) * commentsLimit.value,
      limit: commentsLimit.value
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
        const repliesResponse = await showcaseAPI.getCommentReplies(comment.id)
        let replies = []
        
        if (repliesResponse.data && repliesResponse.data.code === 200) {
          replies = repliesResponse.data.data.items || []
        } else if (repliesResponse.success) {
          replies = repliesResponse.data.items || []
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
        const repliesResponse = await showcaseAPI.getCommentReplies(comment.id)
        
        if (repliesResponse.data && repliesResponse.data.code === 200) {
          comment.replies = repliesResponse.data.data.items || []
        } else if (repliesResponse.success) {
          comment.replies = repliesResponse.data.items || []
        } else {
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
    
    if (response.success) {
      newComment.value = ''
      showCommentForm.value = false
      await fetchComments() // Refresh comments
    }
  } catch (err) {
    console.error('发布评论失败:', err)
  } finally {
    submittingComment.value = false
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
    
    if (response.success) {
      replyContent.value[comment.uuid] = ''
      activeReplyForm.value = null
      await fetchComments() // Refresh comments to show new reply
    }
  } catch (err) {
    console.error('发布回复失败:', err)
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
})
</script>

<style scoped>
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
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 14px;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-item:not(:last-child)::after {
  content: '/';
  margin: 0 8px;
  color: #6c757d;
}

.breadcrumb-link {
  color: #007bff;
  text-decoration: none;
  transition: color 0.3s;
}

.breadcrumb-link:hover {
  color: #0056b3;
}

.breadcrumb-item.active {
  color: #6c757d;
}

.showcase-header {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
  margin-bottom: 32px;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.showcase-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #333;
}

.showcase-description {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.showcase-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: #333;
}

.publish-date {
  font-size: 14px;
  color: #666;
}

.showcase-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 14px;
}

.like-stat {
  cursor: pointer;
  transition: color 0.3s;
}

.like-stat:hover {
  color: #007bff;
}

.showcase-image {
  display: flex;
  align-items: center;
  justify-content: center;
}

.showcase-image img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: cover;
}

.showcase-content {
  margin-bottom: 40px;
}

.content-section {
  margin-bottom: 24px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.content-section h3 {
  font-size: 20px;
  margin-bottom: 16px;
  color: #333;
  border-bottom: 2px solid #007bff;
  padding-bottom: 8px;
}

.content-text {
  line-height: 1.8;
  color: #555;
}

.project-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #007bff;
  text-decoration: none;
  padding: 8px 16px;
  border: 1px solid #007bff;
  border-radius: 4px;
  transition: all 0.3s;
}

.project-link:hover {
  background: #007bff;
  color: white;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: #f8f9fa;
  color: #495057;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  border: 1px solid #dee2e6;
}

.comments-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 24px;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.comment-form {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.comment-textarea {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 12px;
  resize: vertical;
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
  padding: 20px;
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
  border-bottom: 1px solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
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
  gap: 4px;
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.like-btn:hover {
  background: #f8f9fa;
  color: #007bff;
}

.comment-content {
  margin-left: 52px;
  line-height: 1.6;
  color: #555;
}

.comment-footer {
  margin-left: 52px;
  margin-top: 8px;
}

.reply-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 14px;
  padding: 4px 0;
}

.reply-btn:hover {
  text-decoration: underline;
}

.reply-form {
  margin-left: 52px;
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.reply-textarea {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 8px;
  resize: vertical;
}

.reply-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.replies-list {
  margin-left: 52px;
  margin-top: 16px;
  padding-left: 16px;
  border-left: 2px solid #f0f0f0;
}

.reply-item {
  padding: 12px 0;
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
  .showcase-header {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .showcase-meta {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .comments-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
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