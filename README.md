中文 | [English](./README_EN.md)

# 入职智引系统 (OnboardingBot)

基于 RAG 架构的新员工入职智能助手，支持知识库问答、薪资计算、多轮对话与管理后台。

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 大语言模型 | qwen3.7-plus（百炼 API） | - |
| Embedding | text-embedding-v4（DashScope） | - |
| RAG 框架 | LangChain + LCEL | 1.3.11 |
| 向量数据库 | ChromaDB | 1.5.9 |
| 后端服务 | FastAPI + Uvicorn | 0.139.0 |
| 数据处理 | Pandas + NumPy | 3.0.3 |
| 前端框架 | Vue 3 + Vite | 3.5.39 |
| 运行环境 | Python | 3.12.10 |

## 项目结构

```
OnboardingBot/
├── backend/
│   ├── data/
│   │   ├── raw/                    # 原始文档（PDF/TXT/DOCX/MD）
│   │   └── rules/                  # 结构化 CSV 数据表
│   │       ├── salary.csv          # 薪资绩效表
│   │       ├── users.csv           # 用户信息表
│   │       ├── logs.csv            # 对话日志表
│   │       └── config.csv          # 系统配置表
│   ├── VectorStore/                # Chroma 向量库
│   ├── src/
│   │   ├── tools/                  # 原子函数
│   │   │   ├── calculator.py       # 薪资计算函数
│   │   │   └── file_manager.py     # 向量库/CSV 管理函数
│   │   ├── core/                   # RAG 核心模块
│   │   │   ├── rag_chain.py        # RAG 检索链（LCEL）
│   │   │   ├── tools.py            # Function Call 工具封装
│   │   │   └── prompts.py          # Prompt 模板
│   │   └── api/                    # FastAPI 接口层
│   │       ├── main.py             # 应用入口
│   │       └── routes/
│   │           ├── auth.py         # 登录认证
│   │           ├── chat.py         # 智能对话（SSE 流式）
│   │           └── management.py   # 管理后台接口
│   ├── tests/                      # 单元测试（30 个）
│   ├── build_vectorstore.py        # 向量库构建脚本
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/                    # 接口服务层 + Mock 数据
│   │   ├── views/                  # 页面组件
│   │   │   ├── LoginView.vue       # 登录页
│   │   │   ├── ChatView.vue        # AI 智能对话
│   │   │   ├── AdminView.vue       # 管理后台布局
│   │   │   ├── DocsView.vue        # 文档管理
│   │   │   ├── UsersView.vue       # 用户管理
│   │   │   └── LogsView.vue        # 对话日志
│   │   ├── router/index.js         # 路由配置
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── docs/                           # 文档资料
├── start.ps1                       # PowerShell 启动脚本
├── start.bat                       # 双击启动（Windows）
├── stop.bat                        # 双击停止（Windows）
├── requirements.txt                # Python 依赖
├── DEVLOG.md                       # 成员二开发日志
├── PHASE2_DEVLOG.md                # 组长开发日志
└── PHASE3_DEVLOG.md                # 成员三开发日志
```

## 快速开始

### 环境准备

- Python 3.12.10
- Node.js 18+
- 百炼平台 API Key

### 1. 安装后端依赖

```bash
# 创建虚拟环境（如已创建可跳过）
python -m venv .venv
.\.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# Windows PowerShell
$env:API_KEY="your_dashscope_api_key"

# 或创建 .env 文件（项目根目录）
echo API_KEY=your_dashscope_api_key > .env
```

### 3. 构建向量库

将文档放入 `backend/data/raw/` 目录，然后执行：

```bash
cd backend
python build_vectorstore.py
```

支持格式：PDF、TXT、MD、DOCX

### 4. 初始化数据表

```bash
cd backend
python -c "from src.tools.calculator import init_salary_table; init_salary_table()"
```

### 5. 一键启动

```bash
# 双击 start.bat 或在终端执行
.\start.ps1
```

脚本会自动启动后端和前端服务，并打开浏览器。

**其他命令：**

```powershell
.\start.ps1 -Stop          # 停止所有服务
.\start.ps1 -BackendOnly   # 仅启动后端
.\start.ps1 -FrontendOnly  # 仅启动前端
.\stop.bat                 # 快速停止（双击运行）
```

### 6. 手动启动（备选）

```bash
# 后端
cd backend
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm install
npm run dev
```

- Swagger 文档：http://localhost:8000/docs
- 前端地址：http://localhost:5173
- Vite 已配置代理，`/api/*` 自动转发到后端 `http://localhost:8000`

### 7. 运行测试

```bash
cd backend
python -m pytest tests/ -v
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 用户登录认证 |
| POST | `/api/chat` | 智能对话（SSE 流式输出） |
| GET | `/api/docs` | 文档列表 |
| POST | `/api/docs/delete` | 删除文档向量 |
| GET | `/api/logs` | 对话日志列表 |
| GET | `/api/users` | 用户列表 |
| GET | `/api/config` | 系统配置参数 |

## 核心功能

### RAG 智能问答

- 基于 ChromaDB 向量检索，Top-5 相关文档片段作为上下文
- 回答末尾自动标注引用来源：`【来源:文件名-第X页】`
- 多轮对话记忆，支持上下文关联追问

### Function Call 薪资计算

LLM 自动识别计算意图并调用工具，支持：

| 工具 | 说明 |
|------|------|
| `calculate_net_salary_tool` | 综合净工资计算 |
| `calculate_late_deduction_tool` | 迟到扣款（每次 50 元） |
| `calculate_leave_deduction_tool` | 事假扣款（日薪 x 天数） |
| `calculate_overtime_pay_tool` | 加班费（时薪 x 小时 x 倍率） |

### 管理后台

- 登录认证（Token 缓存到 localStorage）
- 文档管理（列表展示 + 删除向量清理）
- 用户管理（列表展示，不含密码）
- 对话日志（按用户 ID / 关键词筛选）

### 前端特性

- SSE 流式打字机效果
- 来源标签高亮可点击，弹窗展示出处
- 快捷提问按钮
- 会话历史自动保存（localStorage）
- 接口失败自动回退到 Mock 数据

## 系统配置

在 `backend/data/rules/config.csv` 中可调整：

| 参数名 | 默认值 | 说明 |
|--------|--------|------|
| chunk_size | 512 | 文本切片大小 |
| chunk_overlap | 50 | 文本切片重叠 |
| embedding_model | text-embedding-v4 | 向量化模型 |
| llm_model | qwen3.7-plus | 大语言模型 |
| max_response_length | 2000 | 单轮回答最大字数 |
| timeout_seconds | 30 | API 调用超时时间 |

## 演示流程

1. 访问 `http://localhost:5173/login` 登录（默认账号：admin / admin123）
2. 在管理后台确认文档列表
3. 前往 `/chat` 提问"员工入职流程是什么"
4. 观察流式输出和来源标签高亮
5. 点击来源标签查看出处弹窗
6. 提问"迟到 3 次扣多少钱"，验证 Function Call 精确计算
7. 返回管理后台查看对话日志，使用筛选功能

## 开发日志

- [PHASE1_DEVLOG.md](./DevLog/PHASE1_DEVLOG.mdd) - 阶段一：知识资产与计算引擎构建
- [PHASE2_DEVLOG.md](./DevLog/PHASE2_DEVLOG.md) - 阶段二：RAG 引擎与 API 服务化
- [PHASE3_DEVLOG.md](./DevLog/PHASE3_DEVLOG.md) - 阶段三：交互实现与体验打磨

## 鸣谢

感谢以下团队成员的辛勤付出：

| 成员      | 负责阶段             | 主要贡献                                        |
| :-------- | :------------------- | :---------------------------------------------- |
| xiaojieun | 阶段一（数据工程师） | 知识库构建、向量库、计算引擎、资产管理函数      |
| HanYu     | 阶段二（组长/后端）  | RAG 链路、FastAPI 服务、Function Call、流式输出 |
| xbin      | 阶段三（前端开发）   | Vue3 双版块界面、SSE 流式对接、管理后台交互     |

---

> 本项目为团队协作完成，各阶段采用串行开发模式。
