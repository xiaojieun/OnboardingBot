import axios from 'axios'
import { mockDocs, mockUsers, mockLogs, mockConfig } from './mock'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 统一请求封装，失败时回退到Mock数据
async function safeRequest(method, url, data, mockFallback) {
  try {
    const res = await api({ method, url, data })
    return res.data
  } catch (err) {
    console.warn(`接口 ${url} 调用失败，使用Mock数据:`, err.message)
    return mockFallback
  }
}

export function login(username, password) {
  return safeRequest('post', '/auth/login', { username, password }, null)
}

export function fetchDocs() {
  return safeRequest('get', '/docs', null, { success: true, documents: mockDocs })
}

export function deleteDoc(filename) {
  return safeRequest('post', '/docs/delete', { filename }, { success: true, message: 'Mock删除成功', deleted_count: 0 })
}

export function fetchLogs() {
  return safeRequest('get', '/logs', null, { success: true, logs: mockLogs, total: mockLogs.length })
}

export function fetchUsers() {
  return safeRequest('get', '/users', null, { success: true, users: mockUsers, total: mockUsers.length })
}

export function fetchConfig() {
  return safeRequest('get', '/config', null, { success: true, config: mockConfig })
}

// SSE流式对话：使用fetch读取ReadableStream解析事件
export async function streamChat(question, sessionId, userId, onChunk) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id: sessionId, user_id: userId }),
  })

  if (!response.ok) {
    throw new Error(`接口返回状态码 ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop()
    for (const part of parts) {
      const line = part.trim()
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          onChunk(data)
        } catch (e) {
          continue
        }
      }
    }
  }
}

// 解析回答中的来源标记
export function parseSources(text) {
  const regex = /【来源:(.+?)-第(\d+)页】/g
  const sources = []
  let match
  while ((match = regex.exec(text)) !== null) {
    sources.push({ filename: match[1], page: match[2] })
  }
  return sources
}

// 移除回答中的来源标记得到纯文本
export function stripSources(text) {
  return text.replace(/【来源:(.+?)-第(\d+)页】/g, '')
}
