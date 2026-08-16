"""
config.py - 项目配置与常量定义
集中管理所有配置项，方便统一修改和维护。
"""

import os

# ── API 配置 ──────────────────────────────────────────────
DEEPSEEK_API_KEY: str = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
MODEL_NAME: str = "deepseek-v4-pro"

# ── 系统提示词模板 ─────────────────────────────────────────
SYSTEM_PROMPT_TEMPLATE: str = """\
You are a helpful assistant named {name}.
Your personality is: {nature}.
Please answer the user's questions in a concise and informative manner.
"""

# ── 会话存储配置 ───────────────────────────────────────────
SESSION_DATA_DIR: str = "session_data"
SESSION_TITLE_MAX_LENGTH: int = 15

# ── 默认值 ─────────────────────────────────────────────────
DEFAULT_NICK_NAME: str = "AI Partner"
DEFAULT_NATURE: str = "You are a helpful assistant."
