"""file_manager模块的单元测试"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# 添加backend到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.file_manager import (
    add_user,
    delete_doc_vector,
    get_config,
    get_logs,
    get_users,
    save_chat_log,
    verify_user,
)


class TestUserManagement:
    """用户管理功能测试"""

    def test_get_users(self) -> None:
        """测试获取所有用户"""
        users = get_users()
        assert isinstance(users, list)
        assert len(users) > 0
        assert "用户ID" in users[0]
        assert "用户名" in users[0]

    def test_add_user(self) -> None:
        """测试添加用户"""
        new_user = add_user(
            username="testuser",
            password="test123",
            email="test@company.com",
            department="测试部",
        )
        assert "用户ID" in new_user
        assert new_user["用户名"] == "testuser"
        assert new_user["部门"] == "测试部"

        # 验证用户已添加
        users = get_users()
        usernames = [u["用户名"] for u in users]
        assert "testuser" in usernames

    def test_verify_user_success(self) -> None:
        """测试用户验证成功"""
        result = verify_user("admin", "admin123")
        assert result is not None
        assert result["用户名"] == "admin"

    def test_verify_user_failure(self) -> None:
        """测试用户验证失败"""
        result = verify_user("admin", "wrongpassword")
        assert result is None

    def test_verify_nonexistent_user(self) -> None:
        """测试验证不存在的用户"""
        result = verify_user("nonexistent", "password")
        assert result is None


class TestChatLogManagement:
    """对话日志管理功能测试"""

    def test_get_logs(self) -> None:
        """测试获取所有日志"""
        logs = get_logs()
        assert isinstance(logs, list)

    def test_save_chat_log(self) -> None:
        """测试保存对话日志"""
        initial_count = len(get_logs())

        new_log = save_chat_log(
            user_id="U001",
            question="测试问题",
            answer="测试回答",
            kb_source="员工手册.pdf",
        )
        assert "日志ID" in new_log
        assert new_log["用户ID"] == "U001"
        assert new_log["问题"] == "测试问题"

        # 验证日志已保存
        logs = get_logs()
        assert len(logs) == initial_count + 1


class TestConfigManagement:
    """配置管理功能测试"""

    def test_get_all_config(self) -> None:
        """测试获取所有配置"""
        config = get_config()
        assert isinstance(config, list)
        assert len(config) > 0
        assert "参数名" in config[0]
        assert "参数值" in config[0]

    def test_get_specific_config(self) -> None:
        """测试获取指定配置"""
        config = get_config("chunk_size")
        assert isinstance(config, dict)
        assert config["参数名"] == "chunk_size"
        assert config["参数值"] == "512"

    def test_get_nonexistent_config(self) -> None:
        """测试获取不存在的配置"""
        config = get_config("nonexistent_param")
        assert config == {}


class TestVectorStoreOperations:
    """向量库操作测试"""

    def test_delete_doc_vector_nonexistent(self) -> None:
        """测试删除不存在文档的向量"""
        # 这不应该报错
        result = delete_doc_vector("nonexistent_file.pdf")
        assert result == 0
