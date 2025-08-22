<template>
  <div class="post-detail-page">
    <div class="container">
      <div v-if="loading" class="loading-state">
        <p>加载中...</p>
      </div>

      <div v-else-if="post" class="post-detail">
        <!-- 返回按钮 -->
        <div class="back-nav">
          <button @click="goBack" class="btn-back">
            <i class="icon">←</i>
            返回论坛
          </button>
        </div>

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

        <!-- 帖子标题 -->
        <h1 class="post-title">{{ post.title }}</h1>

        <!-- 帖子元信息 -->
        <div class="post-meta">
          <div class="post-author" v-if="post.author">
            <img 
              :src="post.author.avatar_url || '/images/head.png'" 
              alt="头像"
              class="author-avatar"
            >
            <div class="author-info">
              <span class="author-name">
                {{ post.author.real_name || post.author.username }}
              </span>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>
          </div>
          <div class="post-stats">
            <span class="stat">👀 {{ post.view_count }}</span>
            <span class="stat">💬 {{ post.reply_count }}</span>
          </div>
        </div>

        <!-- 帖子内容 -->
        <div class="post-content">
          <div class="content-body" v-html="formatContent(post.content)"></div>
        </div>

        <!-- 回复区域 -->
        <div class="replies-section">
          <div class="section-header">
            <h3 class="section-title">
              回复 ({{ replies.length }})
            </h3>
            <button 
              v-if="!post.is_locked"
              @click="showReplyForm = !showReplyForm"
              class="btn-reply"
            >
              <i class="icon">💬</i>
              {{ showReplyForm ? '取消回复' : '回复讨论' }}
            </button>
          </div>

          <!-- 回复表单 -->
          <div v-if="showReplyForm && !post.is_locked" class="reply-form">
            <form @submit.prevent="submitReply">
              <textarea 
                v-model="replyContent"
                placeholder="写下你的回复..."
                class="reply-textarea"
                rows="4"
                required
              ></textarea>
              <div class="reply-actions">
                <button type="button" @click="showReplyForm = false" class="btn-cancel">
                  取消
                </button>
                <button type="submit" :disabled="submittingReply" class="btn-submit">
                  {{ submittingReply ? '发布中...' : '发布回复' }}
                </button>
              </div>
            </form>
          </div>

          <!-- 回复列表 -->
          <div class="replies-list">
            <div 
              v-for="reply in replies" 
              :key="reply.uuid"
              class="reply-item"
            >
              <div class="reply-author" v-if="reply.author">
                <img 
                  :src="reply.author.avatar_url || '/images/head.png'" 
                  alt="头像"
                  class="author-avatar"
                >
              </div>
              <div class="reply-content">
                <div class="reply-header">
                  <span class="author-name" v-if="reply.author">
                    {{ reply.author.real_name || reply.author.username }}
                  </span>
                  <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
                  <span v-if="reply.floor_number" class="floor-number">
                    #{{ reply.floor_number }}
                  </span>
                </div>
                <div class="reply-body" v-html="formatContent(reply.content)"></div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="replies.length === 0" class="empty-replies">
            <div class="empty-icon">💭</div>
            <p>暂无回复，成为第一个回复的人吧！</p>
          </div>
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else class="error-state">
        <div class="error-icon">❌</div>
        <h3>帖子不存在或已被删除</h3>
        <button @click="goBack" class="btn-go-back">
          返回论坛
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { forumApi } from '../api/forum'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 响应式数据
const post = ref(null)
const replies = ref([])
const loading = ref(false)
const showReplyForm = ref(false)
const replyContent = ref('')
const submittingReply = ref(false)

// 返回上一页
const goBack = () => {
  router.go(-1)
}

// 获取帖子详情
const fetchPost = async () => {
  loading.value = true
  try {
    const response = await forumApi.post.getPost(route.params.uuid)
    post.value = response.data.data
  } catch (error) {
    console.error('获取帖子失败:', error)
    post.value = null
  } finally {
    loading.value = false
  }
}

// 获取回复列表
const fetchReplies = async () => {
  if (!post.value) return
  
  try {
    const response = await forumApi.reply.getRepliesByPost(post.value.uuid, { limit: 100 })
    replies.value = response.data.data.items || []
  } catch (error) {
    console.error('获取回复失败:', error)
    replies.value = []
  }
}

// 提交回复
const submitReply = async () => {
  if (!authStore.isAuthenticated) {
    alert('请先登录后再回复')
    authStore.showLoginModal()
    return
  }
  
  if (!replyContent.value.trim()) {
    alert('请输入回复内容')
    return
  }
  
  submittingReply.value = true
  
  try {
    const replyData = {
      post_id: post.value.id,
      content: replyContent.value.trim()
    }
    
    await forumApi.reply.createReply(replyData)
    
    // 成功后重置表单并刷新回复列表
    replyContent.value = ''
    showReplyForm.value = false
    await fetchReplies()
    
    // 更新帖子回复数
    if (post.value) {
      post.value.reply_count = (post.value.reply_count || 0) + 1
    }
    
    alert('回复成功！')
  } catch (error) {
    console.error('回复失败:', error)
    
    if (error.response?.status === 401) {
      alert('登录已过期，请重新登录')
      authStore.showLoginModal()
    } else {
      alert('回复失败，请稍后重试')
    }
  } finally {
    submittingReply.value = false
  }
}

// 格式化内容（简单的Markdown解析）
const formatContent = (content) => {
  if (!content) return ''
  
  return content
    // 代码块
    .replace(/```(\w+)?\n([\s\S]*?)\n```/g, '<pre class="code-block"><code>$2</code></pre>')
    // 行内代码
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    // 粗体
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 斜体
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // 引用
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // 列表
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // 换行
    .replace(/\n/g, '<br>')
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
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

// 页面加载
onMounted(async () => {
  await fetchPost()
  if (post.value) {
    await fetchReplies()
  }
})
</script>

<style scoped>
.post-detail-page {
  min-height: 100vh;
  background: #f6f7f9;
  padding: 2rem 0;
}

.loading-state, .error-state {
  text-align: center;
  padding: 4rem 1rem;
  color: #72767d;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  color: #2c2f33;
  margin-bottom: 1.5rem;
}

.btn-go-back, .btn-back {
  background: linear-gradient(135deg, #5865f2, #7289da);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-go-back:hover, .btn-back:hover {
  background: linear-gradient(135deg, #4752c4, #677bc4);
  transform: translateY(-1px);
}

.back-nav {
  margin-bottom: 1.5rem;
}

.post-detail {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem 0;
}

.category-tag {
  background: #f2f3f5;
  color: #4f545c;
  padding: 0.375rem 0.75rem;
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 600;
}

.post-badges {
  display: flex;
  gap: 0.5rem;
}

.badge {
  font-size: 0.8125rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
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

.post-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c2f33;
  line-height: 1.3;
  margin: 1rem 2rem;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  margin-bottom: 2rem;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.author-name {
  font-weight: 600;
  color: #5865f2;
}

.post-time {
  font-size: 0.875rem;
  color: #72767d;
}

.post-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9375rem;
  color: #72767d;
}

.post-content {
  padding: 0 2rem 2rem;
  border-bottom: 1px solid #e3e5e8;
}

.content-body {
  line-height: 1.6;
  color: #2c2f33;
  font-size: 1rem;
}

.content-body :deep(pre.code-block) {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
}

.content-body :deep(code.inline-code) {
  background: #f6f8fa;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.875em;
}

.content-body :deep(blockquote) {
  border-left: 4px solid #5865f2;
  background: #f8f9fa;
  padding: 0.75rem 1rem;
  margin: 1rem 0;
  border-radius: 0 6px 6px 0;
}

.content-body :deep(strong) {
  font-weight: 600;
}

.content-body :deep(em) {
  font-style: italic;
}

.replies-section {
  padding: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c2f33;
  margin: 0;
}

.btn-reply {
  background: linear-gradient(135deg, #5865f2, #7289da);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.btn-reply:hover {
  background: linear-gradient(135deg, #4752c4, #677bc4);
}

.reply-form {
  background: #f8f9fa;
  border: 1px solid #e3e5e8;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.reply-textarea {
  width: 100%;
  border: 1px solid #e3e5e8;
  border-radius: 6px;
  padding: 0.75rem;
  font-size: 0.9375rem;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 1rem;
}

.reply-textarea:focus {
  outline: none;
  border-color: #5865f2;
  box-shadow: 0 0 0 2px rgba(88, 101, 242, 0.1);
}

.reply-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-cancel, .btn-submit {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #f8f9fa;
  border: 1px solid #e3e5e8;
  color: #4f545c;
}

.btn-cancel:hover {
  background: #e9ecef;
}

.btn-submit {
  background: linear-gradient(135deg, #5865f2, #7289da);
  border: none;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #4752c4, #677bc4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.replies-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.reply-item {
  display: flex;
  gap: 0.75rem;
}

.reply-content {
  flex: 1;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.reply-header .author-name {
  font-weight: 600;
  color: #5865f2;
}

.reply-time {
  color: #72767d;
}

.floor-number {
  background: #e3e5e8;
  padding: 0.125rem 0.375rem;
  border-radius: 10px;
  font-size: 0.75rem;
  color: #4f545c;
  margin-left: auto;
}

.reply-body {
  line-height: 1.5;
  color: #2c2f33;
}

.empty-replies {
  text-align: center;
  padding: 3rem 1rem;
  color: #72767d;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-detail-page {
    padding: 1rem 0;
  }
  
  .post-title {
    font-size: 1.5rem;
    margin: 1rem 1rem;
  }
  
  .post-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
    padding: 0 1rem;
  }
  
  .post-content {
    padding: 0 1rem 1.5rem;
  }
  
  .replies-section {
    padding: 1.5rem 1rem;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .reply-item {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .reply-actions {
    flex-direction: column;
  }
}
</style>