<template>
  <div class="page">
    <div class="page-section">
      <div class="container">
        <div class="page-title">开源技术blog</div>
        <div class="swiper-mtr">
          <div class="swiper-container blog-swiper">
            <div class="swiper-wrapper">
              <div class="swiper-slide" v-for="n in 6" :key="`blog-${n}`">
                <div class="blog-card">
                  <div class="blog-head">
                    <img src="/images/head.png" alt="">
                    <span class="item">李明·2小时前</span>
                    <span class="tag">Java 开源框架”</span>
                  </div>
                  <div class="blog-body">
                    <div class="blog-title"><a href="">GitHub 趋势榜 - 实时热门项目和开发者追踪</a></div>
                    <div class="blog-desc">GitHub 趋势榜是开发者追踪实时热门项目和开发者的重要工具...</div>
                  </div>
                  <div class="blog-foot">
                    <div class="item">
                      <span class="iconfont icon-eyes"></span>
                      <span class="num">328 阅读</span>
                    </div>
                    <div class="item">
                      <span class="iconfont icon-dzs"></span>
                      <span class="num">24赞</span>
                    </div>
                    <div class="item">
                      <span class="iconfont icon-taolun"></span>
                      <span class="num">8评论</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="blog-pagination"></div>
          </div>
        </div>
      </div>
    </div>
    <div class="page-section">
      <div class="container">
        <div class="page-title">课程讨论互动社区</div>
        
        <!-- 热门帖子展示区域 -->
        <div class="forum-hot-posts" v-if="hotPosts.length > 0">
          <div class="post-grid">
            <div 
              v-for="post in hotPosts.slice(0, 6)" 
              :key="post.uuid"
              class="post-card"
              @click="navigateToPost(post.uuid)"
            >
              <div class="post-header">
                <div class="post-category" v-if="post.category">
                  <i class="category-icon" v-if="post.category.icon">{{ post.category.icon }}</i>
                  <span class="category-name">{{ post.category.name }}</span>
                </div>
                <div class="post-stats">
                  <span class="view-count">
                    <i class="icon">👀</i>
                    {{ post.view_count }}
                  </span>
                  <span class="reply-count">
                    <i class="icon">💬</i>
                    {{ post.reply_count }}
                  </span>
                </div>
              </div>
              
              <div class="post-title">{{ post.title }}</div>
              
              <div class="post-meta">
                <div class="post-author" v-if="post.author">
                  <img 
                    :src="post.author.avatar_url || '/images/head.png'" 
                    alt="头像" 
                    class="author-avatar"
                  >
                  <span class="author-name">
                    {{ post.author.real_name || post.author.username }}
                  </span>
                </div>
                <div class="post-time">
                  {{ formatTime(post.created_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else-if="!loading" class="empty-state">
          <p>暂无热门讨论，成为第一个发起讨论的人吧！</p>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <p>加载中...</p>
        </div>

        <!-- 进入论坛中心按钮 -->
        <div class="forum-actions">
          <button 
            class="btn-forum-center"
            @click="navigateToForumCenter"
          >
            <i class="icon">🚀</i>
            进入讨论中心
          </button>
        </div>
      </div>
    </div>
    <div class="page-section">
      <div class="container">
        <div class="page-title">学生课程活跃度排名</div>
        <div class="rank-table">
          <div class="rank-table_head">
            <div class="rank-row">
              <div class="table-cell">排名</div>
              <div class="table-cell">头像</div>
              <div class="table-cell">用户昵称</div>
              <div class="table-cell">活跃时间</div>
            </div>
          </div>
          <div class="rank-table_tbody">
            <div class="rank-row" v-for="n in 10" :key="`rank-${n}`">
              <div class="table-cell">
                <div class="cell-num">
                  <img v-if="n <= 3" :src="`/images/rank${n}.png`" alt="">
                  <span v-else>{{ n }}</span>
                </div>
              </div>
              <div class="table-cell">
                <img src="/images/head.png" class="rank-avatar" alt="">
              </div>
              <div class="table-cell">
                张三
              </div>
              <div class="table-cell">
                189小时36分钟
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Swiper from 'swiper/bundle'
import { forumApi } from '../api/forum'

const router = useRouter()

// 响应式数据
const hotPosts = ref([])
const loading = ref(false)

// 获取热门帖子
const fetchHotPosts = async () => {
  loading.value = true
  try {
    const response = await forumApi.post.getHotPosts({ limit: 8, days: 30 })
    hotPosts.value = response.data.data || []
  } catch (error) {
    console.error('获取热门帖子失败:', error)
    hotPosts.value = []
  } finally {
    loading.value = false
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
      day: '2-digit'
    })
  }
}

// 导航到帖子详情
const navigateToPost = (uuid) => {
  router.push(`/community/forum/post/${uuid}`)
}

// 导航到论坛中心
const navigateToForumCenter = () => {
  router.push('/community/forum')
}

onMounted(async () => {
  // 初始化Swiper
  new Swiper('.blog-swiper', {
    slidesPerView: 1,
    slidesPerColumn: 3,
    spaceBetween: 0,
    pagination: {
      el: '.blog-pagination',
      clickable: true,
    },
  })

  // 加载热门帖子
  await fetchHotPosts()
})
</script>

<style scoped>
/* Discord风格论坛帖子样式 */
.forum-hot-posts {
  margin-bottom: 2rem;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.post-card {
  background: #ffffff;
  border: 1px solid #e3e5e8;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.post-card:hover {
  border-color: #5865f2;
  box-shadow: 0 4px 12px rgba(88, 101, 242, 0.15);
  transform: translateY(-2px);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.post-category {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f2f3f5;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
}

.category-icon {
  font-size: 1rem;
}

.category-name {
  font-weight: 500;
  color: #4f545c;
}

.post-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #72767d;
}

.view-count, .reply-count {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.post-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2c2f33;
  line-height: 1.4;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.author-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #5865f2;
}

.post-time {
  font-size: 0.8125rem;
  color: #72767d;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #72767d;
  font-size: 1.1rem;
}

.forum-actions {
  text-align: center;
  margin-top: 2rem;
}

.btn-forum-center {
  background: linear-gradient(135deg, #5865f2, #7289da);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.875rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-forum-center:hover {
  background: linear-gradient(135deg, #4752c4, #677bc4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(88, 101, 242, 0.4);
}

.btn-forum-center .icon {
  font-size: 1.1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .post-card {
    padding: 1rem;
  }
  
  .post-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .post-stats {
    align-self: flex-end;
  }
}
</style>
