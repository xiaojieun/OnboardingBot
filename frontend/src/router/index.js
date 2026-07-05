import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'
import ChatView from '../views/ChatView.vue'
import AdminView from '../views/AdminView.vue'
import DocsView from '../views/DocsView.vue'
import UsersView from '../views/UsersView.vue'
import LogsView from '../views/LogsView.vue'

// 定义前后端路由表
const routes = [
  { path: '/', redirect: '/chat' },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/chat', name: 'chat', component: ChatView },
  {
    path: '/admin',
    component: AdminView,
    redirect: '/admin/docs',
    children: [
      { path: 'docs', name: 'docs', component: DocsView },
      { path: 'users', name: 'users', component: UsersView },
      { path: 'logs', name: 'logs', component: LogsView },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
