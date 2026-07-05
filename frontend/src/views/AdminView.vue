<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const loggedIn = computed(() => localStorage.getItem('loggedIn') === 'true')
const username = computed(() => localStorage.getItem('username') || '')

const pageTitles = {
  docs: '文档管理',
  users: '用户管理',
  logs: '对话日志',
}

const pageTitle = computed(() => pageTitles[route.name] || '管理后台')

function handleLogout() {
  localStorage.removeItem('loggedIn')
  localStorage.removeItem('userId')
  localStorage.removeItem('username')
  localStorage.removeItem('department')
  router.push('/login')
}
</script>

<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <h2>管理后台</h2>
        <p class="subtitle">入职智引系统</p>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/chat" class="nav-item">
          <span>智能对话</span>
        </router-link>
        <div class="nav-divider"></div>
        <p class="nav-section-title">后台管理</p>
        <router-link to="/admin/docs" class="nav-item">
          <span>文档管理</span>
        </router-link>
        <router-link to="/admin/users" class="nav-item">
          <span>用户管理</span>
        </router-link>
        <router-link to="/admin/logs" class="nav-item">
          <span>对话日志</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div v-if="loggedIn" class="user-info">
          <span>{{ username }}</span>
          <button class="btn-logout" @click="handleLogout">退出</button>
        </div>
        <router-link v-else to="/login" class="btn-login-link">登录管理后台</router-link>
      </div>
    </aside>
    <main class="admin-main">
      <header class="admin-header">
        <h3>{{ pageTitle }}</h3>
        <div class="header-right">
          <span class="status-dot"></span>
          <span class="status-text">服务运行中</span>
        </div>
      </header>
      <div class="admin-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.admin-sidebar {
  width: var(--sidebar-width);
  background: linear-gradient(180deg, #1e293b, #334155);
  color: #fff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 24px 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h2 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.subtitle {
  font-size: 12px;
  opacity: 0.6;
  margin-top: 4px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
}

.nav-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 12px 4px;
}

.nav-section-title {
  font-size: 11px;
  opacity: 0.5;
  padding: 0 14px;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.nav-item {
  display: block;
  padding: 10px 14px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: all 0.2s;
  margin-bottom: 2px;
  text-decoration: none;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.nav-item.router-link-active {
  background: rgba(99, 102, 241, 0.3);
  color: #fff;
  font-weight: 600;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
}

.btn-logout {
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: rgba(239, 68, 68, 0.6);
  color: #fff;
}

.btn-login-link {
  display: block;
  text-align: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-radius: 6px;
  font-size: 13px;
  text-decoration: none;
  transition: background 0.2s;
}

.btn-login-link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.admin-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.admin-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success);
}

.status-text {
  font-size: 13px;
  color: var(--text-secondary);
}

.admin-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
