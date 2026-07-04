"""向量库和CSV文件管理工具函数"""

import csv
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from langchain_chroma import Chroma

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from langchain_community.embeddings import DashScopeEmbeddings


# 文件路径
DATA_DIR = Path(__file__).parent.parent.parent / "data"
RULES_DIR = DATA_DIR / "rules"
VECTOR_STORE_DIR = Path(__file__).parent.parent.parent / "VectorStore"

USERS_CSV = RULES_DIR / "users.csv"
LOGS_CSV = RULES_DIR / "logs.csv"
CONFIG_CSV = RULES_DIR / "config.csv"

EMBEDDING_MODEL = "text-embedding-v4"


def get_vector_store() -> Chroma:
    """初始化并返回Chroma向量库"""
    embeddings = DashScopeEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(
        persist_directory=str(VECTOR_STORE_DIR),
        embedding_function=embeddings,
    )


def delete_doc_vector(filename: str) -> int:
    """从Chroma向量库删除指定文档的所有向量

    Args:
        filename: 要删除的文档文件名

    Returns:
        删除的向量数量
    """
    vector_store = get_vector_store()

    # 查询匹配source文件名的文档
    results = vector_store.get(
        where={"source": filename},
    )

    if results and results["ids"]:
        num_deleted = len(results["ids"])
        vector_store.delete(ids=results["ids"])
        print(f"已删除文档 {filename} 的 {num_deleted} 个向量")
        return num_deleted

    print(f"未找到文档 {filename} 的向量")
    return 0


def add_user(
    username: str,
    password: str,
    email: str,
    department: str,
) -> dict[str, str]:
    """向users.csv添加新用户

    Args:
        username: 用户名
        password: 密码
        email: 邮箱
        department: 部门

    Returns:
        新用户信息字典
    """
    RULES_DIR.mkdir(parents=True, exist_ok=True)

    # 读取现有用户以生成新ID
    existing_users: list[dict[str, str]] = []
    if USERS_CSV.exists():
        df = pd.read_csv(USERS_CSV, dtype=str)
        existing_users = df.to_dict("records")

    # 生成新用户ID
    max_id = 0
    for user in existing_users:
        user_id = user.get("用户ID", "U000")
        try:
            num = int(user_id.replace("U", ""))
            max_id = max(max_id, num)
        except ValueError:
            continue

    new_user_id = f"U{max_id + 1:03d}"

    new_user = {
        "用户ID": new_user_id,
        "用户名": username,
        "密码": password,
        "邮箱": email,
        "部门": department,
    }

    # 追加到CSV
    fieldnames = ["用户ID", "用户名", "密码", "邮箱", "部门"]
    file_exists = USERS_CSV.exists()

    with open(USERS_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(new_user)

    print(f"用户已添加: {new_user_id} - {username}")
    return new_user


def save_chat_log(
    user_id: str,
    question: str,
    answer: str,
    kb_source: str,
) -> dict[str, str]:
    """向logs.csv保存对话日志

    Args:
        user_id: 用户ID
        question: 用户问题
        answer: 机器人回答
        kb_source: 知识库来源

    Returns:
        日志记录字典
    """
    RULES_DIR.mkdir(parents=True, exist_ok=True)

    # 读取现有日志以生成新ID
    existing_logs: list[dict[str, str]] = []
    if LOGS_CSV.exists():
        df = pd.read_csv(LOGS_CSV, dtype=str)
        existing_logs = df.to_dict("records")

    # 生成新日志ID
    max_id = 0
    for log in existing_logs:
        log_id = log.get("日志ID", "L000")
        try:
            num = int(log_id.replace("L", ""))
            max_id = max(max_id, num)
        except ValueError:
            continue

    new_log_id = f"L{max_id + 1:03d}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_log = {
        "日志ID": new_log_id,
        "用户ID": user_id,
        "问题": question,
        "回答": answer,
        "知识库来源": kb_source,
        "时间戳": timestamp,
    }

    # 追加到CSV
    fieldnames = ["日志ID", "用户ID", "问题", "回答", "知识库来源", "时间戳"]
    file_exists = LOGS_CSV.exists()

    with open(LOGS_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(new_log)

    print(f"日志已保存: {new_log_id}")
    return new_log


def get_config(param_name: Optional[str] = None) -> dict[str, str] | list[dict[str, str]]:
    """从config.csv读取配置

    Args:
        param_name: 要读取的参数名，为None时返回所有配置

    Returns:
        参数字典或所有配置列表
    """
    if not CONFIG_CSV.exists():
        return {} if param_name else []

    df = pd.read_csv(CONFIG_CSV, dtype=str)

    if param_name:
        row = df[df["参数名"] == param_name]
        if row.empty:
            return {}
        return row.iloc[0].to_dict()

    return df.to_dict("records")


def get_users() -> list[dict[str, str]]:
    """读取所有用户

    Returns:
        用户字典列表
    """
    if not USERS_CSV.exists():
        return []

    df = pd.read_csv(USERS_CSV, dtype=str)
    return df.to_dict("records")


def get_logs() -> list[dict[str, str]]:
    """读取所有对话日志

    Returns:
        日志字典列表
    """
    if not LOGS_CSV.exists():
        return []

    df = pd.read_csv(LOGS_CSV, dtype=str)
    return df.to_dict("records")


def verify_user(username: str, password: str) -> Optional[dict[str, str]]:
    """验证用户登录

    Args:
        username: 用户名
        password: 密码

    Returns:
        验证成功返回用户信息，失败返回None
    """
    users = get_users()
    for user in users:
        if user.get("用户名") == username and user.get("密码") == password:
            return user
    return None
