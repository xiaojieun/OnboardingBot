<script setup>
import { ref, onMounted } from 'vue'
import { fetchUsers } from '../api'

const users = ref([])
const loading = ref(false)

async function loadUsers() {
  loading.value = true
  const res = await fetchUsers()
  users.value = res && res.users ? res.users : []
  loading.value = false
}

onMounted(loadUsers)
</script>

<template>
  <div>
    <div class="page-bar">
      <button class="btn-ghost" @click="loadUsers" :disabled="loading">刷新列表</button>
      <span class="count">共 {{ users.length }} 个用户</span>
    </div>

    <p v-if="loading" class="loading-tip">加载中...</p>
    <table v-else-if="users.length">
      <thead>
        <tr>
          <th>用户ID</th>
          <th>用户名</th>
          <th>邮箱</th>
          <th>部门</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u['用户ID']">
          <td>{{ u['用户ID'] }}</td>
          <td>{{ u['用户名'] }}</td>
          <td>{{ u['邮箱'] }}</td>
          <td><span class="tag">{{ u['部门'] }}</span></td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty-tip">暂无用户数据</p>
  </div>
</template>

<style scoped>
.page-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.count {
  color: var(--text-secondary);
  font-size: 13px;
}
</style>
