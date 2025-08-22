<script setup>
import { ref, reactive } from 'vue';
import { message } from 'ant-design-vue';

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
</style>