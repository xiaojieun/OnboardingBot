"""RAG检索链构建模块"""

import os
import sys
from operator import itemgetter
from pathlib import Path
from typing import Optional

# 确保backend目录在路径中
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.core.prompts import HR_SYSTEM_PROMPT, CONTEXT_PROMPT
from src.core.tools import ALL_TOOLS
from src.tools.file_manager import get_config


# 路径配置
BACKEND_DIR = Path(__file__).parent.parent.parent
VECTOR_STORE_DIR = BACKEND_DIR / "VectorStore"
EMBEDDING_MODEL = "text-embedding-v4"
LLM_MODEL = "qwen3.7-plus"

# 敏感词列表
SENSITIVE_WORDS: list[str] = []

# 会话历史存储（内存中）
_store: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """获取会话历史"""
    if session_id not in _store:
        _store[session_id] = InMemoryChatMessageHistory()
    return _store[session_id]


def clear_session_history(session_id: str) -> None:
    """清除指定会话历史"""
    if session_id in _store:
        del _store[session_id]


def filter_sensitive_words(text: str) -> str:
    """过滤敏感词，替换为*"""
    filtered = text
    for word in SENSITIVE_WORDS:
        filtered = filtered.replace(word, "*" * len(word))
    return filtered


def get_llm_config() -> dict[str, str]:
    """从config.csv读取LLM相关配置"""
    config = {
        "llm_model": LLM_MODEL,
        "max_response_length": "2000",
        "timeout_seconds": "30",
    }
    try:
        csv_config = get_config()
        if isinstance(csv_config, list):
            for item in csv_config:
                name = item.get("参数名", "")
                value = item.get("参数值", "")
                if name == "llm_model":
                    config["llm_model"] = value
                elif name == "max_response_length":
                    config["max_response_length"] = value
                elif name == "timeout_seconds":
                    config["timeout_seconds"] = value
    except Exception:
        pass
    return config


def _format_docs(docs: list[Document]) -> str:
    """将检索到的文档格式化为上下文字符串"""
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "未知")
        page = doc.metadata.get("page", 0)
        parts.append(f"[来源:{source}-第{page}页] {doc.page_content}")
    return "\n\n".join(parts)


def build_vector_retriever():
    """加载向量库并返回retriever"""
    embeddings = DashScopeEmbeddings(model=EMBEDDING_MODEL)
    vector_store = Chroma(
        persist_directory=str(VECTOR_STORE_DIR),
        embedding_function=embeddings,
    )
    return vector_store.as_retriever(search_kwargs={"k": 5})


def build_rag_chain() -> RunnableWithMessageHistory:
    """构建带Function Call和多轮对话记忆的RAG链路

    使用LCEL管道语法构建完整的RAG链路，支持：
    - 向量检索（Top-5）
    - Function Call工具调用（薪资计算）
    - 多轮对话记忆
    - 引用溯源标注

    Returns:
        可运行的多轮对话RAG链
    """
    # 读取配置
    llm_config = get_llm_config()
    max_response_length = llm_config["max_response_length"]

    # 初始化LLM（绑定工具）
    api_key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("API_KEY")
    llm = ChatOpenAI(
        model=llm_config["llm_model"],
        api_key=api_key,
        temperature=0.3,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    # 构建检索器
    retriever = build_vector_retriever()

    # 构建Prompt模板
    # 系统消息中包含引用溯源指令和字数限制
    system_prompt = (
        "你是一个专业的新员工入职助手。\n"
        "所有回答必须基于提供的知识库内容，不要编造信息。\n"
        "如果知识库中没有相关信息，告知用户建议咨询HR部门。\n"
        "回答末尾必须统一标注引用来源，格式：【来源:文件名-第X页】\n"
        "涉及薪资计算时使用提供的工具获取精确结果。\n"
        f"回复字数不超过{max_response_length}字。"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "human",
                "以下是相关知识库内容：\n\n{context}\n\n用户问题：{input}",
            ),
        ]
    )

    # 使用LCEL构建检索链
    # 1. 检索文档并格式化上下文
    # 2. 传入prompt
    # 3. 调用LLM（含工具）
    rag_chain_from_docs = (
        RunnablePassthrough.assign(
            context=(lambda x: _format_docs(x["context"]))
        )
        | prompt
        | llm_with_tools
    )

    # 构建完整链路：检索 + 生成
    rag_chain_with_source = RunnableParallel(
        {
            "context": itemgetter("input") | retriever,
            "input": itemgetter("input"),
            "chat_history": itemgetter("chat_history"),
        }
    ).assign(answer=rag_chain_from_docs)

    # 包装多轮对话记忆
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain_with_source,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return conversational_rag_chain


def get_answer(question: str, session_id: str = "default") -> str:
    """同步获取RAG回答（用于测试和非流式场景）

    Args:
        question: 用户问题
        session_id: 会话ID

    Returns:
        助手回答文本
    """
    filtered_question = filter_sensitive_words(question)

    chain = build_rag_chain()
    result = chain.invoke(
        {"input": filtered_question},
        config={"configurable": {"session_id": session_id}},
    )
    answer = result.get("answer", None)
    if answer is None:
        return "抱歉，无法获取回答"
    content = answer.content if hasattr(answer, "content") else str(answer)
    return content


def get_stream_answer(question: str, session_id: str = "default"):
    """流式获取RAG回答（生成器）

    手动实现流式输出，包含：
    - 敏感词过滤
    - 向量检索
    - 多轮对话历史
    - 字数截断控制

    Args:
        question: 用户问题
        session_id: 会话ID

    Yields:
        逐块输出文本
    """
    filtered_question = filter_sensitive_words(question)

    llm_config = get_llm_config()
    max_response_length = int(llm_config["max_response_length"])

    api_key = os.environ.get("API_KEY")
    # 初始化LLM
    llm = ChatOpenAI(
        model=llm_config["llm_model"],
        api_key=api_key,
        temperature=0.3,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # 检索相关文档
    retriever = build_vector_retriever()
    docs: list = retriever.invoke(filtered_question)

    # 获取历史
    history = get_session_history(session_id)
    history_text = ""
    for msg in history.messages:
        role = "用户" if isinstance(msg, HumanMessage) else "助手"
        history_text += f"{role}: {msg.content}\n"

    # 构建上下文
    context = _format_docs(docs)

    # 构建消息
    system_prompt = (
        "你是一个专业的新员工入职助手。\n"
        "所有回答必须基于提供的知识库内容，不要编造信息。\n"
        "如果知识库中没有相关信息，告知用户建议咨询HR部门。\n"
        "回答末尾必须统一标注引用来源，格式：【来源:文件名-第X页】\n"
        "涉及薪资计算时使用提供的工具获取精确结果。\n"
        f"回复字数不超过{max_response_length}字。"
    )

    messages: list = [
        SystemMessage(content=system_prompt),
    ]

    # 添加历史消息
    for msg in history.messages:
        messages.append(msg)

    # 添加当前问题
    messages.append(
        HumanMessage(
            content=f"以下是相关知识库内容：\n\n{context}\n\n用户问题：{filtered_question}"
        )
    )

    # 流式输出
    full_response = ""
    for chunk in llm.stream(messages):
        content = chunk.content if hasattr(chunk, "content") else str(chunk)
        if content:
            full_response += content
            yield content

    # 截断超长回复
    if len(full_response) > max_response_length:
        full_response = full_response[:max_response_length] + "\n...回答已超过字数限制，已截断"

    # 记录历史
    history.add_message(HumanMessage(content=question))
    history.add_message(AIMessage(content=full_response))
