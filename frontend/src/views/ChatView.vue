<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { marked } from 'marked'
import { streamChat, parseSources, stripSources } from '../api'

const messages = ref([])
const inputText = ref('')
const sessionId = ref('session_' + Date.now())
const streaming = ref(false)
const errorTip = ref('')
const sourcePopup = ref(null)

const chatBody = ref(null)

const loggedIn = ref(localStorage.getItem('loggedIn') === 'true')
const username = ref(localStorage.getItem('username') || '游客')
const userId = ref(localStorage.getItem('userId') || 'anonymous')

const quickQuestions = [
  '员工入职流程是什么？',
  '迟到扣款怎么计算？',
  '事假扣款如何计算？',
  '加班费计算规则是什么？',
]

// 自动滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatBody.value) {
      chatBody.value.scrollTop = chatBody.value.scrollHeight
    }
  })
}

// 把回答文本按来源标记拆分成段
function renderAnswer(text) {
  const regex = /【来源:(.+?)-第(\d+)页】/g
  const parts = []
  let lastIndex = 0
  let match
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', value: text.slice(lastIndex, match.index) })
    }
    parts.push({ type: 'source', filename: match[1], page: match[2], raw: match[0] })
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < text.length) {
    parts.push({ type: 'text', value: text.slice(lastIndex) })
  }
  return parts
}

// 把文本段渲染为HTML
function toHtml(text) {
  try {
    return marked.parse(text)
  } catch (e) {
    return text
  }
}

// 发送消息并接收流式回答
async function sendMessage(text) {
  const question = (text ?? inputText.value).trim()
  if (!question || streaming.value) return

  errorTip.value = ''
  inputText.value = ''
  messages.value.push({ role: 'user', content: question, parts: [] })
  messages.value.push({ role: 'assistant', content: '', parts: [], streaming: true })
  streaming.value = true
  scrollToBottom()

  try {
    await streamChat(question, sessionId.value, userId.value, (data) => {
      if (data.type === 'content') {
        const last = messages.value[messages.value.length - 1]
        last.content += data.content
        last.parts = renderAnswer(last.content)
        scrollToBottom()
      } else if (data.type === 'error') {
        errorTip.value = data.content
      }
    })
  } catch (err) {
    errorTip.value = '对话失败：' + err.message + '（请确认后端服务已启动）'
  } finally {
    const last = messages.value[messages.value.length - 1]
    if (last) last.streaming = false
    streaming.value = false
    scrollToBottom()
  }
}

// 清除当前会话历史
function clearSession() {
  sessionId.value = 'session_' + Date.now()
  messages.value = []
  errorTip.value = ''
}

// 点击来源标签弹出原文信息
function clickSource(source) {
  sourcePopup.value = source
}

function closePopup() {
  sourcePopup.value = null
}

// 进入对话页时加载历史会话
onMounted(() => {
  const saved = localStorage.getItem('chatMessages')
  if (saved) {
    try {
      const arr = JSON.parse(saved)
      messages.value = arr.map((m) => ({
        ...m,
        parts: m.role === 'assistant' ? renderAnswer(m.content) : [],
      }))
    } catch (e) {
      messages.value = []
    }
  }
})

// 自动保存会话到本地
const saveTimer = ref(null)
function autoSave() {
  if (saveTimer.value) clearTimeout(saveTimer.value)
  saveTimer.value = setTimeout(() => {
    const toSave = messages.value.map((m) => ({ role: m.role, content: m.content }))
    localStorage.setItem('chatMessages', JSON.stringify(toSave))
  }, 500)
}

const messagesWatcher = computed(() => {
  messages.value.length
  autoSave()
  return true
})
</script>

<template>
  <div class="chat-layout">
    <aside class="chat-sidebar">
      <div class="sidebar-top">
        <h3>AI 智能对话</h3>
        <p class="sub">入职智引助手</p>
      </div>
      <div class="sidebar-section">
        <p class="section-title">快捷提问</p>
        <button
          v-for="q in quickQuestions"
          :key="q"
          class="quick-btn"
          :disabled="streaming"
          @click="sendMessage(q)"
        >
          {{ q }}
        </button>
      </div>
      <div class="sidebar-section">
        <p class="section-title">会话控制</p>
        <button class="btn-ghost clear-btn" @click="clearSession">清除当前会话</button>
      </div>
      <div class="sidebar-bottom">
        <div v-if="loggedIn" class="user-box">
          <span>{{ username }}</span>
          <router-link to="/admin/docs" class="to-admin">管理后台</router-link>
        </div>
        <router-link v-else to="/login" class="to-admin">登录管理后台</router-link>
      </div>
    </aside>

    <main class="chat-main">
      <header class="chat-header">
        <h3>智能对话</h3>
        <span class="session-id">会话：{{ sessionId }}</span>
      </header>

      <div ref="chatBody" class="chat-body">
        <div v-if="messages.length === 0" class="empty-tip">
          欢迎使用入职智引助手，请输入问题或点击快捷提问开始对话
        </div>

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['msg-row', msg.role]"
        >
          <div class="msg-avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
          <div class="msg-bubble">
            <template v-if="msg.role === 'user'">{{ msg.content }}</template>
            <template v-else>
              <template v-for="(part, pidx) in msg.parts" :key="pidx">
                <span v-if="part.type === 'text'" class="answer-text" v-html="toHtml(part.value)"></span>
                <button
                  v-else
                  class="source-tag"
                  @click="clickSource(part)"
                  :title="`查看 ${part.filename} 第${part.page}页`"
                >
                  来源：{{ part.filename }} - 第{{ part.page }}页
                </button>
              </template>
              <span v-if="msg.streaming" class="cursor">|</span>
            </template>
          </div>
        </div>

        <p v-if="errorTip" class="error-tip">{{ errorTip }}</p>
      </div>

      <footer class="chat-input">
        <textarea
          v-model="inputText"
          placeholder="输入问题，回车发送，Shift+回车换行"
          @keydown.enter.exact.prevent="sendMessage()"
          rows="2"
        ></textarea>
        <button class="btn-primary send-btn" :disabled="streaming || !inputText.trim()" @click="sendMessage()">
          {{ streaming ? '回答中...' : '发送' }}
        </button>
      </footer>
    </main>

    <div v-if="sourcePopup" class="source-popup-mask" @click="closePopup">
      <div class="source-popup" @click.stop>
        <div class="popup-header">
          <h4>来源详情</h4>
          <button class="btn-ghost" @click="closePopup">关闭</button>
        </div>
        <div class="popup-body">
          <p><strong>文件名：</strong>{{ sourcePopup.filename }}</p>
          <p><strong>页码：</strong>第 {{ sourcePopup.page }} 页</p>
          <p class="popup-tip">该来源引用自知识库文档，原始文本块需通过对话提问或后端检索接口获取。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.chat-sidebar {
  width: var(--sidebar-width);
  background: linear-gradient(180deg, #1e293b, #334155);
  color: #fff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-top {
  padding: 22px 18px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-top h3 {
  margin: 0;
  font-size: 17px;
}

.sidebar-top .sub {
  font-size: 12px;
  opacity: 0.6;
  margin-top: 4px;
}

.sidebar-section {
  padding: 16px 14px;
}

.section-title {
  font-size: 11px;
  opacity: 0.5;
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.quick-btn {
  display: block;
  width: 100%;
  text-align: left;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 8px;
  border: none;
}

.quick-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clear-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
}

.sidebar-bottom {
  margin-top: auto;
  padding: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.to-admin {
  color: #c4b5fd;
  font-size: 13px;
  text-decoration: none;
}

.to-admin:hover {
  text-decoration: underline;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg);
}

.chat-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
}

.session-id {
  font-size: 12px;
  color: var(--text-secondary);
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.msg-row {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
}

.msg-row.user .msg-avatar {
  background: #16a34a;
}

.msg-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  line-height: 1.6;
  word-break: break-word;
}

.msg-row.user .msg-bubble {
  background: #eef2ff;
  border-color: #c7d2fe;
}

.answer-text {
  display: inline;
}

.answer-text :deep(p) {
  margin: 0 0 8px;
}

.answer-text :deep(p:last-child) {
  margin-bottom: 0;
}

.source-tag {
  display: inline-block;
  background: var(--primary-light);
  color: var(--primary);
  border: 1px solid var(--primary);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  margin: 0 4px;
}

.source-tag:hover {
  background: var(--primary);
  color: #fff;
}

.cursor {
  color: var(--primary);
  font-weight: bold;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.error-tip {
  color: var(--danger);
  text-align: center;
  padding: 12px;
}

.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: var(--bg-card);
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}

.chat-input textarea {
  flex: 1;
  resize: none;
}

.send-btn {
  align-self: stretch;
  padding: 0 24px;
}

.source-popup-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.source-popup {
  width: 420px;
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.popup-header h4 {
  margin: 0;
  font-size: 16px;
}

.popup-body {
  padding: 20px;
  line-height: 1.8;
}

.popup-body p {
  margin: 0 0 8px;
}

.popup-tip {
  color: var(--text-secondary);
  font-size: 13px;
  margin-top: 12px;
}
</style>
