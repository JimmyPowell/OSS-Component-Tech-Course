<template>
  <div class="page">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="breadcrumb-nav">
          <router-link to="/showcase" class="breadcrumb-link">作品展示</router-link>
          <span class="breadcrumb-separator">></span>
          <span class="breadcrumb-current">提交作品</span>
        </div>
        <h1 class="page-title">提交我的作品</h1>
        <p class="page-subtitle">分享您的优秀作品，让更多人看到您的创意</p>
      </div>

      <!-- 提交表单 -->
      <div class="submit-form-container">
        <form @submit.prevent="handleSubmit" class="showcase-form">
          <!-- 作品名称 -->
          <div class="form-group">
            <label class="form-label required">作品名称</label>
            <input 
              type="text" 
              v-model="form.name"
              class="form-control"
              placeholder="请输入作品名称"
              maxlength="255"
              :class="{ 'error': errors.name }"
              @blur="validateField('name')"
            >
            <div class="char-counter">{{ form.name.length }}/255</div>
            <div v-if="errors.name" class="error-message">{{ errors.name }}</div>
          </div>

          <!-- 作品封面 -->
          <div class="form-group">
            <label class="form-label">作品封面</label>
            <div class="upload-area">
              <div v-if="!form.avatar_url" class="upload-placeholder" @click="triggerUpload">
                <div class="upload-icon">📁</div>
                <div class="upload-text">
                  <p>点击上传作品封面</p>
                  <p class="upload-hint">支持 JPG、PNG 格式，建议尺寸 800x600，不超过 5MB</p>
                </div>
              </div>
              <div v-else class="uploaded-image">
                <img :src="form.avatar_url" alt="作品封面" class="preview-image">
                <div class="image-overlay">
                  <button type="button" @click="triggerUpload" class="btn-overlay">重新上传</button>
                  <button type="button" @click="removeImage" class="btn-overlay btn-remove">删除</button>
                </div>
              </div>
              <input 
                ref="fileInput" 
                type="file" 
                accept="image/*"
                style="display: none"
                @change="handleFileChange"
              >
            </div>
            <div v-if="uploading" class="upload-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
              </div>
              <span class="progress-text">上传中 {{ uploadProgress }}%</span>
            </div>
            <div v-if="errors.avatar_url" class="error-message">{{ errors.avatar_url }}</div>
          </div>

          <!-- 作品简介 -->
          <div class="form-group">
            <label class="form-label">作品简介</label>
            <textarea 
              v-model="form.summary"
              class="form-control"
              placeholder="请简要介绍您的作品亮点和特色"
              rows="3"
              maxlength="512"
              :class="{ 'error': errors.summary }"
              @blur="validateField('summary')"
            ></textarea>
            <div class="char-counter">{{ form.summary.length }}/512</div>
            <div v-if="errors.summary" class="error-message">{{ errors.summary }}</div>
          </div>

          <!-- 详细介绍 -->
          <div class="form-group">
            <label class="form-label">详细介绍</label>
            <textarea 
              v-model="form.detailed_introduction"
              class="form-control detailed-textarea"
              placeholder="请详细描述您的作品：&#10;- 项目背景和目标&#10;- 使用的技术栈&#10;- 实现的功能特性&#10;- 遇到的挑战和解决方案&#10;- 项目收获和反思"
              rows="8"
              :class="{ 'error': errors.detailed_introduction }"
              @blur="validateField('detailed_introduction')"
            ></textarea>
            <div class="form-hint">支持链接自动识别，粘贴的网址将自动转换为可点击链接</div>
            <div v-if="errors.detailed_introduction" class="error-message">{{ errors.detailed_introduction }}</div>
          </div>

          <!-- 项目链接 -->
          <div class="form-group">
            <label class="form-label">项目链接</label>
            <input 
              type="url" 
              v-model="form.project_url"
              class="form-control"
              placeholder="https://github.com/username/project 或 项目演示地址"
              :class="{ 'error': errors.project_url }"
              @blur="validateField('project_url')"
            >
            <div class="form-hint">可以是 GitHub 仓库、在线演示地址等</div>
            <div v-if="errors.project_url" class="error-message">{{ errors.project_url }}</div>
          </div>

          <!-- 作品标签 -->
          <div class="form-group">
            <label class="form-label">作品标签</label>
            <div class="tag-input-container">
              <div class="selected-tags">
                <span 
                  v-for="(tag, index) in form.tags" 
                  :key="index" 
                  class="tag-item"
                >
                  {{ tag }}
                  <button type="button" @click="removeTag(index)" class="tag-remove">×</button>
                </span>
              </div>
              <input 
                type="text" 
                v-model="newTag"
                class="tag-input"
                placeholder="输入标签后按回车添加"
                @keydown.enter.prevent="addTag"
                @keydown.comma.prevent="addTag"
                maxlength="20"
              >
            </div>
            <div class="form-hint">推荐标签：前端、后端、移动端、机器学习、数据分析、UI设计等</div>
            <div v-if="errors.tags" class="error-message">{{ errors.tags }}</div>
          </div>

          <!-- 提交按钮组 -->
          <div class="form-actions">
            <button 
              type="button" 
              @click="saveAsDraft"
              class="btn btn-secondary"
              :disabled="submitting"
            >
              <span v-if="submitting && submitType === 'draft'">保存中...</span>
              <span v-else>保存草稿</span>
            </button>
            <button 
              type="submit"
              class="btn btn-primary"
              :disabled="submitting || !isFormValid"
            >
              <span v-if="submitting && submitType === 'submit'">提交中...</span>
              <span v-else>提交审核</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showcaseAPI } from '@/api/showcase.js'
import { qiniuAPI } from '@/api/qiniu.js'

const router = useRouter()

// 表单数据
const form = reactive({
  name: '',
  summary: '',
  detailed_introduction: '',
  avatar_url: '',
  project_url: '',
  tags: []
})

// 表单验证错误
const errors = reactive({
  name: '',
  summary: '',
  detailed_introduction: '',
  avatar_url: '',
  project_url: '',
  tags: ''
})

// 其他状态
const submitting = ref(false)
const submitType = ref('')
const uploading = ref(false)
const uploadProgress = ref(0)
const newTag = ref('')
const fileInput = ref(null)

// 表单验证规则
const validateField = (field) => {
  errors[field] = ''
  
  switch (field) {
    case 'name':
      if (!form.name.trim()) {
        errors.name = '作品名称不能为空'
      } else if (form.name.length > 255) {
        errors.name = '作品名称不能超过255个字符'
      }
      break
    case 'summary':
      if (form.summary && form.summary.length > 512) {
        errors.summary = '作品简介不能超过512个字符'
      }
      break
    case 'project_url':
      if (form.project_url && !isValidUrl(form.project_url)) {
        errors.project_url = '请输入有效的URL地址'
      }
      break
  }
}

// 验证URL格式
const isValidUrl = (url) => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// 表单整体验证
const isFormValid = computed(() => {
  return form.name.trim() && 
         !Object.values(errors).some(error => error !== '') &&
         !submitting.value
})

// 触发文件上传
const triggerUpload = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 文件类型验证
  if (!file.type.startsWith('image/')) {
    errors.avatar_url = '请选择图片文件'
    return
  }

  // 文件大小验证
  if (file.size > 5 * 1024 * 1024) {
    errors.avatar_url = '图片大小不能超过5MB'
    return
  }

  // 上传文件
  await uploadFile(file)
}

// 上传文件到七牛云
const uploadFile = async (file) => {
  try {
    uploading.value = true
    uploadProgress.value = 0
    errors.avatar_url = ''

    // 生成文件key
    const fileKey = qiniuAPI.generateFileKey('showcase/avatar', file.name)
    
    // 获取上传token
    const tokenResponse = await qiniuAPI.getUploadToken(fileKey, `作品封面上传: ${file.name}`)
    
    if (!tokenResponse.data || tokenResponse.data.code !== 201) {
      throw new Error(tokenResponse.data?.message || '获取上传凭证失败')
    }
    
    const tokenInfo = tokenResponse.data.data
    
    // 上传文件到七牛云
    const uploadResult = await qiniuAPI.uploadFile(
      file, 
      tokenInfo.token, 
      fileKey, 
      tokenInfo.upload_domain,
      (progress) => {
        uploadProgress.value = progress
      }
    )
    
    // 构建完整的文件URL
    form.avatar_url = `${tokenInfo.download_domain}/${uploadResult.key}`
    
  } catch (error) {
    console.error('文件上传失败:', error)
    errors.avatar_url = error.message || '文件上传失败，请重试'
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

// 删除图片
const removeImage = () => {
  form.avatar_url = ''
}

// 添加标签
const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !form.tags.includes(tag) && form.tags.length < 10) {
    form.tags.push(tag)
    newTag.value = ''
  }
}

// 删除标签
const removeTag = (index) => {
  form.tags.splice(index, 1)
}

// 保存草稿
const saveAsDraft = async () => {
  if (!form.name.trim()) {
    errors.name = '作品名称不能为空'
    return
  }

  await submitForm('draft')
}

// 提交审核
const handleSubmit = async () => {
  // 验证所有字段
  Object.keys(form).forEach(field => {
    validateField(field)
  })

  if (!isFormValid.value) return

  await submitForm('pending')
}

// 提交表单
const submitForm = async (status) => {
  try {
    submitting.value = true
    submitType.value = status === 'draft' ? 'draft' : 'submit'

    const submitData = {
      ...form,
      status: status
    }

    const response = await showcaseAPI.createShowcase(submitData)

    if (response.data?.code === 200 || response.success) {
      const message = status === 'draft' ? '草稿保存成功' : '作品提交成功，请等待审核'
      
      // 显示成功消息
      alert(message)
      
      // 跳转回作品页面
      router.push('/showcase')
    } else {
      throw new Error(response.data?.message || response.message || '提交失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    alert('提交失败：' + (error.message || '请稍后重试'))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  // 组件初始化
})
</script>

<style scoped>
.page {
  background: #ffffff;
  min-height: 100vh;
  padding: 20px 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 页面头部 */
.page-header {
  margin-bottom: 40px;
}

.breadcrumb-nav {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
  gap: 8px;
}

.breadcrumb-link {
  color: #666;
  text-decoration: none;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: #007bff;
}

.breadcrumb-separator {
  color: #ccc;
}

.breadcrumb-current {
  color: #333;
  font-weight: 500;
}

.page-title {
  font-size: 32px;
  color: #333;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 表单容器 */
.submit-form-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.showcase-form {
  width: 100%;
}

/* 表单组 */
.form-group {
  margin-bottom: 32px;
}

.form-label {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.form-label.required::after {
  content: " *";
  color: #e74c3c;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s ease;
  background: #fff;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
}

.form-control.error {
  border-color: #e74c3c;
}

.detailed-textarea {
  font-family: inherit;
  resize: vertical;
  min-height: 200px;
}

/* 字符计数 */
.char-counter {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

/* 表单提示 */
.form-hint {
  font-size: 14px;
  color: #666;
  margin-top: 6px;
  line-height: 1.4;
}

/* 错误信息 */
.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 6px;
}

/* 上传区域 */
.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.upload-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.upload-placeholder:hover {
  background-color: #f8f9fa;
}

.upload-icon {
  font-size: 48px;
  margin-right: 20px;
}

.upload-text p {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.upload-hint {
  font-size: 14px;
  color: #666;
}

.uploaded-image {
  position: relative;
  display: inline-block;
}

.preview-image {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
  display: block;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.uploaded-image:hover .image-overlay {
  opacity: 1;
}

.btn-overlay {
  background: #fff;
  color: #333;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.btn-overlay:hover {
  background: #f8f9fa;
}

.btn-remove {
  background: #e74c3c;
  color: #fff;
}

.btn-remove:hover {
  background: #c0392b;
}

/* 上传进度 */
.upload-progress {
  padding: 16px 0;
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e1e5e9;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: #007bff;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #666;
}

/* 标签输入 */
.tag-input-container {
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  padding: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  min-height: 50px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  background: #007bff;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag-remove {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.tag-remove:hover {
  background: rgba(255, 255, 255, 0.2);
}

.tag-input {
  border: none;
  outline: none;
  flex: 1;
  min-width: 120px;
  padding: 4px;
  font-size: 16px;
}

/* 按钮组 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid #e1e5e9;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #6c757d;
  color: #fff;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }

  .submit-form-container {
    padding: 24px 20px;
  }

  .page-title {
    font-size: 28px;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .upload-placeholder {
    padding: 24px 16px;
    flex-direction: column;
    text-align: center;
  }

  .upload-icon {
    margin-right: 0;
    margin-bottom: 16px;
  }
}
</style>