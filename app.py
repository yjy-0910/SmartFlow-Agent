"""
app.py - AI Partner 主界面
Streamlit 应用的入口，负责页面布局、用户交互和状态管理。
"""

import streamlit as st
from datetime import datetime

from config import DEFAULT_NICK_NAME, DEFAULT_NATURE, SESSION_TITLE_MAX_LENGTH
from session import save_session, list_sessions, load_session, delete_session
from chat import create_client, send_message


# ── 页面配置 ───────────────────────────────────────────────
st.set_page_config(page_title="AI Partner", page_icon=":robot_face:", layout="wide")
st.title("AI Partner")


# ── 会话状态初始化 ─────────────────────────────────────────
def init_session_state() -> None:
    """初始化 Streamlit 会话状态，确保所有必要变量存在。"""
    defaults = {
        "message": [],
        "nick_name": DEFAULT_NICK_NAME,
        "nature": DEFAULT_NATURE,
        "session_id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "session_title": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ── 渲染历史消息 ───────────────────────────────────────────
for msg in st.session_state.message:
    st.chat_message(msg["role"]).write(msg["content"])


# ── 侧边栏 ─────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Settings")
    st.write("Configure your AI Partner settings below.")

    # 用户设置输入
    nick_name = st.text_input(
        "Nickname",
        value=st.session_state.nick_name,
        placeholder="给你的AI伴侣起个名字",
        key="sidebar_nick",
    )
    nature = st.text_area(
        "Nature",
        value=st.session_state.nature,
        height=100,
        placeholder="描述AI伴侣的性格特点",
        key="sidebar_nature",
    )

    if nick_name:
        st.session_state.nick_name = nick_name
    if nature:
        st.session_state.nature = nature

    # ── 新建会话 ───────────────────────────────────────────
    st.divider()
    if st.button("新建会话", use_container_width=True):
        if st.session_state.message:
            save_session(
                st.session_state.session_id,
                st.session_state.message,
                st.session_state.nick_name,
                st.session_state.nature,
                st.session_state.session_title,
            )
        st.session_state.message = []
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.session_title = ""
        st.rerun()

    # ── 删除当前会话 ───────────────────────────────────────
    st.divider()
    if st.session_state.message:
        if st.button("删除当前会话", use_container_width=True, type="secondary"):
            delete_session(st.session_state.session_id)
            st.session_state.message = []
            st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
            st.session_state.session_title = ""
            st.rerun()

    # ─ 历史会话列表 ───────────────────────────────────────
    st.divider()
    st.subheader("历史会话")

    all_sessions = list_sessions()

    if not all_sessions:
        st.caption("暂无历史会话")
    else:
        for session in all_sessions:
            session_id = session.get("session_id", "")
            session_date = session.get("session_date", "")
            session_name = session.get("session_name", "未命名会话")
            session_title = session.get("session_title", "")
            msg_count = len(session.get("session_messages", []))

            display_name = session_title if session_title else session_name

            col_load, col_del = st.columns([4, 1])

            with col_load:
                button_label = f"{display_name} ({msg_count}条)"
                if st.button(
                    button_label,
                    key=f"session_{session_id}",
                    use_container_width=True,
                    help=f"{session_date}",
                ):
                    loaded = load_session(session_id)
                    if loaded:
                        st.session_state.session_id = loaded["session_id"]
                        st.session_state.message = loaded["session_messages"]
                        st.session_state.nick_name = loaded.get("session_name", DEFAULT_NICK_NAME)
                        st.session_state.nature = loaded.get("session_nature", DEFAULT_NATURE)
                        st.session_state.session_title = loaded.get("session_title", "")
                        st.rerun()
                    else:
                        st.error("加载会话失败，文件可能已损坏。")

            with col_del:
                if st.button(
                    "🗑",
                    key=f"del_{session_id}",
                    help=f"删除: {display_name}",
                ):
                    if delete_session(session_id):
                        st.rerun()
                    else:
                        st.error("删除失败，文件可能不存在。")


# ── 聊天输入与 AI 交互 ─────────────────────────────────────
prompt = st.chat_input("输入你想说的话...", key="chat_input")

if prompt:
    # 输入校验
    if not prompt.strip():
        st.warning("请输入有效内容。")
        st.stop()

    # 显示用户消息
    st.chat_message("user").write(prompt)
    st.session_state.message.append({"role": "user", "content": prompt})

    # 自动生成会话标题（取首条消息前 N 个字符）
    if not st.session_state.session_title:
        title = prompt[:SESSION_TITLE_MAX_LENGTH]
        if len(prompt) > SESSION_TITLE_MAX_LENGTH:
            title += "..."
        st.session_state.session_title = title

    # 创建客户端并发送消息
    with st.spinner("AI 正在思考..."):
        try:
            client = create_client()
            reply, error = send_message(
                client,
                st.session_state.message,
                st.session_state.nick_name,
                st.session_state.nature,
            )

            if error:
                st.error(error)
                # 移除刚才添加的用户消息，避免消息列表不一致
                st.session_state.message.pop()
            else:
                st.chat_message("assistant").write(reply)
                st.session_state.message.append({"role": "assistant", "content": reply})

        except ValueError as e:
            st.error(str(e))
            st.session_state.message.pop()
        except Exception as e:
            st.error(f"发生未知错误：{e}")
            st.session_state.message.pop()
