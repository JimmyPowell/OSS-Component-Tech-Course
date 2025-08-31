<template>
  <div class="page">
    <div class="container">
      <div class="page-title">优秀作品展示</div>
      
      <!-- Loading state -->
      <div v-if="loading" class="loading-state flex-center">
        <div class="spinner"></div>
        <span>正在加载作品...</span>
      </div>

      <!-- Empty state -->
      <div v-else-if="!loading && showcases.length === 0" class="empty-state flex-center">
        <div class="empty-content">
          <div class="empty-icon">📚</div>
          <p>暂无作品展示</p>
          <span class="empty-desc">还没有发布作品，期待您的精彩作品</span>
        </div>
      </div>

      <!-- Showcase grid -->
      <div v-else class="card-cels">
        <ul class="row card-row">
          <li class="col-md-4" v-for="showcase in showcases" :key="showcase.uuid">
            <div class="card-cell">
              <router-link :to="`/showcase/${showcase.uuid}`" class="card-img scale">
                <img 
                  :src="showcase.avatar_url || `/images/show${Math.floor(Math.random() * 3) + 1}.png`" 
                  :alt="showcase.name"
                  @error="handleImageError"
                >
              </router-link>
              <div class="card-grid mb-10">
                <div class="card-title">
                  <router-link :to="`/showcase/${showcase.uuid}`">{{ showcase.name }}</router-link>
                </div>
                <div class="card-time">{{ formatDate(showcase.created_at) }}</div>
              </div>
              <div class="card-meta">
                <img src="/images/avatat.png" alt="用户头像">
                <span>{{ showcase.author?.username || showcase.author?.real_name || '匿名用户' }}</span>
              </div>
              <div class="card-stats">
                <span class="stat-item">
                  <i class="iconfont icon-eye"></i>
                  {{ showcase.views_count || 0 }}
                </span>
                <span class="stat-item">
                  <i class="iconfont icon-dianzan"></i>
                  {{ showcase.likes_count || 0 }}
                </span>
              </div>
            </div>
          </li>
        </ul>

        <!-- Pagination -->
        <div class="pagination-cell flex-center" v-if="totalPages > 1">
          <button 
            class="pagination-btn" 
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            <span class="iconfont icon-l-left"></span>
          </button>
          
          <button 
            v-for="page in visiblePages" 
            :key="page"
            class="pagination-btn"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
          
          <button 
            class="pagination-btn" 
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            <span class="iconfont icon-l-right"></span>
          </button>
          
          <div class="pagination-info flex-center">
            <span>跳至</span>
            <input 
              type="number" 
              class="form-control pagination-input"
              v-model.number="jumpPage"
              @keyup.enter="jumpToPage"
              :min="1"
              :max="totalPages"
            >
            <span>页</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { showcaseAPI } from '@/api/showcase'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 响应式数据
const showcases = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const jumpPage = ref('')

// 计算属性
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// 方法
const fetchShowcases = async () => {
  try {
    loading.value = true
    const response = await showcaseAPI.getFrontendShowcases({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    })
    
    console.log('API响应:', response)
    
    if (response.data && response.data.code === 200) {
      const data = response.data.data
      if (data && data.items) {
        showcases.value = data.items
        total.value = data.total || 0
      } else if (Array.isArray(data)) {
        // 如果data直接是数组
        showcases.value = data
        total.value = data.length
      } else {
        console.log('未知的数据格式:', data)
        showcases.value = []
        total.value = 0
      }
    } else if (response.success) {
      // 兼容旧格式
      showcases.value = response.data.items || []
      total.value = response.data.total || 0
    } else {
      console.log('API调用失败:', response)
      showcases.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取作品列表失败:', error)
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
    currentPage.value = page
    router.push({ query: { ...route.query, page } })
  }
}

const jumpToPage = () => {
  if (jumpPage.value && jumpPage.value >= 1 && jumpPage.value <= totalPages.value) {
    goToPage(jumpPage.value)
    jumpPage.value = ''
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const handleImageError = (event) => {
  event.target.src = `/images/show${Math.floor(Math.random() * 3) + 1}.png`
}

// 监听路由变化
watch(() => route.query.page, (newPage) => {
  currentPage.value = parseInt(newPage) || 1
}, { immediate: true })

// 监听页码变化
watch(currentPage, () => {
  fetchShowcases()
})

// 生命周期
onMounted(() => {
  fetchShowcases()
})
</script>

<style scoped>
.submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #007bff;
  color: #fff;
  padding: 12px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}

.submit-btn:hover {
  background: #0056b3;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
  color: #fff;
  text-decoration: none;
}

.submit-icon {
  font-size: 18px;
}

.loading-state {
  min-height: 300px;
  flex-direction: column;
  gap: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  min-height: 400px;
}

.empty-content {
  text-align: center;
}

.empty-image {
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
  opacity: 0.6;
}

.card-stats {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 14px;
  color: #666;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-item .iconfont {
  font-size: 16px;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-input {
  width: 60px;
  text-align: center;
  margin: 0 8px;
}

.card-title a {
  color: #333;
  text-decoration: none;
  transition: color 0.3s;
}

.card-title a:hover {
  color: #007bff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .submit-btn {
    padding: 10px 16px;
    font-size: 14px;
  }
}
</style>
