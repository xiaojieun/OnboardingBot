// 后端未启动时使用的兜底Mock数据

export const mockDocs = [
  { filename: '员工手册.pdf', size: 102400, type: '.pdf' },
  { filename: '入职指南.txt', size: 8192, type: '.txt' },
  { filename: '考勤制度.md', size: 4096, type: '.md' },
]

export const mockUsers = [
  { 用户ID: 'U001', 用户名: 'admin', 邮箱: 'admin@company.com', 部门: 'IT部' },
  { 用户ID: 'U002', 用户名: 'zhangsan', 邮箱: 'zhangsan@company.com', 部门: '人力资源部' },
  { 用户ID: 'U003', 用户名: 'lisi', 邮箱: 'lisi@company.com', 部门: '行政部' },
]

export const mockLogs = [
  { 日志ID: 'L001', 用户ID: 'U001', 问题: '员工入职流程是什么？', 回答: '新员工入职需经过资料登记、培训安排等环节。【来源:员工手册.pdf-第3页】', 知识库来源: '员工手册.pdf', 时间戳: '2026-07-04 16:25:59' },
  { 日志ID: 'L002', 用户ID: 'U001', 问题: '迟到扣款怎么算？', 回答: '每次迟到扣50元，可由系统计算。【来源:员工手册.pdf-第5页】', 知识库来源: '员工手册.pdf', 时间戳: '2026-07-04 16:26:20' },
]

export const mockConfig = [
  { 参数名: 'chunk_size', 参数值: '512', 描述: '文本切片大小' },
  { 参数名: 'chunk_overlap', 参数值: '50', 描述: '文本切片重叠大小' },
  { 参数名: 'embedding_model', 参数值: 'text-embedding-v4', 描述: '向量化模型名称' },
  { 参数名: 'llm_model', 参数值: 'qwen3.7-plus', 描述: '大语言模型名称' },
  { 参数名: 'max_response_length', 参数值: '2000', 描述: '单轮回答最大字数' },
  { 参数名: 'timeout_seconds', 参数值: '30', 描述: 'API调用超时时间' },
]
