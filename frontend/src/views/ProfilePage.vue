<template>
  <div class="page">
    <div class="container">
      <div class="profile-layout">
        <!-- 左侧头像区域 -->
        <div class="profile-sidebar">
          <div class="avatar-section">
            <div class="avatar-container" :class="{ 'editable': isEditing }" @click="handleAvatarClick">
              <img 
                v-if="userData.avatar_url" 
                :src="userData.avatar_url" 
                :alt="userData.username"
                class="profile-avatar"
              />
              <div v-else class="profile-avatar default-avatar">
                {{ userInitial }}
              </div>
              <div v-if="isEditing" class="avatar-overlay">
                <i class="iconfont icon-camera"></i>
                <span>更换头像</span>
              </div>
            </div>
            <div class="user-name">{{ displayName }}</div>
            <div class="user-role">{{ userRoleDisplay }}</div>
          </div>
        </div>

        <!-- 右侧信息区域 -->
        <div class="profile-main">
          <div class="profile-header">
            <h1>个人资料</h1>
            <div class="profile-actions">
              <button v-if="!isEditing" @click="startEditing" class="btn btn-primary">
                <i class="iconfont icon-edit"></i>编辑资料
              </button>
              <div v-else class="edit-actions">
                <button @click="saveProfile" class="btn btn-primary" :disabled="saving">
                  {{ saving ? '保存中...' : '保存' }}
                </button>
                <button @click="cancelEditing" class="btn btn-secondary">取消</button>
              </div>
            </div>
          </div>

          <!-- 基本信息展示/编辑 -->
          <div class="profile-content">
            <div class="info-section">
              <h3>基本信息</h3>
              <div class="info-grid">
                <!-- 用户名 -->
                <div class="info-item">
                  <label>用户名</label>
                  <div v-if="!isEditing" class="info-value">
                    {{ userData.username || '-' }}
                  </div>
                  <input v-else v-model="formData.username" class="form-control" placeholder="请输入用户名" />
                </div>

                <!-- 真实姓名 -->
                <div class="info-item">
                  <label>真实姓名</label>
                  <div v-if="!isEditing" class="info-value">
                    {{ userData.real_name || '-' }}
                  </div>
                  <input v-else v-model="formData.real_name" class="form-control" placeholder="请输入真实姓名" />
                </div>

                <!-- 学生ID -->
                <div class="info-item">
                  <label>学生ID</label>
                  <div v-if="!isEditing" class="info-value">
                    {{ userData.student_id || '-' }}
                  </div>
                  <input v-else v-model="formData.student_id" class="form-control" placeholder="请输入学生ID" />
                </div>

                <!-- 班级 -->
                <div class="info-item">
                  <label>班级</label>
                  <div v-if="!isEditing" class="info-value">
                    {{ userData.student_class || '-' }}
                  </div>
                  <input v-else v-model="formData.student_class" class="form-control" placeholder="请输入班级" />
                </div>

                <!-- 联系方式 -->
                <div class="info-item">
                  <label>联系方式</label>
                  <div v-if="!isEditing" class="info-value">
                    {{ userData.phone_number || '-' }}
                  </div>
                  <input v-else v-model="formData.phone_number" class="form-control" placeholder="请输入联系方式" />
                </div>

                <!-- 学校 -->
                <div class="info-item">
                  <label>学校</label>
                  <div v-if="!isEditing" class="info-value">
                    {{ userData.school || '-' }}
                  </div>
                  <input v-else v-model="formData.school" class="form-control" placeholder="请输入学校" />
                </div>

                <!-- 邮箱 -->
                <div class="info-item">
                  <label>邮箱</label>
                  <div class="info-value">
                    {{ userData.email || '-' }}
                  </div>
                </div>

                <!-- 头像链接 (仅编辑模式显示) -->
                <div v-if="isEditing" class="info-item full-width">
                  <label>头像链接</label>
                  <input v-model="formData.avatar_url" class="form-control" placeholder="请输入头像URL" />
                </div>
              </div>
            </div>

            <!-- 密码修改区域 -->
            <div class="info-section">
              <div class="section-header">
                <h3>密码设置</h3>
                <button 
                  v-if="!showPasswordChange" 
                  @click="showPasswordChange = true" 
                  class="btn btn-outline"
                >
                  修改密码
                </button>
              </div>
              
              <div v-if="showPasswordChange" class="password-form">
                <div class="info-grid">
                  <div class="info-item">
                    <label>当前密码</label>
                    <input 
                      type="password" 
                      v-model="passwordData.old_password" 
                      class="form-control"
                      placeholder="请输入当前密码"
                    />
                  </div>
                  <div class="info-item">
                    <label>新密码</label>
                    <input 
                      type="password" 
                      v-model="passwordData.new_password" 
                      class="form-control"
                      placeholder="请输入新密码"
                    />
                  </div>
                  <div class="info-item">
                    <label>确认新密码</label>
                    <input 
                      type="password" 
                      v-model="passwordData.confirm_password" 
                      class="form-control"
                      placeholder="请再次输入新密码"
                    />
                  </div>
                </div>
                <div class="password-actions">
                  <button @click="changePassword" class="btn btn-primary" :disabled="changingPassword">
                    {{ changingPassword ? '修改中...' : '确认修改' }}
                  </button>
                  <button @click="cancelPasswordChange" class="btn btn-secondary">取消</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 头像裁剪组件 -->
    <AvatarCropper
      v-if="showAvatarCropper"
      :show="showAvatarCropper"
      :imageFile="selectedImageFile"
      @close="closeAvatarCropper"
      @success="handleAvatarUploadSuccess"
      @error="handleAvatarUploadError"
    />

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileSelect"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';
import AvatarCropper from '../components/AvatarCropper.vue';

const authStore = useAuthStore();

// 状态控制
const isEditing = ref(false);
const saving = ref(false);
const changingPassword = ref(false);
const showPasswordChange = ref(false);

// 头像相关状态
const showAvatarCropper = ref(false);
const selectedImageFile = ref(null);
const fileInput = ref(null);

// 用户数据
const userData = ref({});

// 编辑表单数据
const formData = ref({
  username: '',
  real_name: '',
  student_id: '',
  student_class: '',
  phone_number: '',
  school: '',
  avatar_url: ''
});

// 密码数据
const passwordData = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
});

// 计算属性
const displayName = computed(() => {
  if (userData.value.real_name && userData.value.real_name.trim()) {
    return userData.value.real_name;
  }
  return userData.value.username || '用户';
});

const userInitial = computed(() => {
  const name = displayName.value;
  return name ? name.charAt(0).toUpperCase() : '?';
});

const userRoleDisplay = computed(() => {
  const role = userData.value.role || 'user';
  switch(role) {
    case 'admin': return '超级管理员';
    case 'manager': return '管理员';
    case 'teacher': return '教师';
    default: return '学生';
  }
});

// 获取用户信息
const loadUserData = async () => {
  try {
    // 从auth store获取已经登录的用户信息
    if (authStore.user) {
      userData.value = authStore.user;
      console.log('Using user data from auth store:', userData.value);
      return;
    }

    // 如果store中没有，尝试从API获取
    const token = localStorage.getItem('accessToken'); // 使用正确的key
    if (!token) {
      console.log('No access token found');
      return;
    }

    console.log('Loading user data from API...');
    const response = await axios.get('http://localhost:8000/api/v1/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    console.log('User data response:', response.data);
    
    if (response.data.code === 200) {
      userData.value = response.data.data;
      console.log('User data set:', userData.value);
    } else {
      console.error('API returned error:', response.data);
      alert('获取用户信息失败');
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
    alert('获取用户信息失败');
  }
};

// 开始编辑
const startEditing = () => {
  isEditing.value = true;
  // 将当前数据复制到表单
  formData.value = {
    username: userData.value.username || '',
    real_name: userData.value.real_name || '',
    student_id: userData.value.student_id || '',
    student_class: userData.value.student_class || '',
    phone_number: userData.value.phone_number || '',
    school: userData.value.school || '',
    avatar_url: userData.value.avatar_url || ''
  };
};

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false;
  formData.value = {};
};

// 保存资料
const saveProfile = async () => {
  saving.value = true;
  try {
    const token = localStorage.getItem('accessToken'); // 使用正确的key
    if (!token) {
      alert('请先登录');
      return;
    }

    // 过滤空值
    const updateData = {};
    Object.keys(formData.value).forEach(key => {
      if (formData.value[key] && formData.value[key].trim()) {
        updateData[key] = formData.value[key].trim();
      }
    });

    const response = await axios.put('http://localhost:8000/api/v1/auth/profile', updateData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.data.code === 200) {
      alert('个人资料更新成功！');
      // 更新数据并退出编辑模式
      userData.value = response.data.data;
      authStore.user = response.data.data;
      isEditing.value = false;
    } else {
      alert(response.data.message || '更新失败');
    }
  } catch (error) {
    console.error('更新用户资料失败:', error);
    const errorMessage = error.response?.data?.message || '更新失败，请稍后重试';
    alert(errorMessage);
  } finally {
    saving.value = false;
  }
};

// 修改密码
const changePassword = async () => {
  if (passwordData.value.new_password !== passwordData.value.confirm_password) {
    alert('两次输入的密码不一致');
    return;
  }

  if (passwordData.value.new_password.length < 6) {
    alert('新密码长度至少6位');
    return;
  }

  changingPassword.value = true;
  try {
    const token = localStorage.getItem('accessToken'); // 使用正确的key
    const refreshToken = localStorage.getItem('refreshToken'); // 使用正确的key
    
    if (!token || !refreshToken) {
      alert('请先登录');
      return;
    }

    const response = await axios.post('http://localhost:8000/api/v1/auth/change-password', {
      old_password: passwordData.value.old_password,
      new_password: passwordData.value.new_password,
      refresh_token: refreshToken
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.data.code === 200) {
      alert('密码修改成功！');
      cancelPasswordChange();
    } else {
      alert(response.data.message || '密码修改失败');
    }
  } catch (error) {
    console.error('修改密码失败:', error);
    const errorMessage = error.response?.data?.message || '密码修改失败，请稍后重试';
    alert(errorMessage);
  } finally {
    changingPassword.value = false;
  }
};

// 取消密码修改
const cancelPasswordChange = () => {
  showPasswordChange.value = false;
  passwordData.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  };
};

// 头像相关方法
const handleAvatarClick = () => {
  if (!isEditing.value) return;
  
  // 触发文件选择
  fileInput.value?.click();
};

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件');
    return;
  }
  
  // 验证文件大小 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过5MB');
    return;
  }
  
  // 设置选中的文件并显示裁剪组件
  selectedImageFile.value = file;
  showAvatarCropper.value = true;
  
  // 清空文件输入，以便下次选择同一文件时也能触发change事件
  event.target.value = '';
};

const closeAvatarCropper = () => {
  showAvatarCropper.value = false;
  selectedImageFile.value = null;
};

const handleAvatarUploadSuccess = async (imageUrl) => {
  try {
    // 更新formData中的头像URL
    if (isEditing.value) {
      formData.value.avatar_url = imageUrl;
    }
    
    // 同时更新userData显示
    userData.value.avatar_url = imageUrl;
    
    // 可选：自动保存头像更改
    await saveAvatarOnly(imageUrl);
    
    alert('头像上传成功！');
  } catch (error) {
    console.error('保存头像失败:', error);
    alert('头像保存失败，请重试');
  }
};

const handleAvatarUploadError = (errorMessage) => {
  alert(errorMessage);
};

// 仅保存头像
const saveAvatarOnly = async (avatarUrl) => {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      throw new Error('请先登录');
    }

    const response = await axios.put('http://localhost:8000/api/v1/auth/profile', {
      avatar_url: avatarUrl
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.data.code === 200) {
      // 更新auth store中的用户信息
      authStore.user = response.data.data;
      userData.value = response.data.data;
    } else {
      throw new Error(response.data.message || '保存失败');
    }
  } catch (error) {
    console.error('保存头像失败:', error);
    throw error;
  }
};

onMounted(() => {
  loadUserData();
});
</script>

<style scoped>
.page {
  background-color: #f8f9fa;
  min-height: 100vh;
  padding-top: 100px;
  padding-bottom: 50px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

.profile-layout {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

/* 左侧头像区域 */
.profile-sidebar {
  flex: 0 0 300px;
}

.avatar-section {
  background: white;
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.avatar-section:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.avatar-container {
  margin-bottom: 20px;
  position: relative;
  display: inline-block;
}

.avatar-container.editable {
  cursor: pointer;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #f0f0f0;
  transition: transform 0.3s ease;
}

.profile-avatar:hover {
  transform: scale(1.05);
}

.default-avatar {
  background: linear-gradient(135deg, #545ae7 0%, #6c5ce7 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: bold;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: all 0.3s ease;
  font-size: 12px;
}

.avatar-container.editable:hover .avatar-overlay {
  opacity: 1;
}

.avatar-overlay i {
  font-size: 20px;
  margin-bottom: 4px;
}

.avatar-overlay span {
  font-size: 11px;
  font-weight: 600;
  text-align: center;
  line-height: 1.2;
}

.user-name {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
}

.user-role {
  color: #6c757d;
  font-size: 16px;
  padding: 4px 12px;
  background: #e9ecef;
  border-radius: 12px;
  display: inline-block;
}

/* 右侧主要内容区域 */
.profile-main {
  flex: 1;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px 40px;
  border-bottom: 1px solid #e9ecef;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.profile-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

.profile-actions {
  display: flex;
  gap: 12px;
}

.edit-actions {
  display: flex;
  gap: 12px;
}

/* 内容区域 */
.profile-content {
  padding: 40px;
}

.info-section {
  margin-bottom: 40px;
}

.info-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e9ecef;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 16px;
  color: #2c3e50;
  padding: 12px 0;
  border-bottom: 1px solid #e9ecef;
  min-height: 20px;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.form-control:focus {
  outline: none;
  border-color: #545ae7;
  background: white;
  box-shadow: 0 0 0 3px rgba(84, 90, 231, 0.1);
}

/* 按钮样式 */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-align: center;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #545ae7 0%, #6c5ce7 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(84, 90, 231, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.btn-outline {
  background: transparent;
  color: #545ae7;
  border: 2px solid #545ae7;
}

.btn-outline:hover {
  background: #545ae7;
  color: white;
}

/* 密码表单 */
.password-form {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.password-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-layout {
    flex-direction: column;
    gap: 20px;
  }

  .profile-sidebar {
    flex: none;
  }

  .profile-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
    padding: 20px;
  }

  .profile-content {
    padding: 20px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .profile-actions, .edit-actions, .password-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 10px;
  }

  .profile-avatar {
    width: 100px;
    height: 100px;
  }

  .default-avatar {
    font-size: 40px;
  }

  .user-name {
    font-size: 20px;
  }

  .profile-header h1 {
    font-size: 24px;
  }
}
</style>