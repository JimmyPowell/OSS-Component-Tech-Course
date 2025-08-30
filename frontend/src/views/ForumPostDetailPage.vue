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
            <div class="header-actions">
              <div class="sort-dropdown" ref="sortDropdown" :class="{ open: showSortDropdown }">
                <div 
                  class="custom-select"
                  @click="toggleSortDropdown"
                  :class="{ active: showSortDropdown }"
                >
                  <span class="selected-text">{{ getSortText(sortConfig) }}</span>
                  <i class="iconfont icon-down dropdown-icon" :class="{ rotated: showSortDropdown }"></i>
                </div>
                <div class="dropdown-menu" v-if="showSortDropdown">
                  <div 
                    class="dropdown-item"
                    :class="{ active: sortConfig === 'created_at_desc' }"
                    @click="selectSort('created_at_desc')"
                  >
                    <i class="iconfont icon-time"></i>
                    <span>最新回复</span>
                  </div>
                  <div 
                    class="dropdown-item"
                    :class="{ active: sortConfig === 'created_at_asc' }"
                    @click="selectSort('created_at_asc')"
                  >
                    <i class="iconfont icon-time"></i>
                    <span>最早回复</span>
                  </div>
                </div>
              </div>
              <button 
                v-if="!post.is_locked"
                @click="showReplyForm = !showReplyForm"
                class="btn-reply btn-reply-large"
              >
                <i class="icon">💬</i>
                {{ showReplyForm ? '取消回复' : '回复讨论' }}
              </button>
            </div>
          </div>

          <!-- 回复表单 -->
          <div v-if="showReplyForm && !post.is_locked" class="reply-form">
            <form @submit.prevent="submitReply(false)">
              <textarea 
                v-model="replyContent"
                placeholder="写下你的回复..."
                class="reply-textarea reply-textarea-large"
                rows="6"
                required
              ></textarea>
              <div class="reply-actions">
                <button type="button" @click="showReplyForm = false" class="btn-cancel btn-large">
                  取消
                </button>
                <button type="submit" :disabled="submittingReply" class="btn-submit btn-large">
                  {{ submittingReply ? '发布中...' : '发布回复' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Discord风格回复列表 -->
          <div class="replies-list discord-style">
            <DiscordReplyItem 
              v-for="reply in flatReplies" 
              :key="reply.uuid"
              :reply="reply" 
              :level="0"
              :max-level="5"
              :parent-methods="parentMethods"
              :auth-store="authStore"
            />
          </div>

          <!-- 空状态 -->
          <div v-if="flatReplies.length === 0" class="empty-replies">
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '../stores/auth'
import { forumApi } from '../api/forum'
import DiscordReplyItem from '../components/forum/DiscordReplyItem.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 响应式数据
const post = ref(null)
const replies = ref([]) // 树形结构的回复数据
const flatReplies = ref([]) // 扁平化的回复列表用于显示
const expandedReplies = ref(new Set()) // 记录展开的回复ID
const replyingTo = ref(null) // 记录当前回复的对象
const loading = ref(false)
const showReplyForm = ref(false)
const showNestedReplyForm = ref({}) // 记录嵌套回复表单状态
const nestedReplyContent = ref({}) // 记录嵌套回复内容
const replyContent = ref('')
const submittingReply = ref(false)

// 排序相关状态
const sortConfig = ref('created_at_desc')
const showSortDropdown = ref(false)
const sortDropdown = ref(null)

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
    // 转换为扁平化列表用于显示，使用当前排序配置
    flatReplies.value = flattenReplies(replies.value, sortConfig.value)
  } catch (error) {
    console.error('获取回复失败:', error)
    replies.value = []
    flatReplies.value = []
  }
}

// 将树形回复结构转换为扁平化列表（支持动态排序）
const flattenReplies = (repliesList, sortBy = 'created_at_desc') => {
  const flatList = []
  
  const collectReplies = (replies) => {
    replies.forEach(reply => {
      // 添加当前回复到扁平列表
      flatList.push({
        ...reply,
        hasChildren: reply.children && reply.children.length > 0,
        childrenData: reply.children || [] // 保存子回复数据用于展开功能
      })
      
      // 递归收集子回复
      if (reply.children && reply.children.length > 0) {
        collectReplies(reply.children)
      }
    })
  }
  
  collectReplies(repliesList)
  
  // 根据配置进行排序
  return sortReplies(flatList, sortBy)
}

// 排序回复列表
const sortReplies = (repliesList, sortBy) => {
  return repliesList.sort((a, b) => {
    switch (sortBy) {
      case 'created_at_asc':
        return new Date(a.created_at) - new Date(b.created_at)
      case 'created_at_desc':
      default:
        return new Date(b.created_at) - new Date(a.created_at)
    }
  })
}

// 切换回复展开状态
const toggleReplyExpanded = (replyUuid) => {
  if (expandedReplies.value.has(replyUuid)) {
    expandedReplies.value.delete(replyUuid)
  } else {
    expandedReplies.value.add(replyUuid)
  }
  // 强制响应式更新
  expandedReplies.value = new Set(expandedReplies.value)
}

// 获取某个回复的子回复列表（用于展开显示）
const getChildrenForReply = (replyUuid) => {
  const reply = flatReplies.value.find(r => r.uuid === replyUuid)
  return reply ? reply.childrenData : []
}

// 提交回复内部实现
const submitReplyInternal = async (isNested = false, replyId = null, content = null) => {
  if (!authStore.isAuthenticated) {
    message.warning('请先登录后再回复')
    authStore.showLoginModal()
    return
  }
  
  const replyContentText = content || (isNested ? nestedReplyContent.value[replyId] : replyContent.value)
  if (!replyContentText || !replyContentText.trim()) {
    message.warning('请输入回复内容')
    return
  }
  
  submittingReply.value = true
  
  try {
    const replyData = {
      post_id: post.value.id,
      content: replyContentText.trim()
    }
    
    // 如果是嵌套回复，设置parent_id和reply_to_user_id
    if (isNested && replyId) {
      const parentReply = findReplyById(replies.value, replyId)
      if (parentReply) {
        replyData.parent_id = parentReply.id  // 直接使用被回复评论的ID作为parent_id
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
    
    message.success('回复成功！')
  } catch (error) {
    console.error('回复失败:', error)
    
    if (error.response?.status === 401) {
      message.error('登录已过期，请重新登录')
      authStore.showLoginModal()
    } else {
      message.error('回复失败，请稍后重试')
    }
  } finally {
    submittingReply.value = false
  }
}

// 原始的submitReply函数（兼容现有调用）
const submitReply = async (isNested = false, replyId = null) => {
  return submitReplyInternal(isNested, replyId)
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
    message.warning('请先登录后再回复')
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

// 父组件方法对象
const parentMethods = {
  formatTime,
  formatContent,
  submitReply: async (isNested = false, replyId = null, content = null) => {
    return submitReplyInternal(isNested, replyId, content)
  },
  toggleReplyExpanded,
  getChildrenForReply,
  isReplyExpanded: (replyUuid) => expandedReplies.value.has(replyUuid)
}

// 排序相关方法
const toggleSortDropdown = () => {
  showSortDropdown.value = !showSortDropdown.value
}

const selectSort = (value) => {
  if (value !== sortConfig.value) {
    sortConfig.value = value
    // 重新应用排序到现有数据
    flatReplies.value = flattenReplies(replies.value, sortConfig.value)
  }
  showSortDropdown.value = false
}

const getSortText = (value) => {
  const sortTexts = {
    'created_at_desc': '最新回复',
    'created_at_asc': '最早回复'
  }
  return sortTexts[value] || '最新回复'
}

// 处理点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  if (sortDropdown.value && !sortDropdown.value.contains(event.target)) {
    showSortDropdown.value = false
  }
}

onMounted(async () => {
  await fetchPost()
  if (post.value) {
    await fetchReplies()
  }
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* 排序筛选器样式 */
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
  border-color: #5865f2;
  box-shadow: 0 2px 8px rgba(88, 101, 242, 0.15);
}

.custom-select.active {
  border-color: #5865f2;
  box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.1);
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
  color: #5865f2;
}

.dropdown-item.active {
  background-color: #5865f2;
  color: white;
}

.dropdown-item.active:hover {
  background-color: #4752c4;
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

/* 大尺寸回复按钮 */
.btn-reply-large {
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
  border-radius: 8px;
}

.btn-reply-large .icon {
  font-size: 1.25rem;
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

/* 大尺寸回复输入框 */
.reply-textarea-large {
  padding: 1rem;
  font-size: 1.125rem;
  border-radius: 8px;
  line-height: 1.6;
  min-height: 150px;
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

/* 大尺寸按钮 */
.btn-large {
  padding: 0.5rem 1.25rem !important;
  font-size: 0.9375rem !important;
  border-radius: 6px !important;
}

/* 确保提交按钮的大尺寸样式正确应用 */
.btn-submit.btn-large {
  padding: 0.5rem 1.25rem;
  font-size: 0.9375rem;
  border-radius: 6px;
  min-width: 100px;
  font-weight: 600;
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
  
  .header-actions {
    width: 100%;
    flex-direction: column;
    gap: 1rem;
  }
  
  .custom-select {
    width: 100%;
    min-width: auto;
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