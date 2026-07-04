# 入职智引系统 - 阶段一任务看板

## 环境基线

- Python 版本: 3.12.10
- LLM 模型: qwen3.7-plus (百炼 API)
- Embedding 模型: text-embedding-v4
- 鉴权方式: 系统环境变量 API_KEY (代码禁止硬编码)
- 核心框架: LangChain + Pandas + NumPy + ChromaDB + FastAPI

## 代码规范

- 全局禁止使用 emoji (代码、注释、日志、Git 提交信息)
- Python 遵循 PEP 8 风格
- 函数必须有 Type Hints 和 Docstring

## 文件结构

```
OnboardingBot/
├── backend/
│   ├── data/raw/          # 原始 PDF
│   ├── data/rules/        # CSV 规则表
│   ├── VectorStore/       # 向量库
│   ├── src/tools/         # 计算函数
│   ├── src/core/          # LangChain 链路
│   ├── src/api/           # FastAPI 接口
│   └── tests/             # 测试用例
├── frontend/              # Vue3 前端
└── docs/                  # 文档
```

---

## 成员二任务 (数据工程师)

### 任务进度

- [ ] 1. 工程基座与环境验证
- [ ] 2. PDF 知识库构建 (LangChain + ChromaDB)
- [ ] 3. 结构化数据提取与计算引擎 (Pandas + NumPy)
- [ ] 4. 阶段一交付物打包与交接

---

### 任务详情

#### 1. 工程基座与环境验证

执行动作:
- 初始化 Git 仓库
- 创建 requirements.txt (锁定 Python 3.12.10 依赖)
- 配置 .gitignore
- 编写环境检测脚本 (验证 API_KEY 和 text-embedding-v4)

验收标准:
- 环境检测脚本输出 "Environment Ready"
- Git 仓库结构规范

#### 2. PDF 知识库构建 (LangChain + ChromaDB)

执行动作:
- PyPDFLoader 读取《员工手册》
- RecursiveCharacterTextSplitter 切片 (chunk_size=512, overlap=50)
- DashScopeEmbeddings (model="text-embedding-v4") 向量化
- 写入本地 ./VectorStore/ 并持久化

验收标准:
- ./VectorStore/ 目录生成
- 重启后能成功加载
- 检索测试 Top-3 准确率达标

#### 3. 结构化数据提取与计算引擎 (Pandas + NumPy)

执行动作:
- pdfplumber 提取薪资/绩效表格
- Pandas 清洗导出为 CSV
- 编写 calculate_deduction(salary, late_count) 等纯函数
- 类型提示 + Docstring
- pytest 单元测试覆盖边界值

验收标准:
- CSV 文件无缺失
- pytest 全部通过
- 计算函数可直接 import

#### 4. 阶段一交付物打包与交接

交付清单:
1. ./VectorStore/ 目录
2. data/rules/*.csv
3. src/tools/calculator.py
4. 检索质量与风格自测报告

验收标准:
- 组长能加载向量库、读取 CSV、调用计算函数
- 组长签字确认

---

## 时间规划

| 任务 | 预计时间 | 状态 |
|------|----------|------|
| 1. 工程基座 | 0.5天 | 已完成 |
| 2. PDF 知识库 | 1天 | 进行中 |
| 3. 计算引擎 | 1天 | 待开始 |
| 4. 交付交接 | 0.5天 | 待开始 |
