"""对话接口路由"""

import json

from pydantic import BaseModel

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.core.rag_chain import filter_sensitive_words, get_stream_answer
from src.tools.file_manager import save_chat_log

router = APIRouter(prefix="/api", tags=["对话"])


class ChatRequest(BaseModel):
    """对话请求体"""

    question: str
    session_id: str = "default"
    user_id: str = "anonymous"


class ChatResponse(BaseModel):
    """非流式对话响应体"""

    answer: str
    session_id: str
    sources: list[dict] = []


@router.post("/chat")
async def chat(request: ChatRequest):
    """智能对话接口（SSE流式输出）

    接收用户问题，通过RAG链路检索知识库并生成回答，
    以Server-Sent Events格式流式返回。

    Args:
        request: 对话请求，包含问题和会话ID

    Returns:
        SSE流式响应
    """

    async def event_generator():
        full_answer = ""
        kb_source = "未知"

        try:
            for chunk in get_stream_answer(request.question, request.session_id):
                full_answer += chunk
                # SSE格式输出
                event_data = json.dumps(
                    {"type": "content", "content": chunk}, ensure_ascii=False
                )
                yield f"data: {event_data}\n\n"

            # 发送完成事件
            done_data = json.dumps(
                {"type": "done", "content": ""}, ensure_ascii=False
            )
            yield f"data: {done_data}\n\n"

            # 保存对话日志
            save_chat_log(
                user_id=request.user_id,
                question=request.question,
                answer=full_answer,
                kb_source=kb_source,
            )

        except Exception as e:
            error_data = json.dumps(
                {"type": "error", "content": f"处理请求时出错: {str(e)}"},
                ensure_ascii=False,
            )
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
