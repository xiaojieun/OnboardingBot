<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchLogs } from '../api'

const logs = ref([])
const loading = ref(false)
const filterUserId = ref('')
const filterKeyword = ref('')

async function loadLogs() {
  loading.value = true
  const res = await fetchLogs()
  logs.value = res && res.logs ? res.logs : []
  loading.value = false
}

// 按用户ID和关键词筛选日志
const filteredLogs = computed(() => {
  return logs.value.filter((log) => {
    const uid = (log['用户ID'] || '').toString()
    const question = log['问题'] || ''
    const answer = log['回答'] || ''
    const matchUid = !filterUserId.value || uid.includes(filterUserId.value.trim())
    const kw = filterKeyword.value.trim()
    const matchKw = !kw || question.includes(kw) || answer.includes(kw)
    return matchUid && matchKw
  })
})

function clearFilter() {
  filterUserId.value = ''
  filterKeyword.value = ''
}

onMounted(loadLogs)
</script>

<template>
  <div>
    <div class="filter-bar">
      <div class="filter-item">
        <label>用户ID</label>
        <input v-model="filterUserId" placeholder="如 U001" />
      </div>
      <div class="filter-item">
        <label>关键词</label>
        <input v-model="filterKeyword" placeholder="问题或回答关键词" />
      </div>
      <button class="btn-ghost" @click="clearFilter">清空</button>
      <button class="btn-primary" @click="loadLogs" :disabled="loading">刷新</button>
      <span class="count">共 {{ filteredLogs.length }} 条（总计 {{ logs.length }} 条）</span>
    </div>

    <p v-if="loading" class="loading-tip">加载中...</p>
    <table v-else-if="filteredLogs.length">
      <thead>
        <tr>
          <th>日志ID</th>
          <th>用户ID</th>
          <th>问题</th>
          <th>回答</th>
          <th>来源</th>
          <th>时间</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="log in filteredLogs" :key="log['日志ID']">
          <td>{{ log['日志ID'] }}</td>
          <td>{{ log['用户ID'] }}</td>
          <td class="col-question">{{ log['问题'] }}</td>
          <td class="col-answer">{{ log['回答'] }}</td>
          <td><span class="tag">{{ log['知识库来源'] }}</span></td>
          <td class="col-time">{{ log['时间戳'] }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty-tip">暂无符合条件的日志记录</p>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-item label {
  font-size: 12px;
  color: var(--text-secondary);
}

.filter-item input {
  width: 180px;
}

.count {
  color: var(--text-secondary);
  font-size: 13px;
  margin-left: auto;
}

.col-question {
  max-width: 240px;
}

.col-answer {
  max-width: 320px;
  white-space: pre-wrap;
}

.col-time {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}
</style>
