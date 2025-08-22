<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>管理员登录</h2>
        <p>《开源项目构建与实践》课程资源管理后台</p>
      </div>
      
      <a-form
        :model="formState"
        name="login"
        layout="vertical"
        @finish="onFinish"
        @finish-failed="onFinishFailed"
        class="login-form"
      >
        <a-form-item
          label="用户名或邮箱"
          name="identifier"
          :rules="[{ required: true, message: '请输入用户名或邮箱!' }]"
        >
          <a-input 
            v-model:value="formState.identifier" 
            placeholder="请输入用户名或邮箱"
            size="large"
          />
        </a-form-item>

        <a-form-item
          label="密码"
          name="password"
          :rules="[{ required: true, message: '请输入密码!' }]"
        >
          <a-input-password 
            v-model:value="formState.password" 
            placeholder="请输入密码"
            size="large"
          />
        </a-form-item>

        <a-form-item>
          <a-button 
            type="primary" 
            html-type="submit" 
            :loading="loading" 
            block 
            size="large"
            class="login-button"
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);

const formState = reactive({
  identifier: '',
  password: ''
});

const API_BASE_URL = 'http://localhost:8000/api/v1/auth';

const onFinish = async (values) => {
  loading.value = true;
  
  try {
    const response = await axios.post(`${API_BASE_URL}/login`, {
      identifier: values.identifier,
      password: values.password
    });
    
    if (response.data.code === 200) {
      const { access_token, refresh_token } = response.data.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      message.success('登录成功!');
      
      router.push('/welcome');
    } else {
      message.error(response.data.message || '登录失败');
    }
  } catch (error) {
    console.error('Login error:', error);
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('登录失败，请检查网络连接');
    }
  } finally {
    loading.value = false;
  }
};

const onFinishFailed = (errorInfo) => {
  console.log('Failed:', errorInfo);
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.login-header p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.login-form {
  flex: 1;
}

.login-form :deep(.ant-form-item-label) {
  font-weight: 500;
  color: #333;
}

.login-form :deep(.ant-input),
.login-form :deep(.ant-input-password) {
  border-radius: 8px;
}

.login-button {
  height: 44px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.login-button:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

@media (max-width: 480px) {
  .login-card {
    padding: 24px;
    margin: 20px;
  }
  
  .login-header h2 {
    font-size: 20px;
  }
}
</style>