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
                {{ post.author.username || post.author.real_name }}
              </span>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>
          </div>
          <div class="post-stats">
            <span class="stat"><i class="bi bi-eye"></i> {{ post.view_count }}</span>
            <span class="stat"><i class="bi bi-chat-dots"></i> {{ post.reply_count }}</span>
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
              回复 ({{ getTotalRepliesCount(replies) }})
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
            <form @submit.prevent="submitReply(false)">
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

          <!-- Discord风格回复列表 -->
          <div class="replies-list discord-style">
            <template v-for="reply in replies" :key="reply.uuid">
              <DiscordReplyItem 
                :reply="reply" 
                :level="0"
                :parent-instance="{ 
                  formatTime, 
                  formatContent, 
                  showNestedReplyForm, 
                  nestedReplyContent, 
                  submittingReply, 
                  authStore,
                  showNestedReplyToReply,
                  submitReply
                }"
              />
            </template>
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
const replyingTo = ref(null) // 记录当前回复的对象
const loading = ref(false)
const showReplyForm = ref(false)
const showNestedReplyForm = ref({}) // 记录嵌套回复表单状态
const nestedReplyContent = ref({}) // 记录嵌套回复内容
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

// 获取回复列表（树结构）
const fetchReplies = async () => {
  if (!post.value) return
  
  try {
    const response = await forumApi.reply.getRepliesTree(post.value.uuid)
    replies.value = response.data.data || []
  } catch (error) {
    console.error('获取回复失败:', error)
    replies.value = []
  }
}

// 提交回复
const submitReply = async (isNested = false, replyId = null) => {
  if (!authStore.isAuthenticated) {
    alert('请先登录后再回复')
    authStore.showLoginModal()
    return
  }
  
  const content = isNested ? nestedReplyContent.value[replyId] : replyContent.value
  if (!content || !content.trim()) {
    alert('请输入回复内容')
    return
  }
  
  submittingReply.value = true
  
  try {
    const replyData = {
      post_id: post.value.id,
      content: content.trim()
    }
    
    // 如果是嵌套回复，设置parent_id和reply_to_user_id
    if (isNested && replyId) {
      const parentReply = findReplyById(replies.value, replyId)
      if (parentReply) {
        replyData.parent_id = findReplyParentId(replies.value, replyId)
        replyData.reply_to_user_id = parentReply.user_id
      }
    }
    
    await forumApi.reply.createReply(replyData)
    
    // 成功后重置表单并刷新回复列表
    if (isNested) {
      nestedReplyContent.value[replyId] = ''
      showNestedReplyForm.value[replyId] = false
    } else {
      replyContent.value = ''
      showReplyForm.value = false
    }
    
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

// 辅助函数：在树结构中查找回复
const findReplyById = (repliesList, replyId) => {
  for (const reply of repliesList) {
    if (reply.uuid === replyId) {
      return reply
    }
    if (reply.children && reply.children.length > 0) {
      const found = findReplyById(reply.children, replyId)
      if (found) return found
    }
  }
  return null
}

// 辅助函数：获取父回复ID（用于数据库）
const findReplyParentId = (repliesList, replyId) => {
  const reply = findReplyById(repliesList, replyId)
  return reply ? reply.id || reply.parent_id : null
}

// 显示嵌套回复表单
const showNestedReplyToReply = (replyId) => {
  if (!authStore.isAuthenticated) {
    alert('请先登录后再回复')
    authStore.showLoginModal()
    return
  }
  
  showNestedReplyForm.value[replyId] = !showNestedReplyForm.value[replyId]
  
  // 初始化内容
  if (showNestedReplyForm.value[replyId] && !nestedReplyContent.value[replyId]) {
    nestedReplyContent.value[replyId] = ''
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
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

// 页面加载
// 计算总回复数量（递归计算） - 用于显示回复总数
const getTotalRepliesCount = (repliesList) => {
  let count = repliesList.length
  repliesList.forEach(reply => {
    if (reply.children && reply.children.length > 0) {
      count += getTotalRepliesCount(reply.children)
    }
  })
  return count
}

onMounted(async () => {
  await fetchPost()
  if (post.value) {
    await fetchReplies()
  }
})

</script>

<script>
// 递归回复组件定义
const DiscordReplyItem = {
  name: 'DiscordReplyItem',
  props: ['reply', 'level', 'parentInstance'],
  template: `
    <div class="discord-reply-thread">
      <div class="discord-reply-item" :class="{ 'has-children': reply.children && reply.children.length > 0 }">
        <div class="reply-connector" v-if="level > 0"></div>
        
        <div class="reply-main">
          <div class="reply-author-avatar">
            <img 
              :src="reply.author?.avatar_url || '/images/head.png'" 
              alt="头像"
              class="avatar"
            >
          </div>
          
          <div class="reply-content-wrapper">
            <div v-if="reply.reply_to_user && reply.reply_to_user.id !== reply.author?.id" class="reply-reference">
              <i class="bi bi-reply"></i>
              <span class="reply-to-user">{{ reply.reply_to_user.username || reply.reply_to_user.real_name }}</span>
            </div>
            
            <div class="reply-header">
              <span class="author-name">{{ reply.author?.username || reply.author?.real_name }}</span>
              <span class="reply-time">{{ parentInstance.formatTime(reply.created_at) }}</span>
              <span v-if="reply.floor_number" class="floor-number">#{{ reply.floor_number }}</span>
            </div>
            
            <div class="reply-body" v-html="parentInstance.formatContent(reply.content)"></div>
            
            <div class="reply-actions">
              <button 
                @click="parentInstance.showNestedReplyToReply(reply.uuid)" 
                class="btn-reply"
                v-if="!parentInstance.showNestedReplyForm[reply.uuid]"
              >
                <i class="bi bi-reply"></i> 回复
              </button>
              
              <span v-if="reply.children && reply.children.length > 0" class="replies-count">
                {{ reply.children.length }} 个回复
              </span>
            </div>
            
            <div v-if="parentInstance.showNestedReplyForm[reply.uuid]" class="discord-reply-form">
              <form @submit.prevent="parentInstance.submitReply(true, reply.uuid)">
                <div class="form-header">
                  <img :src="parentInstance.authStore.user?.avatar_url || '/images/head.png'" alt="我的头像" class="my-avatar">
                  <span class="replying-to">回复 {{ reply.author?.username || reply.author?.real_name }}</span>
                </div>
                <textarea 
                  v-model="parentInstance.nestedReplyContent[reply.uuid]"
                  placeholder="输入你的回复..."
                  class="reply-textarea"
                  rows="3"
                  required
                ></textarea>
                <div class="form-actions">
                  <button type="button" @click="parentInstance.showNestedReplyToReply(reply.uuid)" class="btn-cancel">
                    取消
                  </button>
                  <button type="submit" :disabled="parentInstance.submittingReply" class="btn-send">
                    {{ parentInstance.submittingReply ? '发送中...' : '发送' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="reply.children && reply.children.length > 0" class="discord-children-replies">
        <DiscordReplyItem 
          v-for="childReply in reply.children" 
          :key="childReply.uuid"
          :reply="childReply"
          :level="level + 1"
          :parent-instance="parentInstance"
        />
      </div>
    </div>
  `,
  components: {
    DiscordReplyItem: () => DiscordReplyItem
  }
}

export default {
  components: {
    DiscordReplyItem
  }
}
</script>

<style scoped>
.post-detail-page {
  min-height: 100vh;
  background: #f6f7f9;
  padding: 10rem 0 2rem 0;
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
  margin-bottom: 2.5rem;
  padding-bottom: 1rem;
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
  padding: 0.5rem 1rem;
  border-radius: 16px;
  font-size: 1.125rem;
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
  font-size: 3.2rem;
  font-weight: 700;
  color: #2c2f33;
  line-height: 1.3;
  margin: 1.5rem 2rem;
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
  font-size: 1.4rem;
}

.post-time {
  font-size: 1.25rem;
  color: #72767d;
}

.post-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 1.4rem;
  color: #72767d;
}

.post-content {
  padding: 0 2rem 2rem;
  border-bottom: 1px solid #e3e5e8;
}

.content-body {
  line-height: 1.8;
  color: #2c2f33;
  font-size: 1.6rem;
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
  font-size: 2rem;
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
  align-items: center;
}

.btn-cancel, .btn-submit {
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: auto;
  width: auto;
  flex-shrink: 0;
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

/* Discord风格回复列表 */
.replies-list.discord-style {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.discord-reply-thread {
  margin-bottom: 1rem;
}

.discord-reply-item {
  display: flex;
  position: relative;
  margin-bottom: 0.5rem;
}

.discord-reply-item.has-children {
  margin-bottom: 0;
}

/* 连接线 */
.reply-connector {
  width: 2px;
  background: #e3e5e8;
  margin-right: 1rem;
  flex-shrink: 0;
}

.reply-main {
  display: flex;
  flex: 1;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.reply-author-avatar {
  flex-shrink: 0;
}

.reply-author-avatar .avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.reply-content-wrapper {
  flex: 1;
  min-width: 0;
}

/* 回复引用样式 */
.reply-reference {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: #72767d;
}

.reply-reference .bi-reply {
  font-size: 0.875rem;
}

.reply-to-user {
  color: #5865f2;
  font-weight: 500;
  cursor: pointer;
}

.reply-to-user:hover {
  text-decoration: underline;
}

/* 回复头部 */
.discord-reply-item .reply-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.discord-reply-item .author-name {
  font-weight: 600;
  color: #5865f2;
  font-size: 1.125rem;
}

.discord-reply-item .reply-time {
  font-size: 0.875rem;
  color: #72767d;
}

.discord-reply-item .floor-number {
  background: #f2f3f5;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  color: #4f545c;
}

/* 回复内容 */
.discord-reply-item .reply-body {
  line-height: 1.6;
  color: #2c2f33;
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
  word-wrap: break-word;
}

/* 回复操作 */
.discord-reply-item .reply-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.25rem;
}

.discord-reply-item .btn-reply {
  background: transparent;
  border: none;
  color: #72767d;
  font-size: 0.875rem;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.discord-reply-item .btn-reply:hover {
  color: #5865f2;
  background: #f8f9fa;
}

.replies-count {
  font-size: 0.875rem;
  color: #5865f2;
  font-weight: 500;
}

/* Discord回复表单 */
.discord-reply-form {
  margin-top: 0.75rem;
  background: #f8f9fa;
  border: 1px solid #e3e5e8;
  border-radius: 8px;
  padding: 0.75rem;
}

.discord-reply-form .form-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.discord-reply-form .my-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
}

.discord-reply-form .replying-to {
  font-size: 0.875rem;
  color: #72767d;
}

.discord-reply-form .reply-textarea {
  width: 100%;
  border: 1px solid #e3e5e8;
  border-radius: 6px;
  padding: 0.5rem;
  font-size: 0.875rem;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 0.5rem;
  min-height: 60px;
}

.discord-reply-form .reply-textarea:focus {
  outline: none;
  border-color: #5865f2;
  box-shadow: 0 0 0 2px rgba(88, 101, 242, 0.1);
}

.discord-reply-form .form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.discord-reply-form .btn-cancel,
.discord-reply-form .btn-send {
  padding: 0.375rem 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.discord-reply-form .btn-cancel {
  background: transparent;
  border: 1px solid #e3e5e8;
  color: #4f545c;
}

.discord-reply-form .btn-cancel:hover {
  background: #f2f3f5;
}

.discord-reply-form .btn-send {
  background: #5865f2;
  border: none;
  color: white;
}

.discord-reply-form .btn-send:hover:not(:disabled) {
  background: #4752c4;
}

.discord-reply-form .btn-send:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 子回复区域 */
.discord-children-replies {
  margin-left: 3rem;
  border-left: 2px solid #e3e5e8;
  padding-left: 1rem;
  margin-top: 0.5rem;
}

.discord-children-replies .discord-reply-item {
  margin-bottom: 0.75rem;
}

.discord-children-replies .discord-reply-item:last-child {
  margin-bottom: 0;
}

/* 老的回复样式已被 Discord 风格替代 */

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