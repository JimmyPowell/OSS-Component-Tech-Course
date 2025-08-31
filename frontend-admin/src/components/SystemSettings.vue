<script setup>
import { ref, reactive } from 'vue';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import request from '../utils/request';

const router = useRouter();
const loading = ref(false);

const systemForm = reactive({
  aiConfig: {
    provider: '1',
    baseUrl: '',
    apiKey: ''
  },
  storageConfig: {
    bucketName: '',
    domainName: '',
    akKey: '',
    skKey: ''
  }
});

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
});

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码' }
  ],
  new_password: [
    { required: true, message: '请输入新密码' },
    { min: 6, message: '密码长度至少6位' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码' },
    {
      validator: (rule, value) => {
        if (value && value !== passwordForm.new_password) {
          return Promise.reject('两次输入的密码不一致');
        }
        return Promise.resolve();
      }
    }
  ]
};

const handleSave = () => {
  message.success('系统设置保存成功');
};

const handleReset = () => {
  systemForm.aiConfig.provider = '1';
  systemForm.aiConfig.baseUrl = '';
  systemForm.aiConfig.apiKey = '';
  systemForm.storageConfig.bucketName = '';
  systemForm.storageConfig.domainName = '';
  systemForm.storageConfig.akKey = '';
  systemForm.storageConfig.skKey = '';
  message.info('已重置为默认值');
};

const handleChangePassword = async () => {
  try {
    loading.value = true;
    
    // 获取refresh_token
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      message.error('登录状态已过期，请重新登录');
      router.push('/login');
      return;
    }
    
    console.log('发送密码修改请求:', {
      old_password: passwordForm.old_password ? '***' : '',
      new_password: passwordForm.new_password ? '***' : '',
      refresh_token: refreshToken ? '***' : ''
    });
    
    const response = await request.post('http://localhost:8000/api/v1/auth/change-password', {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
      refresh_token: refreshToken
    });
    
    console.log('密码修改响应:', response.data);
    
    if (response.data.code === 200) {
      message.success('密码修改成功，请重新登录');
      
      // 清除token
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // 跳转到登录页
      router.push('/login');
    } else {
      console.error('密码修改失败，响应:', response.data);
      message.error(response.data.message || '密码修改失败');
    }
  } catch (error) {
    console.error('密码修改请求异常:', error);
    console.error('错误响应:', error.response?.data);
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message;
    message.error('密码修改失败：' + errorMsg);
  } finally {
    loading.value = false;
  }
};

const resetPasswordForm = () => {
  passwordForm.old_password = '';
  passwordForm.new_password = '';
  passwordForm.confirm_password = '';
};
</script>

<template>
  <div class="system-settings">
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-subtitle">管理系统核心配置参数</p>
    </div>

    <div class="settings-content">
      <!-- AI调用配置 -->
      <div class="settings-section">
        <div class="section-header">
          <h2 class="section-title">AI调用</h2>
        </div>
        <div class="section-content">
          <a-form :model="systemForm.aiConfig" layout="vertical">
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="模型提供商">
                  <a-select v-model:value="systemForm.aiConfig.provider" class="provider-select">
                    <a-select-option value="1">1</a-select-option>
                    <a-select-option value="2">2</a-select-option>
                    <a-select-option value="3">3</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="24">
                <a-form-item>
                  <template #label>
                    <div class="label-with-checkbox">
                      <a-checkbox v-model:checked="systemForm.aiConfig.useBaseUrl">
                        启用BASE_URL
                      </a-checkbox>
                    </div>
                  </template>
                  <a-input 
                    v-model:value="systemForm.aiConfig.baseUrl" 
                    placeholder="请输入"
                    class="config-input"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="24">
                <a-form-item label="API_KEY">
                  <a-input 
                    v-model:value="systemForm.aiConfig.apiKey" 
                    placeholder="请输入"
                    type="password"
                    class="config-input"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </div>
      </div>

      <!-- 对象存储配置 -->
      <div class="settings-section">
        <div class="section-header">
          <h2 class="section-title">对象存储</h2>
        </div>
        <div class="section-content">
          <a-form :model="systemForm.storageConfig" layout="vertical">
            <a-row :gutter="24">
              <a-col :span="24">
                <a-form-item label="存储桶名称">
                  <a-input 
                    v-model:value="systemForm.storageConfig.bucketName" 
                    placeholder="请输入"
                    class="config-input"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="24">
                <a-form-item label="存储桶域名">
                  <a-input 
                    v-model:value="systemForm.storageConfig.domainName" 
                    placeholder="请输入"
                    class="config-input"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="24">
                <a-form-item label="AK KEY">
                  <a-input 
                    v-model:value="systemForm.storageConfig.akKey" 
                    placeholder="请输入"
                    class="config-input"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="24">
                <a-form-item label="SK KEY">
                  <a-input 
                    v-model:value="systemForm.storageConfig.skKey" 
                    placeholder="请输入"
                    type="password"
                    class="config-input"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </div>
      </div>

      <!-- 管理员密码修改 -->
      <div class="settings-section">
        <div class="section-header">
          <h2 class="section-title">管理员密码修改</h2>
        </div>
        <div class="section-content">
          <a-form
            :model="passwordForm"
            layout="vertical"
            @finish="handleChangePassword"
            :rules="passwordRules"
          >
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item
                  label="当前密码"
                  name="old_password"
                  required
                >
                  <a-input-password
                    v-model:value="passwordForm.old_password"
                    placeholder="请输入当前密码"
                    class="config-input"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item
                  label="新密码"
                  name="new_password"
                  required
                >
                  <a-input-password
                    v-model:value="passwordForm.new_password"
                    placeholder="请输入新密码（至少6位）"
                    class="config-input"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item
                  label="确认新密码"
                  name="confirm_password"
                  required
                >
                  <a-input-password
                    v-model:value="passwordForm.confirm_password"
                    placeholder="请再次输入新密码"
                    class="config-input"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="24">
                <div class="password-actions">
                  <a-button @click="resetPasswordForm" class="reset-password-btn">
                    重置表单
                  </a-button>
                  <a-button
                    type="primary"
                    html-type="submit"
                    :loading="loading"
                    class="change-password-btn"
                  >
                    修改密码
                  </a-button>
                </div>
              </a-col>
            </a-row>
          </a-form>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-bar">
        <a-button @click="handleReset" class="reset-btn">
          重置
        </a-button>
        <a-button type="primary" @click="handleSave" class="save-btn">
          保存配置
        </a-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.system-settings {
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  height: calc(100vh - 120px);
  overflow-y: auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 500;
  color: #262626;
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: #8c8c8c;
}

.settings-content {
  max-width: 800px;
}

.settings-section {
  margin-bottom: 32px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  background-color: #fafafa;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

.section-content {
  padding: 24px 20px;
}

.label-with-checkbox {
  display: flex;
  align-items: center;
}

.config-input {
  border-radius: 6px;
}

.config-input :deep(.ant-input) {
  border-radius: 6px;
}

.provider-select {
  width: 120px;
}

.provider-select :deep(.ant-select-selector) {
  border-radius: 6px;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px 0;
  border-top: 1px solid #f0f0f0;
  margin-top: 32px;
}

.reset-btn {
  padding: 0 20px;
  height: 36px;
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  background-color: #fff;
  color: #595959;
}

.reset-btn:hover {
  border-color: #40a9ff;
  color: #40a9ff;
}

.save-btn {
  padding: 0 20px;
  height: 36px;
  border-radius: 6px;
  background-color: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

.save-btn:hover {
  background-color: #40a9ff;
  border-color: #40a9ff;
}

:deep(.ant-form-item-label > label) {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

:deep(.ant-checkbox-wrapper) {
  font-size: 14px;
  color: #262626;
}

:deep(.ant-input::placeholder) {
  color: #bfbfbf;
  font-size: 14px;
}

:deep(.ant-select-selection-placeholder) {
  color: #bfbfbf;
  font-size: 14px;
}

.password-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.reset-password-btn {
  padding: 0 16px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  background-color: #fff;
  color: #595959;
}

.reset-password-btn:hover {
  border-color: #40a9ff;
  color: #40a9ff;
}

.change-password-btn {
  padding: 0 16px;
  height: 32px;
  border-radius: 6px;
  background-color: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

.change-password-btn:hover {
  background-color: #40a9ff;
  border-color: #40a9ff;
}
</style>