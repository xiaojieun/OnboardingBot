<script setup>
import { ref, onMounted } from 'vue'
import { fetchDocs, deleteDoc } from '../api'

const docs = ref([])
const loading = ref(false)
const deleting = ref('')
const tip = ref('')

// 加载文档列表
async function loadDocs() {
  loading.value = true
  tip.value = ''
  const res = await fetchDocs()
  docs.value = res && res.documents ? res.documents : []
  loading.value = false
}

// 删除指定文档向量并刷新列表
async function handleDelete(filename) {
  if (!confirm(`确认删除文档 ${filename} 及其向量数据？`)) return
  deleting.value = filename
  tip.value = ''
  try {
    const res = await deleteDoc(filename)
    tip.value = res.message || '删除完成'
    await loadDocs()
  } catch (err) {
    tip.value = '删除失败：' + err.message
  } finally {
    deleting.value = ''
  }
}

function formatSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

onMounted(loadDocs)
</script>

<template>
  <div>
    <div class="page-bar">
      <button class="btn-ghost" @click="loadDocs" :disabled="loading">刷新列表</button>
      <span class="count">共 {{ docs.length }} 份文档</span>
    </div>
    <p v-if="tip" class="tip">{{ tip }}</p>

    <p v-if="loading" class="loading-tip">加载中...</p>
    <table v-else-if="docs.length">
      <thead>
        <tr>
          <th>文件名</th>
          <th>类型</th>
          <th>大小</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doc in docs" :key="doc.filename">
          <td>{{ doc.filename }}</td>
          <td><span class="tag">{{ doc.type }}</span></td>
          <td>{{ formatSize(doc.size) }}</td>
          <td>
            <button
              class="btn-danger"
              @click="handleDelete(doc.filename)"
              :disabled="deleting === doc.filename"
            >
              {{ deleting === doc.filename ? '删除中...' : '删除' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty-tip">暂无文档，请将文件放入 backend/data/raw/ 后刷新</p>
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

.tip {
  background: var(--primary-light);
  color: var(--primary);
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 13px;
}
</style>
