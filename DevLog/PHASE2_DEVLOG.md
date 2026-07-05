# 开发日志 - 组长（后端开发）

## 阶段二：RAG 引擎与 API 服务化

### 完成时间：2026-07-04

---

## 一、新增文件清单

```
backend/
├── src/
│   ├── core/                       # RAG核心模块（新增）
│   │   ├── __init__.py
│   │   ├── prompts.py              # HR助手Prompt模板
│   │   ├── tools.py                # Function Call工具封装（4个计算工具）
│   │   └── rag_chain.py            # RAG检索链（LCEL管道语法）
│   └── api/                        # FastAPI服务层（新增）
│       ├── __init__.py
│       ├── main.py                 # FastAPI应用入口
│       ├── dependencies.py         # 公共依赖（API Key鉴权）
│       └── routes/
│           ├── __init__.py
│           ├── auth.py             # 登录认证接口
│           ├── chat.py             # 智能对话接口（SSE流式输出）
│           └── management.py       # 管理后台接口（文档/日志/用户/配置）
```

---

## 二、模块详解

### 2.1 src/core/prompts.py - Prompt模板

定义HR助手系统提示词，核心规则：
- 基于知识库回答，不编造信息
- 无法回答时引导咨询HR部门
- 回答末尾强制标注【来源:文件名-第X页】
- 涉及薪资计算时使用提供的计算工具
- 回复字数受 config.csv 中 max_response_length 控制

### 2.2 src/core/tools.py - Function Call工具

将阶段一的 calculator.py 函数封装为 LangChain `@tool` 装饰器工具，供LLM自动调用：

| 工具函数 | 对应原子函数 | 用途 |
|----------|-------------|------|
| `calculate_net_salary_tool` | `calculate_net_salary()` | 综合工资计算 |
| `calculate_late_deduction_tool` | `calculate_deduction()` | 迟到扣款计算 |
| `calculate_leave_deduction_tool` | `calculate_leave_deduction()` | 事假扣款计算 |
| `calculate_overtime_pay_tool` | `calculate_overtime_pay()` | 加班费计算 |

所有工具注册在 `ALL_TOOLS` 列表中，通过 `llm.bind_tools(ALL_TOOLS)` 绑定到LLM。

### 2.3 src/core/rag_chain.py - RAG检索链

使用 LangChain LCEL（LangChain Expression Language）管道语法构建完整RAG链路：

**链路结构**：
```
用户输入 → 敏感词过滤 → 向量检索(Top-5) → 上下文格式化 → Prompt拼装 → LLM(含工具) → 回答
```

**核心功能**：
- **向量检索**：加载 Chroma 向量库，DashScopeEmbeddings 向量化查询，返回 Top-5 结果
- **多轮对话**：`RunnableWithMessageHistory` + 内存会话历史，支持上下文关联追问
- **Function Call**：LLM绑定4个薪资计算工具，自动识别计算意图并调用
- **流式输出**：`get_stream_answer()` 生成器逐块输出，支持SSE推送
- **字数截断**：读取 config.csv 配置，超长回复自动截断
- **敏感词过滤**：`filter_sensitive_words()` 替换敏感词为 `*`

**关键设计决策**：
- 使用纯 LCEL 管道语法（LangChain 1.3+ 不支持 `langchain.chains` 旧API）
- 流式输出手动管理消息历史，确保多轮对话记忆完整
- 上下文格式化时在每段文本前添加来源标记，辅助LLM生成引用

### 2.4 src/api/main.py - FastAPI应用入口

- 注册三个路由模块：auth、chat、management
- CORS 中间件：允许前端跨域访问
- 提供 `/` 根路径（服务状态）和 `/health` 健康检查

### 2.5 API 接口列表

| 方法 | 路径 | 说明 | 响应格式 |
|------|------|------|----------|
| GET | `/` | 服务状态 | JSON |
| GET | `/health` | 健康检查 | JSON |
| POST | `/api/auth/login` | 用户登录 | JSON |
| POST | `/api/chat` | 智能对话 | SSE 流式 |
| GET | `/api/docs` | 文档列表 | JSON |
| POST | `/api/docs/delete` | 删除文档向量 | JSON |
| GET | `/api/logs` | 对话日志列表 | JSON |
| GET | `/api/users` | 用户列表(不含密码) | JSON |
| GET | `/api/config` | 系统配置参数 | JSON |

---

## 三、接口详细说明

### 3.1 POST /api/auth/login

**请求体**：
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**成功响应**：
```json
{
    "success": true,
    "message": "登录成功",
    "user": {
        "用户ID": "U001",
        "用户名": "admin",
        "邮箱": "admin@company.com",
        "部门": "IT部"
    }
}
```

**失败响应**：HTTP 401，detail: "用户名或密码错误"

### 3.2 POST /api/chat (SSE流式)

**请求体**：
```json
{
    "question": "员工入职流程是什么？",
    "session_id": "session_001",
    "user_id": "U001"
}
```

**SSE事件格式**：
```
data: {"type": "content", "content": "新员工入职需要..."}
data: {"type": "content", "content": "..."}
data: {"type": "done", "content": ""}
```

每次对话结束自动调用 `save_chat_log()` 保存记录到 logs.csv。

### 3.3 POST /api/docs/delete

**请求体**：
```json
{
    "filename": "员工手册.pdf"
}
```

**响应**：
```json
{
    "success": true,
    "message": "已删除文档 员工手册.pdf 的 35 个向量块",
    "deleted_count": 35
}
```

---

## 四、运行方式

### 环境准备

```bash
# 安装依赖
pip install fastapi uvicorn langchain-chroma

# 设置环境变量（百炼API Key）
set DASHSCOPE_API_KEY=your_api_key_here
```

### 启动服务

```bash
cd backend
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 访问

- API文档（Swagger UI）：http://localhost:8000/docs
- API文档（ReDoc）：http://localhost:8000/redoc
- 健康检查：http://localhost:8000/health

### 运行测试

```bash
cd backend
python -m pytest tests/ -v
```

---

## 五、测试验证结果

### 单元测试：30/30 全部通过
```
tests/test_calculator.py - 19 passed
tests/test_file_manager.py - 11 passed
```

### API接口验证：9个接口全部正常

| 测试项 | 结果 |
|--------|------|
| 健康检查 | PASS |
| 用户登录（正确密码） | PASS - 返回用户信息 |
| 用户登录（错误密码） | PASS - 返回401 |
| 文档列表查询 | PASS |
| 日志列表查询 | PASS - 8条记录 |
| 配置参数查询 | PASS - 6个参数 |
| 用户列表查询 | PASS - 12个用户(不含密码) |
| 向量检索测试 | PASS - 检索到5个文档块 |
| 服务启动 | PASS - Uvicorn正常运行 |

---

## 六、待前端对接的接口约定

阶段三（前端开发）需要对接以下接口：

### 对话流式消费
```javascript
const eventSource = new EventSource('/api/chat');
// 或使用 fetch + ReadableStream 处理 POST SSE
// 解析 data: {"type": "content", "content": "..."}
// 解析 data: {"type": "done", "content": ""}
```

### 来源标注正则
```
【来源:(.+?)-第(\d+)页】
```
前端可用此正则匹配并渲染为可点击的来源标签。

### 模拟数据（Mock）
前端在等待后端接口联调时，可直接读取 `backend/data/rules/*.csv` 作为Mock数据源。

---

## 七、技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.13.5 | 运行环境 |
| FastAPI | 0.139.0 | Web API框架 |
| Uvicorn | 0.49.0 | ASGI服务器 |
| LangChain Core | 1.4.8 | RAG管道核心 |
| LangChain Community | - | ChatTongyi + DashScopeEmbeddings |
| LangChain Chroma | 1.1.0 | Chroma向量库集成 |
| ChromaDB | 1.5.9 | 向量数据库 |
| DashScope | 1.26.2 | 阿里云AI API |

---

## 八、给阶段三（前端）的交接说明

> 阶段二完成了。RAG链在 `backend/src/core/rag_chain.py`，FastAPI服务入口在 `backend/src/api/main.py`。
>
> **核心接口**：
> - 登录：`POST /api/auth/login`（body: username, password）
> - 对话：`POST /api/chat`（SSE流式返回，body: question, session_id, user_id）
> - 管理：`GET /api/docs`、`POST /api/docs/delete`、`GET /api/logs`、`GET /api/users`、`GET /api/config`
>
> **启动命令**：`cd backend && python -m uvicorn src.api.main:app --reload --port 8000`
> **Swagger文档**：启动后访问 http://localhost:8000/docs 可查看所有接口
> **测试**：30个pytest全部通过，9个API接口验证正常

> 终端接口启动指令：
> PS D:\APP\pycharm\data\OnboardingBot> cd backend
> PS D:\APP\pycharm\data\OnboardingBot\backend> python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

> - Swagger 接口文档 ： http://localhost:8000/docs
> - ReDoc 文档 ： http://localhost:8000/redoc
> - 健康检查 ： http://localhost:8000/health
