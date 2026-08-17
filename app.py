"""
app.py - AI Partner 主界面
Gradio 应用入口，负责页面布局、用户交互和状态管理。
"""

import gradio as gr
from datetime import datetime

from config import DEFAULT_NICK_NAME, DEFAULT_NATURE, SESSION_TITLE_MAX_LENGTH
from session import save_session, list_sessions, load_session, delete_session
from chat import create_client, send_message


# ── 全局状态 ───────────────────────────────────────────────
_current_session_id: str = datetime.now().strftime("%Y%m%d%H%M%S")
_current_nick: str = DEFAULT_NICK_NAME
_current_nature: str = DEFAULT_NATURE
_current_title: str = ""


def _new_session_id() -> str:
    """生成新的会话 ID。"""
    return datetime.now().strftime("%Y%m%d%H%M%S")


# ── 回调函数 ───────────────────────────────────────────────

def create_new_session() -> tuple[list, list, str, str, str, gr.Dropdown]:
    """
    新建会话：保存当前会话（如有消息），清空聊天界面。

    Returns:
        (空聊天历史, 空消息列表, 新会话ID, 默认昵称, 默认性格, 刷新的会话下拉框)
    """
    global _current_session_id, _current_nick, _current_nature, _current_title

    # 保存当前会话（如果有消息）
    if _current_title:  # 有标题说明有过对话
        # 这里不自动保存，由用户手动管理
        pass

    _current_session_id = _new_session_id()
    _current_title = ""

    dropdown = gr.Dropdown(
        choices=_get_session_choices(),
        value=None,
        label="加载历史会话",
    )
    return [], [], _current_session_id, _current_nick, _current_nature, dropdown


def delete_current_session(
    messages: list,
) -> tuple[list, list, str, str, str, gr.Dropdown]:
    """
    删除当前会话文件并清空界面。

    Args:
        messages: 当前消息列表（用于判断是否有内容可删）

    Returns:
        (空聊天历史, 空消息列表, 新会话ID, 默认昵称, 默认性格, 刷新的会话下拉框)
    """
    global _current_session_id, _current_title

    if messages:
        delete_session(_current_session_id)

    _current_session_id = _new_session_id()
    _current_title = ""

    dropdown = gr.Dropdown(
        choices=_get_session_choices(),
        value=None,
        label="加载历史会话",
    )
    return [], [], _current_session_id, _current_nick, _current_nature, dropdown


def _get_session_choices() -> list[tuple[str, str]]:
    """
    获取历史会话列表，返回 Gradio Dropdown 所需的 (显示名, 值) 元组列表。
    """
    sessions = list_sessions()
    choices = []
    for s in sessions:
        sid = s.get("session_id", "")
        title = s.get("session_title", "") or s.get("session_name", "未命名会话")
        date = s.get("session_date", "")
        count = len(s.get("session_messages", []))
        label = f"{title} ({count}条) - {date}"
        choices.append((label, sid))
    return choices


def load_session_handler(
    session_id: str,
) -> tuple[list, list, str, str, str, gr.Dropdown]:
    """
    从文件加载历史会话。

    Args:
        session_id: 要加载的会话 ID

    Returns:
        (聊天历史, 消息列表, 会话ID, 昵称, 性格, 刷新后的会话下拉框)
    """
    global _current_session_id, _current_nick, _current_nature, _current_title

    dropdown = gr.Dropdown(
        choices=_get_session_choices(), value=session_id, label="加载历史会话"
    )

    if not session_id:
        return gr.update(), gr.update(), _current_session_id, _current_nick, _current_nature, dropdown

    loaded = load_session(session_id)
    if not loaded:
        return gr.update(), gr.update(), _current_session_id, _current_nick, _current_nature, dropdown

    _current_session_id = loaded["session_id"]
    _current_nick = loaded.get("session_name", DEFAULT_NICK_NAME)
    _current_nature = loaded.get("session_nature", DEFAULT_NATURE)
    _current_title = loaded.get("session_title", "")

    # 构建 Chatbot 显示历史（不含 system 消息）
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in loaded["session_messages"]
        if m["role"] in ("user", "assistant")
    ]

    return chat_history, loaded["session_messages"], _current_session_id, _current_nick, _current_nature, dropdown


def chat(
    message: str,
    history: list,
    messages: list,
    nick: str,
    nature: str,
) -> tuple[list, list, str, str, gr.Dropdown]:
    """
    处理用户输入，调用 AI 并返回更新后的聊天历史。

    Args:
        message: 用户输入的消息
        history: Chatbot 当前显示历史
        messages: 完整消息列表（含 system）
        nick: AI 昵称
        nature: AI 性格描述

    Returns:
        (更新后的聊天历史, 更新后的消息列表, 昵称, 性格, 刷新后的会话下拉框)
    """
    global _current_nick, _current_nature, _current_title

    # 更新全局设置
    _current_nick = nick or DEFAULT_NICK_NAME
    _current_nature = nature or DEFAULT_NATURE

    # 输入校验
    if not message or not message.strip():
        return history, messages, _current_nick, _current_nature, gr.Dropdown(
            choices=_get_session_choices(), value=None, label="加载历史会话"
        )

    # 自动生成会话标题
    if not _current_title:
        title = message[:SESSION_TITLE_MAX_LENGTH]
        if len(message) > SESSION_TITLE_MAX_LENGTH:
            title += "..."
        _current_title = title

    # 追加用户消息
    messages.append({"role": "user", "content": message})

    # 调用 AI
    try:
        client = create_client()
        reply, error = send_message(client, messages, _current_nick, _current_nature)

        if error:
            # 回滚用户消息
            messages.pop()
            error_history = list(history) + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": f"⚠️ {error}"},
            ]
            return error_history, messages, _current_nick, _current_nature, gr.Dropdown(
                choices=_get_session_choices(), value=None, label="加载历史会话"
            )

        # 追加 AI 回复
        messages.append({"role": "assistant", "content": reply})

        # 保存会话到文件
        save_session(
            session_id=_current_session_id,
            messages=messages,
            nick_name=_current_nick,
            nature=_current_nature,
            session_title=_current_title,
        )

        # 构建新的聊天历史
        new_history = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in ("user", "assistant")
        ]

        return new_history, messages, _current_nick, _current_nature, gr.Dropdown(
            choices=_get_session_choices(), value=None, label="加载历史会话"
        )

    except ValueError as e:
        messages.pop()  # 回滚
        error_history = list(history) + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": f"⚠️ {str(e)}"},
        ]
        return error_history, messages, _current_nick, _current_nature, gr.Dropdown(
            choices=_get_session_choices(), value=None, label="加载历史会话"
        )

    except Exception as e:
        messages.pop()  # 回滚
        error_history = list(history) + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": f"️ 发生未知错误：{e}"},
        ]
        return error_history, messages, _current_nick, _current_nature, gr.Dropdown(
            choices=_get_session_choices(), value=None, label="加载历史会话"
        )


# ── 构建 Gradio 界面 ───────────────────────────────────────

with gr.Blocks(title="AI Partner") as demo:

    gr.Markdown("# AI Partner")

    with gr.Row():
        # ── 侧边栏 ─────────────────────────────────────────
        with gr.Column(scale=1, min_width=280):
            gr.Markdown("### Settings")
            gr.Markdown("Configure your AI Partner settings below.")

            nick_input = gr.Textbox(
                label="Nickname",
                value=DEFAULT_NICK_NAME,
                placeholder="给你的AI伴侣起个名字",
            )
            nature_input = gr.Textbox(
                label="Nature",
                value=DEFAULT_NATURE,
                placeholder="描述AI伴侣的性格特点",
                lines=4,
            )

            gr.Markdown("---")

            btn_new = gr.Button("新建会话", variant="primary", size="sm")
            btn_delete = gr.Button("删除当前会话", variant="stop", size="sm")

            gr.Markdown("---")
            gr.Markdown("### 历史会话")

            session_dropdown = gr.Dropdown(
                choices=_get_session_choices(),
                value=None,
                label="加载历史会话",
                interactive=True,
            )
            btn_load = gr.Button("加载", size="sm")

        # ── 主聊天区 ───────────────────────────────────────
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="AI Partner",
                height=500,
                render_markdown=True,
            )
            msg_input = gr.Textbox(
                label="输入你想说的话...",
                placeholder="输入你想说的话...",
                lines=1,
            )

    # ── State 组件（存储完整消息列表，含 system prompt）──
    messages_state = gr.State(value=[])

    # ── 会话 ID 隐藏组件（用于回调中识别当前会话）──────────
    session_id_state = gr.State(value=_current_session_id)
    nick_state = gr.State(value=DEFAULT_NICK_NAME)
    nature_state = gr.State(value=DEFAULT_NATURE)

    # ── 事件绑定 ───────────────────────────────────────────

    # 发送消息
    msg_input.submit(
        fn=chat,
        inputs=[msg_input, chatbot, messages_state, nick_input, nature_input],
        outputs=[chatbot, messages_state, nick_state, nature_state, session_dropdown],
    )

    # 新建会话
    btn_new.click(
        fn=create_new_session,
        inputs=[],
        outputs=[chatbot, messages_state, session_id_state, nick_state, nature_state, session_dropdown],
    )

    # 删除当前会话
    btn_delete.click(
        fn=delete_current_session,
        inputs=[messages_state],
        outputs=[chatbot, messages_state, session_id_state, nick_state, nature_state, session_dropdown],
    )

    # 加载历史会话
    btn_load.click(
        fn=load_session_handler,
        inputs=[session_dropdown],
        outputs=[chatbot, messages_state, session_id_state, nick_state, nature_state, session_dropdown],
    )


# ── 启动 ───────────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=8501,
        theme=gr.themes.Soft(),
        css=".main-chat { max-height: 70vh; }",
    )
