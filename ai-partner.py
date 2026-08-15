import streamlit as st
from openai import OpenAI
from datetime import datetime
import json
import os

st.set_page_config(page_title="AI Partner", page_icon=":robot_face:", layout="wide")
st.title("AI Partner") 

system_prompt = """
You are a helpful assistant named %s. 
Your personality is: %s. 
Please answer the user's questions in a concise and informative manner.
"""

def save_session(session_id, messages, nick_name, nature, session_title=""):
    session_data = {
        "session_id": session_id,
        "session_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_name": nick_name,
        "session_nature": nature,
        "session_messages": messages,
        "session_status": "completed",
        "session_title": session_title
    }
    if not os.path.exists("session_data"):
        os.makedirs("session_data")
    with open(f"session_data/{session_id}.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

#加载指定会话
def list_sessions():
    """列出所有已保存的会话，按时间倒序"""
    sessions = []
    if os.path.exists("session_data"):
        for filename in os.listdir("session_data"):
            if filename.endswith(".json"):
                filepath = os.path.join("session_data", filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        sessions.append(data)
                except (json.JSONDecodeError, KeyError):
                    continue
    sessions.sort(key=lambda x: x.get("session_date", ""), reverse=True)
    return sessions

def load_session(session_id):
    """加载指定会话"""
    filepath = os.path.join("session_data", f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def delete_session(session_id):
    """删除指定会话文件"""
    filepath = os.path.join("session_data", f"{session_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


#初始化 
if "message" not in st.session_state:
    st.session_state.message = []

#初始化昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "AI Partner"
#初始化性格
if "nature" not in st.session_state:
    st.session_state.nature = "You are a helpful assistant."
#会话标识
if "session_id" not in st.session_state: 
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
#会话标题（从第一条用户消息自动生成）
if "session_title" not in st.session_state:
    st.session_state.session_title = ""

for msg in st.session_state.message:
    st.chat_message(msg["role"]).write(msg["content"])

# 改进1：API Key 从环境变量读取，保留默认值作为后备
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com")

#左侧侧边栏
with st.sidebar:
    st.subheader("Settings")
    st.write("Configure your AI Partner settings below.")
    # 改进2：给输入组件添加 key 参数，避免状态冲突
    nick_name = st.text_input("Nickname", value=st.session_state.nick_name, placeholder="给你的AI伴侣起个名字", key="sidebar_nick")
    nature = st.text_area("Nature", value=st.session_state.nature, height=100, placeholder="描述AI伴侣的性格特点", key="sidebar_nature")
    if nick_name:
        st.session_state.nick_name = nick_name
    if nature:
        st.session_state.nature = nature

    st.divider()
    if st.button("新建会话", use_container_width=True):
        if st.session_state.message:
            save_session(st.session_state.session_id, st.session_state.message, st.session_state.nick_name, st.session_state.nature, st.session_state.session_title)
        st.session_state.message = []
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.session_title = ""
        st.rerun()



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

            # 优先显示自动生成的标题，没有则显示AI伴侣名字
            display_name = session_title if session_title else session_name

            # 改进3：用两列布局，左边加载按钮，右边删除按钮
            col_load, col_del = st.columns([4, 1])
            with col_load:
                button_label = f"{display_name} ({msg_count}条)"
                if st.button(button_label, key=f"session_{session_id}", use_container_width=True, help=f"{session_date}"):
                    loaded = load_session(session_id)
                    if loaded:
                        st.session_state.session_id = loaded["session_id"]
                        st.session_state.message = loaded["session_messages"]
                        st.session_state.nick_name = loaded.get("session_name", "AI Partner")
                        st.session_state.nature = loaded.get("session_nature", "You are a helpful assistant.")
                        st.session_state.session_title = loaded.get("session_title", "")
                        st.rerun()
            with col_del:
                if st.button("🗑", key=f"del_{session_id}", help=f"删除: {display_name}"):
                    delete_session(session_id)
                    st.rerun()

# 改进6：中文输入提示
prompt = st.chat_input("输入你想说的话...", key="chat_input")
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.message.append({"role": "user", "content": prompt})

    # 改进4：用第一条用户消息自动生成会话标题
    if not st.session_state.session_title:
        st.session_state.session_title = prompt[:15] + ("..." if len(prompt) > 15 else "")

    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[{"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)}] + st.session_state.message,
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    st.chat_message("assistant").write(response.choices[0].message.content)
    st.session_state.message.append({"role": "assistant", "content": response.choices[0].message.content})
