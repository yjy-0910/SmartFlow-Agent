"""
chat.py - 对话交互模块
封装 OpenAI/DeepSeek API 调用逻辑，包含完善的错误处理。
"""

from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError
from typing import Optional

from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    MODEL_NAME,
    SYSTEM_PROMPT_TEMPLATE,
)


def create_client() -> OpenAI:
    """
    创建 OpenAI 客户端实例。

    Raises:
        ValueError: 当 API Key 未配置时抛出
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError(
            "未配置 DEEPSEEK_API_KEY。"
            "请在环境变量中设置，或在 Streamlit Cloud 的 Secrets 中添加。"
        )

    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
    )


def send_message(
    client: OpenAI,
    messages: list[dict],
    nick_name: str,
    nature: str,
) -> tuple[Optional[str], Optional[str]]:
    """
    发送消息并获取 AI 回复。

    Args:
        client: OpenAI 客户端实例
        messages: 当前对话消息列表
        nick_name: AI 伴侣昵称
        nature: AI 伴侣性格描述

    Returns:
        (回复内容, 错误信息) 元组。成功时错误信息为 None，失败时回复内容为 None。
    """
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(name=nick_name, nature=nature)

    full_messages = [
        {"role": "system", "content": system_prompt},
        *messages,
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=full_messages,
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )
        return response.choices[0].message.content, None

    except RateLimitError:
        return None, "请求过于频繁，请稍后再试。"

    except APITimeoutError:
        return None, "请求超时，请检查网络连接后重试。"

    except APIConnectionError:
        return None, "无法连接到 API 服务，请检查网络或 API 地址是否正确。"

    except APIError as e:
        return None, f"API 调用失败：{e}"

    except Exception as e:
        return None, f"发生未知错误：{e}"
