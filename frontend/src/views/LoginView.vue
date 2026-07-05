<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api'

const router = useRouter()

const username = ref('admin')
const password = ref('admin123')
const errorMsg = ref('')
const loading = ref(false)

// 提交登录并缓存登录态到localStorage
async function handleLogin() {
  errorMsg.value = ''
  if (!username.value || !password.value) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    const res = await login(username.value, password.value)
    if (res && res.success) {
      const user = res.user || {}
      localStorage.setItem('loggedIn', 'true')
      localStorage.setItem('userId', user['用户ID'] || '')
      localStorage.setItem('username', user['用户名'] || username.value)
      localStorage.setItem('department', user['部门'] || '')
      router.push('/admin/docs')
    } else {
      errorMsg.value = res && res.message ? res.message : '登录失败'
    }
  } catch (err) {
    errorMsg.value = '登录失败：' + (err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-box">
      <h2>入职智引系统</h2>
      <p class="login-sub">管理后台登录</p>
      <div class="login-form">
        <div class="form-item">
          <label>用户名</label>
          <input v-model="username" type="text" placeholder="请输入用户名" @keyup.enter="handleLogin" />
        </div>
        <div class="form-item">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" @keyup.enter="handleLogin" />
        </div>
        <p v-if="errorMsg" class="error-tip">{{ errorMsg }}</p>
        <button class="btn-primary login-btn" :disabled="loading" @click="handleLogin">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <p class="login-hint">默认账号：admin / admin123</p>
        <router-link to="/chat" class="to-chat">前往智能对话</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
}

.login-box {
  width: 360px;
  background: #fff;
  border-radius: 12px;
  padding: 36px 32px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.login-box h2 {
  margin: 0 0 4px;
  font-size: 22px;
  text-align: center;
  color: var(--text);
}

.login-sub {
  text-align: center;
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 28px;
}

.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.login-btn {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
}

.error-tip {
  color: var(--danger);
  font-size: 13px;
  margin: 8px 0;
}

.login-hint {
  text-align: center;
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 16px;
}

.to-chat {
  display: block;
  text-align: center;
  color: var(--primary);
  font-size: 13px;
  margin-top: 12px;
  text-decoration: none;
}

.to-chat:hover {
  text-decoration: underline;
}
</style>
