"""管理后台接口路由"""

from pathlib import Path

from pydantic import BaseModel

from fastapi import APIRouter, HTTPException

from src.tools.file_manager import (
    delete_doc_vector,
    get_config,
    get_logs,
    get_users,
)

router = APIRouter(prefix="/api", tags=["管理"])


class DeleteDocRequest(BaseModel):
    """删除文档请求体"""

    filename: str


class DeleteDocResponse(BaseModel):
    """删除文档响应体"""

    success: bool
    message: str
    deleted_count: int = 0


# 文档列表
@router.get("/docs")
def list_documents():
    """获取知识库文档列表

    Returns:
        文档列表
    """
    raw_dir = Path(__file__).parent.parent.parent.parent / "data" / "raw"
    docs = []
    if raw_dir.exists():
        for f in raw_dir.iterdir():
            if f.is_file():
                docs.append(
                    {
                        "filename": f.name,
                        "size": f.stat().st_size,
                        "type": f.suffix.lower(),
                    }
                )
    return {"success": True, "documents": docs}


@router.post("/docs/delete", response_model=DeleteDocResponse)
def delete_document(request: DeleteDocRequest) -> DeleteDocResponse:
    """删除指定文档及其向量数据

    从Chroma向量库中删除该文档的所有向量块。

    Args:
        request: 包含要删除的文档文件名

    Returns:
        删除结果
    """
    try:
        count = delete_doc_vector(request.filename)
        if count > 0:
            msg = f"已删除文档 {request.filename} 的 {count} 个向量块"
        else:
            msg = f"未找到文档 {request.filename} 的向量数据"
        return DeleteDocResponse(success=True, message=msg, deleted_count=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# 日志查询
@router.get("/logs")
def query_logs():
    """获取所有对话日志

    Returns:
        日志列表
    """
    logs = get_logs()
    return {"success": True, "logs": logs, "total": len(logs)}


# 用户列表
@router.get("/users")
def list_users():
    """获取所有用户列表（不含密码）

    Returns:
        用户列表
    """
    users = get_users()
    safe_users = []
    for u in users:
        safe_users.append(
            {
                "用户ID": u.get("用户ID", ""),
                "用户名": u.get("用户名", ""),
                "邮箱": u.get("邮箱", ""),
                "部门": u.get("部门", ""),
            }
        )
    return {"success": True, "users": safe_users, "total": len(safe_users)}


# 系统配置查询
@router.get("/config")
def query_config():
    """获取系统配置参数

    Returns:
        配置列表
    """
    config = get_config()
    return {"success": True, "config": config}
