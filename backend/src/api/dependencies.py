"""公共依赖"""

import os
from functools import lru_cache

from fastapi import Header, HTTPException


def verify_api_key(authorization: str = Header(default="")) -> str:
    """验证API Key鉴权

    Args:
        authorization: Authorization请求头

    Returns:
        通过验证的API Key

    Raises:
        HTTPException: 鉴权失败
    """
    expected_key = os.environ.get("API_KEY", "")
    if not expected_key:
        # 开发环境下未设置API_KEY时跳过验证
        return "dev_mode"

    # 支持 Bearer Token 格式
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization[7:]

    if token != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    return token
