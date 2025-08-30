<template>
  <div class="discord-reply-wrapper" :style="{ '--level': level }">
    <!-- 主回复 -->
    <div class="discord-reply-item" :class="{ 'has-children': hasChildren && isExpanded }">
      <!-- 层级连接线 -->
      <div v-if="level > 0" class="reply-connector"></div>
      
      <!-- 回复主体 -->
      <div class="reply-main">
        <!-- 头像 -->
        <div class="reply-avatar">
          <img 
            :src="reply.author?.avatar_url || '/images/head.png'" 
            :alt="reply.author?.username || '用户头像'"
            class="avatar"
          >
        </div>
        
        <!-- 内容区域 -->
        <div class="reply-content">
          <!-- 回复引用 -->
          <div v-if="reply.reply_to_user && reply.reply_to_user.id !== reply.author?.id" class="reply-reference">
            <i class="reply-icon">↳</i>
            <span class="reply-to-user" @click="scrollToUser(reply.reply_to_user.id)">
              {{ reply.reply_to_user.username || reply.reply_to_user.real_name }}
            </span>
          </div>
          
          <!-- 用户信息行 -->
          <div class="reply-header">
            <span class="author-name">{{ reply.author?.username || reply.author?.real_name }}</span>
            <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
            <span v-if="reply.floor_number" class="floor-number">#{{ reply.floor_number }}</span>
          </div>
          
          <!-- 回复内容 -->
          <div class="reply-body" v-html="formatContent(reply.content)"></div>
          
          <!-- 操作区域 -->
          <div class="reply-actions">
            <!-- 点赞按钮 -->
            <button 
              @click="toggleLike" 
              class="action-btn like-btn"
              :class="{ 'liked': isLiked }"
            >
              <i class="action-icon">{{ isLiked ? '❤️' : '🤍' }}</i>
              {{ likeCount > 0 ? likeCount : '点赞' }}
            </button>
            
            <button 
              @click="toggleReplyForm" 
              class="action-btn reply-btn"
              v-if="!showReplyForm"
            >
              <i class="action-icon">💬</i>
              回复
            </button>
            
            <!-- 子回复统计和展开/折叠 -->
            <button 
              v-if="hasChildren" 
              @click="toggleExpanded"
              class="action-btn replies-toggle"
            >
              <i class="toggle-icon" :class="{ 'expanded': isExpanded }">{{ isExpanded ? '▼' : '▶' }}</i>
              {{ childrenCount }}个回复
            </button>
          </div>
          
          <!-- 回复表单 -->
          <div v-if="showReplyForm" class="reply-form">
            <div class="form-header">
              <img :src="authStore.user?.avatar_url || '/images/head.png'" alt="我的头像" class="my-avatar">
              <span class="replying-to">回复 {{ reply.author?.username || reply.author?.real_name }}</span>
            </div>
            <form @submit.prevent="handleSubmitReply">
              <textarea 
                v-model="replyContent"
                placeholder="输入你的回复..."
                class="reply-textarea reply-textarea-large"
                rows="4"
                required
              ></textarea>
              <div class="form-actions">
                <button type="button" @click="cancelReply" class="btn-cancel btn-large">
                  取消
                </button>
                <button type="submit" :disabled="submitting" class="btn-send btn-large">
                  {{ submitting ? '发送中...' : '发送' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 子回复区域 -->
    <div v-if="hasChildren && isExpanded" class="reply-children">
      <DiscordReplyItem 
        v-for="childReply in parentMethods.getChildrenForReply(reply.uuid)" 
        :key="childReply.uuid"
        :reply="childReply"
        :level="level + 1"
        :max-level="maxLevel"
        :parent-methods="parentMethods"
        :auth-store="authStore"
      />
    </div>
    
    <!-- 查看更多链接（当层级过深时） -->
    <div v-if="hasChildren && !isExpanded && level >= maxLevel" class="view-more">
      <button @click="viewMoreReplies" class="view-more-btn">
        查看此线程的更多回复 ({{ childrenCount }})
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'

// Props
const props = defineProps({
  reply: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  },
  maxLevel: {
    type: Number,
    default: 5
  },
  parentMethods: {
    type: Object,
    required: true
  },
  authStore: {
    type: Object,
    required: true
  }
})

// 响应式状态，现在从父组件获取展开状态
const isExpanded = computed(() => props.parentMethods.isReplyExpanded(props.reply.uuid))
const showReplyForm = ref(false)
const replyContent = ref('')
const submitting = ref(false)

// 点赞相关状态
const isLiked = ref(false) // TODO: 从用户点赞状态获取
const likeCount = ref(props.reply.like_count || 0)
const likingInProgress = ref(false)

// 计算属性
const hasChildren = computed(() => {
  return props.reply.hasChildren || false
})

const childrenCount = computed(() => {
  return props.reply.childrenData ? props.reply.childrenData.length : 0
})

// 方法
const formatTime = (dateString) => {
  return props.parentMethods.formatTime(dateString)
}

const formatContent = (content) => {
  return props.parentMethods.formatContent(content)
}

const toggleExpanded = () => {
  // 使用父组件的展开切换方法
  props.parentMethods.toggleReplyExpanded(props.reply.uuid)
}

const toggleReplyForm = () => {
  if (!props.authStore.isAuthenticated) {
    message.warning('请先登录后再回复')
    props.authStore.showLoginModal()
    return
  }
  showReplyForm.value = !showReplyForm.value
  if (showReplyForm.value) {
    replyContent.value = ''
  }
}

const cancelReply = () => {
  showReplyForm.value = false
  replyContent.value = ''
}

const handleSubmitReply = async () => {
  if (!replyContent.value.trim()) {
    message.warning('请输入回复内容')
    return
  }
  
  submitting.value = true
  try {
    await props.parentMethods.submitReply(true, props.reply.uuid, replyContent.value.trim())
    showReplyForm.value = false
    replyContent.value = ''
  } catch (error) {
    console.error('回复失败:', error)
  } finally {
    submitting.value = false
  }
}

const scrollToUser = (userId) => {
  // 滚动到指定用户的回复
  console.log('滚动到用户:', userId)
}

const viewMoreReplies = () => {
  // 跳转到专门的线程页面或展开所有回复
  isExpanded.value = true
}

// 点赞功能
const toggleLike = async () => {
  if (!props.authStore.isAuthenticated) {
    message.warning('请先登录后再点赞')
    props.authStore.showLoginModal()
    return
  }

  if (likingInProgress.value) return

  likingInProgress.value = true
  
  try {
    // TODO: 调用点赞/取消点赞API
    // 暂时先模拟API调用
    await new Promise(resolve => setTimeout(resolve, 300))
    
    if (isLiked.value) {
      // 取消点赞
      isLiked.value = false
      likeCount.value = Math.max(0, likeCount.value - 1)
    } else {
      // 点赞
      isLiked.value = true  
      likeCount.value += 1
    }
  } catch (error) {
    console.error('点赞操作失败:', error)
    message.error('操作失败，请稍后重试')
  } finally {
    likingInProgress.value = false
  }
}
</script>

<style scoped>
.discord-reply-wrapper {
  --indent-size: 2rem;
  --level: 0;
  margin-left: calc(var(--level) * var(--indent-size));
}

.discord-reply-item {
  display: flex;
  margin-bottom: 0.5rem;
  position: relative;
}

.discord-reply-item.has-children {
  margin-bottom: 0.25rem;
}

/* 连接线 */
.reply-connector {
  width: 2px;
  background: #e3e5e8;
  margin-right: 1rem;
  flex-shrink: 0;
  min-height: 1rem;
}

.reply-main {
  display: flex;
  flex: 1;
  gap: 1rem;
  background: #ffffff;
  border-radius: 10px;
  padding: 1.25rem;
  border: 1px solid #e3e5e8;
  transition: all 0.2s ease;
  margin-bottom: 0.75rem;
}

.reply-main:hover {
  border-color: #5865f2;
  box-shadow: 0 2px 8px rgba(88, 101, 242, 0.1);
}

/* 头像 */
.reply-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

/* 内容区域 */
.reply-content {
  flex: 1;
  min-width: 0;
}

/* 回复引用 */
.reply-reference {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: #72767d;
}

.reply-icon {
  color: #5865f2;
  font-size: 0.875rem;
}

.reply-to-user {
  color: #5865f2;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
}

.reply-to-user:hover {
  text-decoration: underline;
}

/* 用户信息行 */
.reply-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.author-name {
  font-weight: 600;
  color: #2c2f33;
  font-size: 1.375rem;
}

.reply-time {
  font-size: 1.125rem;
  color: #72767d;
}

.floor-number {
  background: #f2f3f5;
  color: #4f545c;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
}

/* 回复内容 */
.reply-body {
  line-height: 1.7;
  color: #2c2f33;
  font-size: 1.25rem;
  margin-bottom: 1rem;
  word-wrap: break-word;
}

.reply-body :deep(p) {
  margin: 0.5rem 0;
}

.reply-body :deep(code) {
  background: #f6f8fa;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
  font-size: 0.875em;
}

.reply-body :deep(pre) {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}

/* 操作区域 */
.reply-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.action-btn {
  background: none;
  border: none;
  color: #72767d;
  font-size: 1.125rem;
  cursor: pointer;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-weight: 500;
}

.action-btn:hover {
  color: #5865f2;
  background: #f8f9fa;
}

.action-icon, .toggle-icon {
  font-size: 0.875rem;
}

.toggle-icon {
  transition: transform 0.2s ease;
}

.toggle-icon.expanded {
  transform: rotate(0deg);
}

.replies-toggle {
  color: #5865f2;
  font-weight: 500;
}

.replies-toggle:hover {
  background: rgba(88, 101, 242, 0.1);
}

/* 点赞按钮样式 */
.like-btn {
  color: #72767d;
  transition: all 0.2s ease;
}

.like-btn:hover {
  color: #e91e63;
  background: rgba(233, 30, 99, 0.1);
}

.like-btn.liked {
  color: #e91e63;
}

.like-btn.liked:hover {
  background: rgba(233, 30, 99, 0.15);
}

/* 回复表单 */
.reply-form {
  margin-top: 0.75rem;
  background: #f8f9fa;
  border: 1px solid #e3e5e8;
  border-radius: 8px;
  padding: 0.75rem;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.my-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
}

.replying-to {
  font-size: 0.875rem;
  color: #72767d;
}

.reply-textarea {
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

.reply-textarea:focus {
  outline: none;
  border-color: #5865f2;
  box-shadow: 0 0 0 2px rgba(88, 101, 242, 0.1);
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-cancel, .btn-send {
  padding: 0.375rem 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: transparent;
  border: 1px solid #e3e5e8;
  color: #4f545c;
}

.btn-cancel:hover {
  background: #f2f3f5;
}

.btn-send {
  background: #5865f2;
  border: none;
  color: white;
}

.btn-send:hover:not(:disabled) {
  background: #4752c4;
}

.btn-send:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 大尺寸元素样式 */
.reply-textarea-large {
  padding: 1rem;
  font-size: 1.125rem;
  border-radius: 8px;
  line-height: 1.6;
  min-height: 120px;
}

.btn-large {
  padding: 0.75rem 2rem;
  font-size: 1.125rem;
  border-radius: 8px;
}

/* 子回复区域 */
.reply-children {
  margin-top: 0.75rem;
  border-left: 3px solid #e3e5e8;
  padding-left: 1.5rem;
  margin-left: calc(48px + 1rem); /* 头像宽度 + gap */
}

/* 查看更多 */
.view-more {
  margin-top: 0.75rem;
  margin-left: calc(48px + 1rem);
}

.view-more-btn {
  background: none;
  border: none;
  color: #5865f2;
  font-size: 0.875rem;
  cursor: pointer;
  text-decoration: underline;
  padding: 0.25rem 0;
}

.view-more-btn:hover {
  color: #4752c4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .discord-reply-wrapper {
    --indent-size: 1rem;
  }
  
  .reply-main {
    padding: 0.5rem;
  }
  
  .avatar {
    width: 40px;
    height: 40px;
  }
  
  .reply-children {
    margin-left: calc(40px + 0.75rem);
    padding-left: 1rem;
  }
  
  .view-more {
    margin-left: calc(40px + 0.75rem);
  }
}
</style>