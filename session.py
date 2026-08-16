"""
session.py - 会话管理模块
负责会话的保存、加载、列表和删除操作。
所有会话数据以 JSON 文件形式存储在 session_data/ 目录下。
"""

import json
import os
from datetime import datetime
from typing import Optional

from config import SESSION_DATA_DIR


def _ensure_data_dir() -> None:
    """确保会话数据目录存在，不存在则创建。"""
    if not os.path.exists(SESSION_DATA_DIR):
        os.makedirs(SESSION_DATA_DIR)


def save_session(
    session_id: str,
    messages: list[dict],
    nick_name: str,
    nature: str,
    session_title: str = "",
) -> str:
    """
    保存当前会话到 JSON 文件。

    Args:
        session_id: 会话唯一标识（时间戳格式）
        messages: 对话消息列表，每条包含 role 和 content
        nick_name: AI 伴侣的昵称
        nature: AI 伴侣的性格描述
        session_title: 会话标题（可选，默认从首条消息生成）

    Returns:
        保存的文件路径
    """
    _ensure_data_dir()

    session_data = {
        "session_id": session_id,
        "session_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_name": nick_name,
        "session_nature": nature,
        "session_messages": messages,
        "session_status": "completed",
        "session_title": session_title,
    }

    filepath = os.path.join(SESSION_DATA_DIR, f"{session_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    return filepath


def list_sessions() -> list[dict]:
    """
    列出所有已保存的会话，按时间倒序排列。

    Returns:
        会话数据字典列表，每个字典包含 session_id、session_date 等字段
    """
    sessions: list[dict] = []

    if not os.path.exists(SESSION_DATA_DIR):
        return sessions

    for filename in os.listdir(SESSION_DATA_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(SESSION_DATA_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                sessions.append(data)
        except (json.JSONDecodeError, KeyError, OSError):
            # 跳过损坏或格式错误的文件
            continue

    sessions.sort(key=lambda x: x.get("session_date", ""), reverse=True)
    return sessions


def load_session(session_id: str) -> Optional[dict]:
    """
    加载指定会话。

    Args:
        session_id: 会话唯一标识

    Returns:
        会话数据字典，文件不存在时返回 None
    """
    filepath = os.path.join(SESSION_DATA_DIR, f"{session_id}.json")

    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def delete_session(session_id: str) -> bool:
    """
    删除指定会话文件。

    Args:
        session_id: 会话唯一标识

    Returns:
        删除成功返回 True，文件不存在返回 False
    """
    filepath = os.path.join(SESSION_DATA_DIR, f"{session_id}.json")

    if not os.path.exists(filepath):
        return False

    try:
        os.remove(filepath)
        return True
    except OSError:
        return False
