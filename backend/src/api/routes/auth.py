"""认证接口路由"""

from pydantic import BaseModel

from fastapi import APIRouter, HTTPException

from src.tools.file_manager import verify_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


class LoginRequest(BaseModel):
    """登录请求体"""

    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应体"""

    success: bool
    message: str
    user: dict | None = None


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    """用户登录认证接口

    验证用户名和密码，成功返回用户信息。

    Args:
        request: 包含username和password的登录请求

    Returns:
        登录结果，包含用户信息
    """
    user = verify_user(request.username, request.password)
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 返回用户信息（不包含密码）
    user_info = {
        "用户ID": user.get("用户ID", ""),
        "用户名": user.get("用户名", ""),
        "邮箱": user.get("邮箱", ""),
        "部门": user.get("部门", ""),
    }

    return LoginResponse(success=True, message="登录成功", user=user_info)
