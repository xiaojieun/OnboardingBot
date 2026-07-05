# 开发日志 - 成员三（前端开发）

## 阶段三：交互实现与体验打磨

### 完成时间：2026-07-05

---

## 一、新增文件清单

```
frontend/
├── src/
│   ├── api/                        # 接口服务层（新增）
│   │   ├── index.js                # axios封装 + SSE流式消费 + 来源解析
│   │   └── mock.js                 # 后端未启动时的兜底Mock数据
│   ├── router/
│   │   └── index.js                # vue-router路由表（新增）
│   ├── views/                      # 页面组件
│   │   ├── LoginView.vue           # 登录页（新增）
│   │   ├── ChatView.vue            # AI智能对话页（新增，含SSE流式+来源高亮）
│   │   ├── AdminView.vue           # 管理后台布局（重写）
│   │   ├── DocsView.vue            # 文档管理（新增）
│   │   ├── UsersView.vue           # 用户管理（新增）
│   │   └── LogsView.vue            # 对话日志（新增，含筛选）
│   ├── App.vue                     # 根组件（简化为router-view）
│   ├── main.js                     # 入口（注册路由）
│   └── style.css                   # 全局样式（重写为项目风格）
├── vite.config.js                  # 添加/api代理到后端8000端口
└── index.html                      # 标题改为"入职智引系统"
```

删除文件：
- `src/components/HelloWorld.vue`（Vite模板默认组件，不再使用）

---

## 二、模块详解

### 2.1 src/api/index.js - 接口服务层

封装所有后端接口调用，并提供SSE流式消费函数：

| 函数 | 功能 | 对应接口 |
|------|------|----------|
| `login(username, password)` | 用户登录 | POST /api/auth/login |
| `fetchDocs()` | 获取文档列表 | GET /api/docs |
| `deleteDoc(filename)` | 删除文档向量 | POST /api/docs/delete |
| `fetchLogs()` | 获取对话日志 | GET /api/logs |
| `fetchUsers()` | 获取用户列表 | GET /api/users |
| `fetchConfig()` | 获取系统配置 | GET /api/config |
| `streamChat(question, sessionId, userId, onChunk)` | SSE流式对话 | POST /api/chat |

**核心设计**：
- `safeRequest` 统一封装：接口失败时自动回退到Mock数据，确保前端在无后端环境下也能演示
- `streamChat` 使用 `fetch + ReadableStream` 解析SSE事件（因EventSource不支持POST）
- `parseSources(text)` 用正则 `/【来源:(.+?)-第(\d+)页】/g` 提取来源标记
- `stripSources(text)` 移除来源标记得到纯文本

### 2.2 src/api/mock.js - Mock数据

参照阶段一交付的CSV数据结构编写，包含文档、用户、日志、配置四类Mock数据。

### 2.3 LoginView.vue - 登录页

- 表单含用户名、密码字段，回车快捷提交
- 调用 `/api/auth/login` 接口，成功后将 `loggedIn`、`userId`、`username`、`department` 写入 `localStorage`
- 默认账号提示：admin / admin123

### 2.4 ChatView.vue - AI智能对话页（核心）

**版块布局**：左侧边栏 + 主对话区

**侧边栏功能**：
- 4个快捷提问按钮（入职流程、迟到扣款、事假扣款、加班费），点击即自动发送
- 清除当前会话按钮（重新生成session_id并清空消息）
- 登录态展示与管理后台入口

**主对话区**：
- 消息列表（用户消息右对齐绿色头像，AI消息左对齐紫色头像）
- Markdown渲染（使用marked库）
- 打字机效果：流式接收时显示闪烁光标
- 输入框（回车发送，Shift+回车换行）

**SSE流式对接**：
- 使用 `streamChat` 函数消费 `/api/chat` SSE流
- 每个 `content` 事件追加到当前AI消息，实时渲染
- `done` 事件结束流式状态，`error` 事件显示错误提示

**来源溯源高亮**：
- `renderAnswer(text)` 函数将回答文本按 `【来源:xxx-第X页】` 正则拆分为文本段和来源段
- 来源段渲染为高亮可点击的圆角标签（紫色边框）
- 点击标签弹出弹窗显示来源文件名和页码

**会话持久化**：
- `onMounted` 时从 `localStorage.chatMessages` 加载历史消息
- 消息变化时通过防抖自动保存到本地
- 刷新页面后历史对话正常恢复

### 2.5 AdminView.vue - 管理后台布局

- 侧边栏导航：智能对话、文档管理、用户管理、对话日志
- 顶部状态栏：当前页面标题 + 服务运行状态指示灯
- 登录态展示与退出按钮
- 子路由出口 `<router-view />`

### 2.6 DocsView.vue - 文档管理

- 表格展示文件名、类型、大小、操作
- 删除按钮调用 `/api/docs/delete` 接口，二次确认后执行
- 删除完成自动刷新列表并显示提示
- 文件大小自动格式化（B/KB/MB）

### 2.7 UsersView.vue - 用户管理

- 表格展示用户ID、用户名、邮箱、部门（不含密码，由后端过滤）
- 刷新按钮重新拉取数据

### 2.8 LogsView.vue - 对话日志

- 双筛选条件：用户ID（模糊匹配）+ 关键词（匹配问题和回答）
- 使用 `computed` 实现响应式筛选，无需重新请求
- 表格展示日志ID、用户ID、问题、回答、来源、时间

---

## 三、路由设计

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | - | 重定向到 `/chat` |
| `/login` | LoginView | 登录页 |
| `/chat` | ChatView | AI智能对话 |
| `/admin` | AdminView | 管理后台布局（重定向到/docs） |
| `/admin/docs` | DocsView | 文档管理 |
| `/admin/users` | UsersView | 用户管理 |
| `/admin/logs` | LogsView | 对话日志 |

---

## 四、运行方式

### 环境准备

```bash
cd frontend
npm install
```

### 启动前端开发服务

```bash
cd frontend
npm run dev
```

- 访问地址：http://localhost:5173
- Vite已配置代理：前端 `/api/*` 请求自动转发到后端 `http://localhost:8000`

### 完整联调（前后端同时运行）

终端一（后端）：
```bash
cd backend
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

终端二（前端）：
```bash
cd frontend
npm run dev
```

### 构建生产包

```bash
cd frontend
npm run build
```

构建产物输出到 `frontend/dist/`，可部署到任意静态服务器。

---

## 五、自测报告

### 5.1 双版块基座

| 测试项 | 结果 |
|--------|------|
| 路由切换（对话↔管理后台） | PASS |
| 侧边栏导航高亮 | PASS |
| 管理后台子路由渲染 | PASS |
| Mock数据兜底渲染 | PASS |

### 5.2 AI智能对话

| 测试项 | 结果 |
|--------|------|
| 快捷提问点击自动发送 | PASS |
| SSE流式打字机效果 | PASS（后端启动时） |
| 来源标签高亮渲染 | PASS |
| 来源标签点击弹窗 | PASS |
| 清除会话 | PASS |
| 刷新页面历史恢复 | PASS（localStorage） |
| 后端未启动时Mock兜底 | PASS |

### 5.3 管理后台

| 测试项 | 结果 |
|--------|------|
| 登录成功跳转 | PASS |
| 登录失败提示 | PASS |
| 登录态localStorage缓存 | PASS |
| 退出登录 | PASS |
| 文档列表加载 | PASS |
| 文档删除联动后端 | PASS（后端启动时） |
| 用户列表展示（不含密码） | PASS |
| 日志按用户ID筛选 | PASS |
| 日志按关键词筛选 | PASS |
| 日志筛选清空 | PASS |

---

## 六、技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5.39 | 前端框架（script setup） |
| Vue Router | 4.6.4 | 前端路由 |
| Vite | 8.1.1 | 构建工具 |
| Axios | 1.18.1 | HTTP请求 |
| marked | 18.0.5 | Markdown渲染 |

---

## 七、设计要点说明

1. **Mock兜底机制**：所有接口请求失败时自动回退到 `mock.js` 中的数据，确保前端在无后端环境下也能独立演示和自测。

2. **SSE流式消费**：因浏览器原生 `EventSource` 仅支持GET请求，对话接口使用 `fetch + ReadableStream` 手动解析SSE事件流，按 `\n\n` 分割事件块，解析 `data: ` 前缀的JSON数据。

3. **来源溯源渲染**：用正则将回答文本拆分为文本段和来源段，来源段渲染为独立的可点击标签组件，避免简单字符串替换导致的HTML注入风险。

4. **会话持久化**：对话消息自动保存到 `localStorage`，刷新页面后恢复，避免开发调试时丢失上下文。

5. **基础代码实现**：未引入UI组件库和状态管理库，全部使用原生Vue3 + 基础CSS，符合轻量化脚手架定位。

---

## 八、给阶段四（文档与项目）的交接说明

> 阶段三完成了。前端工程在 `frontend/` 目录，启动命令 `npm run dev`。
>
> **核心页面**：
> - 登录：`/login`（默认账号 admin / admin123）
> - 对话：`/chat`（支持快捷提问、流式输出、来源高亮、会话清除）
> - 管理：`/admin/docs`、`/admin/users`、`/admin/logs`
>
> **演示流程建议**：
> 1. 先访问 `/login` 登录管理后台
> 2. 在文档管理页确认文档列表
> 3. 前往 `/chat` 提问"员工入职流程"，观察流式输出和来源标签
> 4. 点击来源标签查看弹窗
> 5. 返回管理后台查看对话日志，使用筛选功能
>
> **注意事项**：
> - 前端必须与后端同时运行才能完整体验SSE流式对话（前端已配置代理）
> - 后端未启动时，管理后台接口会自动回退到Mock数据，对话功能会提示连接失败
> - 来源标签弹窗目前展示文件名和页码，原始文本块获取需通过对话提问
