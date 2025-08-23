<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="title-icon">✏️</i>
          发表新讨论
        </h2>
        <button class="btn-close" @click="closeModal">
          <i class="icon">✕</i>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="post-form">
        <div class="form-group">
          <label for="category" class="form-label">讨论分类</label>
          <select 
            v-model="formData.category_id" 
            id="category"
            class="form-select"
            required
          >
            <option value="">请选择分类</option>
            <option 
              v-for="category in categories" 
              :key="category.uuid"
              :value="category.id"
            >
              <span v-if="category.icon">{{ category.icon }}</span>
              {{ category.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="title" class="form-label">讨论标题</label>
          <input 
            v-model="formData.title"
            type="text" 
            id="title"
            class="form-input"
            placeholder="请输入讨论标题..."
            maxlength="200"
            required
          >
          <div class="char-count">{{ formData.title.length }}/200</div>
        </div>

        <div class="form-group">
          <label for="content" class="form-label">讨论内容</label>
          <div class="editor-toolbar">
            <button type="button" class="toolbar-btn" @click="insertFormat('**', '**')" title="加粗">
              <strong>B</strong>
            </button>
            <button type="button" class="toolbar-btn" @click="insertFormat('*', '*')" title="斜体">
              <em>I</em>
            </button>
            <button type="button" class="toolbar-btn" @click="insertFormat('`', '`')" title="代码">
              <code>&lt;/&gt;</code>
            </button>
            <button type="button" class="toolbar-btn" @click="insertFormat('> ', '')" title="引用">
              <span>"</span>
            </button>
            <button type="button" class="toolbar-btn" @click="insertFormat('- ', '')" title="列表">
              <span>☰</span>
            </button>
          </div>
          <textarea 
            ref="contentTextarea"
            v-model="formData.content"
            id="content"
            class="form-textarea"
            placeholder="请详细描述你的问题或想法..."
            rows="8"
            required
          ></textarea>
          <div class="editor-tips">
            支持Markdown语法：**粗体** *斜体* `代码` > 引用
          </div>
        </div>

        <div class="form-actions">
          <button type="button" @click="closeModal" class="btn-cancel">
            取消
          </button>
          <button type="submit" :disabled="submitting" class="btn-submit">
            <i v-if="submitting" class="loading-icon">⟳</i>
            {{ submitting ? '发布中...' : '发布讨论' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { forumApi } from '../../api/forum'

const authStore = useAuthStore()

// Props
const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  }
})

// Events
const emit = defineEmits(['close', 'created'])

// 响应式数据
const contentTextarea = ref(null)
const submitting = ref(false)

const formData = reactive({
  category_id: '',
  title: '',
  content: ''
})

// 关闭弹窗
const closeModal = () => {
  emit('close')
}

// 插入格式化文本
const insertFormat = (prefix, suffix) => {
  const textarea = contentTextarea.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = textarea.value.substring(start, end)
  
  const beforeText = textarea.value.substring(0, start)
  const afterText = textarea.value.substring(end)
  
  const newText = beforeText + prefix + selectedText + suffix + afterText
  formData.content = newText
  
  // 重新设置光标位置
  setTimeout(() => {
    const newCursorPos = start + prefix.length + selectedText.length + suffix.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
    textarea.focus()
  }, 0)
}

// 表单验证
const validateForm = () => {
  console.log('验证表单 - category_id:', formData.category_id, 'type:', typeof formData.category_id)
  if (!formData.category_id || formData.category_id === '' || formData.category_id === null || formData.category_id === undefined) {
    alert('请选择讨论分类')
    return false
  }
  
  if (!formData.title.trim()) {
    alert('请输入讨论标题')
    return false
  }
  
  if (formData.title.length > 200) {
    alert('标题长度不能超过200个字符')
    return false
  }
  
  if (!formData.content.trim()) {
    alert('请输入讨论内容')
    return false
  }
  
  return true
}

// 提交表单
const handleSubmit = async () => {
  if (!validateForm()) return
  
  // 检查用户登录状态
  if (!authStore.isAuthenticated) {
    alert('请先登录后再发表讨论')
    authStore.showLoginModal()
    return
  }
  
  submitting.value = true
  
  try {
    const postData = {
      category_id: parseInt(formData.category_id),
      title: formData.title.trim(),
      content: formData.content.trim()
    }
    
    await forumApi.post.createPost(postData)
    
    // 成功提示
    alert('讨论发表成功！')
    
    // 通知父组件
    emit('created')
    
    // 关闭弹窗
    closeModal()
  } catch (error) {
    console.error('发表讨论失败:', error)
    
    if (error.response?.status === 401) {
      alert('登录已过期，请重新登录')
      authStore.showLoginModal()
    } else if (error.response?.status === 400) {
      alert(error.response.data?.message || '发表失败，请检查输入内容')
    } else {
      alert('发表讨论失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

// 组件挂载时聚焦标题输入框
onMounted(() => {
  const titleInput = document.getElementById('title')
  if (titleInput) {
    titleInput.focus()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: #ffffff;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e3e5e8;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.75rem;
  font-weight: 600;
  color: #2c2f33;
  margin: 0;
}

.title-icon {
  font-size: 1.375rem;
}

.btn-close {
  background: none;
  border: none;
  color: #72767d;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.btn-close:hover {
  background: #f2f3f5;
  color: #2c2f33;
}

.post-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 600;
  color: #2c2f33;
  margin-bottom: 0.5rem;
  font-size: 1.375rem;
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e3e5e8;
  border-radius: 6px;
  font-size: 1.375rem;
  transition: all 0.3s ease;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #5865f2;
  box-shadow: 0 0 0 2px rgba(88, 101, 242, 0.1);
}

.char-count {
  text-align: right;
  font-size: 1.125rem;
  color: #72767d;
  margin-top: 0.25rem;
}

.editor-toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e3e5e8;
}

.toolbar-btn {
  background: none;
  border: none;
  padding: 0.375rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  color: #4f545c;
  transition: all 0.3s ease;
  min-width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toolbar-btn:hover {
  background: #e3e5e8;
  color: #2c2f33;
}

.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e3e5e8;
  border-radius: 6px;
  font-size: 1.375rem;
  font-family: inherit;
  resize: vertical;
  min-height: 200px;
  transition: all 0.3s ease;
}

.form-textarea:focus {
  outline: none;
  border-color: #5865f2;
  box-shadow: 0 0 0 2px rgba(88, 101, 242, 0.1);
}

.editor-tips {
  font-size: 1.125rem;
  color: #72767d;
  margin-top: 0.5rem;
  font-style: italic;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e3e5e8;
}

.btn-cancel,
.btn-submit {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  border-color: #d1d5db;
}

.btn-submit {
  background: linear-gradient(135deg, #5865f2, #7289da);
  border: none;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #4752c4, #677bc4);
  transform: translateY(-1px);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .modal-content {
    margin: 0;
    border-radius: 0;
    max-height: 100vh;
  }
  
  .modal-header,
  .post-form {
    padding: 1rem;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn-cancel,
  .btn-submit {
    width: 100%;
    justify-content: center;
    flex-shrink: 1;
  }
  
  .editor-toolbar {
    flex-wrap: wrap;
  }
}
</style>