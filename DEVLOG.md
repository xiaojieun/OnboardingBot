# 开发日志 - 成员二（数据工程师）

## 任务完成情况

### 任务2：混合格式知识库构建 - 已完成

**完成时间**：2026-07-04

**实现内容**：
- 创建 `backend/build_vectorstore.py` 脚本
- 支持 PDF、TXT、MD、DOCX 四种格式
- 使用 RecursiveCharacterTextSplitter 切片（chunk_size=512, overlap=50）
- 使用 DashScopeEmbeddings(text-embedding-v4) 向量化
- 生成 `backend/VectorStore/` 目录，包含35个文本块

**验证结果**：检索测试 Top-3 结果正确返回文件名（员工手册.pdf）和页码

---

### 任务3：结构化计算引擎 - 已完成

**完成时间**：2026-07-04

**实现内容**：
1. `backend/src/tools/calculator.py` - 薪资计算模块
   - `extract_salary_tables()` - 从PDF提取薪资表
   - `calculate_deduction()` - 迟到扣款计算
   - `calculate_leave_deduction()` - 事假扣款计算
   - `calculate_overtime_pay()` - 加班费计算
   - `calculate_net_salary()` - 净工资综合计算

2. CSV 数据表
   - `backend/data/rules/salary.csv` - 薪资表（5名员工示例数据）
   - `backend/data/rules/users.csv` - 用户表（3个初始用户）
   - `backend/data/rules/logs.csv` - 对话日志表（空表）
   - `backend/data/rules/config.csv` - 系统配置参数表

**验证结果**：19个 pytest 单元测试全部通过

---

### 任务4：动态资产管理函数 - 已完成

**完成时间**：2026-07-04

**实现内容**：
- `backend/src/tools/file_manager.py` - 文件管理工具模块

| 函数 | 功能 | 参数 |
|------|------|------|
| `delete_doc_vector(filename)` | 从Chroma删除指定文档向量 | filename: 文件名 |
| `add_user(username, password, email, department)` | 向users.csv添加用户 | 用户信息4个字段 |
| `save_chat_log(user_id, question, answer, kb_source)` | 向logs.csv添加日志 | 日志信息4个字段 |
| `get_config(param_name)` | 读取config.csv配置 | param_name: 参数名(可选) |
| `get_users()` | 读取所有用户 | 无 |
| `get_logs()` | 读取所有日志 | 无 |
| `verify_user(username, password)` | 验证用户登录 | 用户名和密码 |

**验证结果**：11个 pytest 单元测试全部通过

---

### 任务5：阶段一交付 - 已完成

**完成时间**：2026-07-04

**交付清单**：
1. `backend/VectorStore/` - Chroma向量库目录
2. `backend/data/rules/*.csv` - 4个CSV数据表
3. `backend/src/tools/calculator.py` - 薪资计算模块
4. `backend/src/tools/file_manager.py` - 文件管理工具模块

**测试结果**：30个 pytest 测试全部通过

---

## 代码文件说明

### 核心脚本

#### build_vectorstore.py
```python
# 位置：backend/build_vectorstore.py
# 功能：构建向量库

# 主要函数：
- get_loader(file_path)           # 根据文件后缀选择加载器
- load_documents(data_dir)        # 加载data/raw/目录下所有文档
- split_documents(documents)      # 切片并注入metadata(source, page)
- build_vector_store(documents)   # 构建Chroma向量库

# 运行方式：
python backend/build_vectorstore.py
```

---

### 工具模块

#### calculator.py
```python
# 位置：backend/src/tools/calculator.py
# 功能：薪资计算和表格提取

# 核心函数：
calculate_deduction(salary: float, late_count: int) -> float
# 说明：计算迟到扣款，每次迟到扣50元

calculate_leave_deduction(salary: float, leave_days: float) -> float
# 说明：计算事假扣款，公式：薪资/21.75*天数

calculate_overtime_pay(salary: float, overtime_hours: float, multiplier: float = 1.5) -> float
# 说明：计算加班费，公式：时薪*小时*倍率
# 倍率：工作日1.5，周末2.0，节假日3.0

calculate_net_salary(base_salary, performance_salary, allowance, late_count, leave_days, overtime_hours) -> dict
# 说明：综合计算净工资，返回完整工资条
```

#### file_manager.py
```python
# 位置：backend/src/tools/file_manager.py
# 功能：向量库和CSV文件管理

# 向量库操作：
delete_doc_vector(filename: str) -> int
# 说明：删除指定文档的所有向量，返回删除数量

# 用户管理：
add_user(username, password, email, department) -> dict
# 说明：添加新用户，自动生成用户ID(U001, U002...)

verify_user(username: str, password: str) -> dict | None
# 说明：验证用户登录，成功返回用户信息，失败返回None

# 日志管理：
save_chat_log(user_id, question, answer, kb_source) -> dict
# 说明：保存对话日志，自动生成日志ID和时间戳

# 配置读取：
get_config(param_name: str = None) -> dict | list
# 说明：读取系统配置，不传参数返回全部配置
```

---

## 数据表结构

### salary.csv
| 字段 | 说明 | 示例 |
|------|------|------|
| 员工ID | 唯一标识 | E001 |
| 姓名 | 员工姓名 | 张三 |
| 基本工资 | 月基本工资 | 8000 |
| 绩效工资 | 绩效奖金 | 2000 |
| 岗位津贴 | 岗位补贴 | 500 |
| 扣除项 | 已扣除金额 | 0 |

### users.csv
| 字段 | 说明 | 示例 |
|------|------|------|
| 用户ID | 唯一标识 | U001 |
| 用户名 | 登录名 | admin |
| 密码 | 登录密码 | admin123 |
| 邮箱 | 联系邮箱 | admin@company.com |
| 部门 | 所属部门 | IT部 |

### logs.csv
| 字段 | 说明 | 示例 |
|------|------|------|
| 日志ID | 唯一标识 | L001 |
| 用户ID | 提问用户 | U001 |
| 问题 | 用户问题 | 员工入职流程是什么？ |
| 回答 | 机器人回答 | 新员工入职需经过... |
| 知识库来源 | 引用文件 | 员工手册.pdf |
| 时间戳 | 记录时间 | 2026-07-04 14:30:00 |

### config.csv
| 参数名 | 参数值 | 描述 |
|--------|--------|------|
| chunk_size | 512 | 文本切片大小 |
| chunk_overlap | 50 | 文本切片重叠 |
| embedding_model | text-embedding-v4 | 向量化模型 |
| llm_model | qwen3.7-plus | 大语言模型 |
| max_response_length | 2000 | 最大回答字数 |
| timeout_seconds | 30 | API超时时间 |

---

## 环境配置

### 虚拟环境
```bash
# 激活虚拟环境
.\.venv\Scripts\activate

# 安装依赖
pip install langchain langchain-community langchain-text-splitters langchain-chroma dashscope chromadb pdfplumber pypdf docx2txt pandas numpy pytest fastapi
```

### 环境变量
```bash
# 设置API_KEY（百炼平台）
set API_KEY=your_api_key_here
```

### 运行测试
```bash
# 运行所有测试
python -m pytest backend/tests/ -v

# 运行指定测试
python -m pytest backend/tests/test_calculator.py -v
python -m pytest backend/tests/test_file_manager.py -v
```

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12.10 | 运行环境 |
| LangChain | 1.3.11 | RAG框架 |
| ChromaDB | 1.5.9 | 向量数据库 |
| DashScope | 1.26.2 | 阿里云AI API |
| Pandas | 3.0.3 | 数据处理 |
| pdfplumber | 0.11.10 | PDF解析 |
| Pytest | 9.1.1 | 单元测试 |

---

## 遇到的问题与解决方案

1. **编码问题**：Windows控制台默认GBK编码导致Unicode错误
   - 解决：设置 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")`

2. **虚拟环境依赖**：项目.venv初始为空
   - 解决：重新安装所有必需依赖包

3. **PDF表格提取**：员工手册中无标准薪资表格
   - 解决：使用默认薪资结构作为示例数据

---

## 后续工作（给组长的建议）

1. 在阶段二中使用 `file_manager.py` 的函数封装API接口
2. 在阶段二中使用 `calculator.py` 的函数实现Function Call
3. 读取 `config.csv` 配置参数控制行为（如超时、最大字数等）
