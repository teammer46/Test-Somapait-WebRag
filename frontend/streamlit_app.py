import streamlit as st
import requests
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(
    page_title="Company Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Company Chatbot (Gemini + MongoDB)")

# ---------------------------------------------------------
# Utility: create new room
# ---------------------------------------------------------
def create_new_room():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M-%S")
    title = f"chat-{timestamp}"
    requests.post(f"{API}/history/create", json={"title": title})
    return title


# ---------------------------------------------------------
# INIT: Auto-create room if not exists
# ---------------------------------------------------------
if "current_room" not in st.session_state:
    rooms = requests.get(f"{API}/history/list").json()

    if len(rooms) == 0:
        st.session_state.current_room = create_new_room()
    else:
        st.session_state.current_room = rooms[0]["title"]

current_room = st.session_state.current_room


# ---------------------------------------------------------
# SIDEBAR: ROOM MANAGEMENT
# ---------------------------------------------------------
st.sidebar.header("📁 ห้องสนทนา")

# ----- Create Room -----
if st.sidebar.button("➕ สร้างห้องใหม่"):
    st.session_state.current_room = create_new_room()
    st.rerun()

# ----- List Rooms -----
rooms = requests.get(f"{API}/history/list").json()

for r in rooms:
    title = r["title"]

    col1, col2, col3 = st.sidebar.columns([3, 1, 1])  # เลือก | rename | delete

    # 1) ปุ่มเลือกห้อง
    if col1.button(f"🔵 {title}", key=f"room_{title}"):
        st.session_state.current_room = title
        st.rerun()

    # 2) ปุ่ม rename
    if col2.button("✏️", key=f"rename_{title}"):
        st.session_state.rename_target = title

    # 3) ปุ่มลบห้อง
    if col3.button("🗑️", key=f"del_{title}"):
        requests.delete(f"{API}/history/{title}")
        st.sidebar.warning(f"ลบห้อง `{title}` แล้ว!")

        # ถ้าลบห้องปัจจุบัน → สร้างใหม่แทน
        if title == current_room:
            st.session_state.current_room = create_new_room()

        st.rerun()

# ---------------------------------------------------------
# RENAME ROOM POPUP
# ---------------------------------------------------------
if "rename_target" in st.session_state:
    rename_title = st.session_state.rename_target

    with st.sidebar.form("rename_form"):
        st.write(f"✏️ เปลี่ยนชื่อห้อง: `{rename_title}`")
        new_name = st.text_input("ชื่อใหม่", value=rename_title)

        if st.form_submit_button("บันทึกชื่อใหม่"):
            requests.put(
                f"{API}/history/rename",
                json={"session_id": rename_title, "new_title": new_name}
            )
            st.sidebar.success(f"เปลี่ยนชื่อเรียบร้อยเป็น `{new_name}`")

            # อัปเดตห้องปัจจุบันถ้า rename ห้องที่กำลังอยู่
            if rename_title == st.session_state.current_room:
                st.session_state.current_room = new_name

            del st.session_state.rename_target
            st.rerun()

        if st.form_submit_button("ยกเลิก"):
            del st.session_state.rename_target
            st.rerun()


st.sidebar.success(f"ห้องปัจจุบัน: {st.session_state.current_room}")

# ---------------------------------------------------------
# CHAT AREA
# ---------------------------------------------------------
current_room = st.session_state.current_room
st.subheader(f"💬 ห้องสนทนา: {current_room}")

history_res = requests.get(f"{API}/history/{current_room}").json()
messages = history_res.get("messages", [])
if not isinstance(messages, list):
    messages = []

# Show messages
for msg in messages:
    with st.chat_message(msg["role"]):
        st.write(msg["message"])

prompt = st.chat_input("พิมพ์ข้อความ…")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    payload = {"title": current_room, "message": prompt}

    res = requests.post(f"{API}/chat", json=payload).json()
    answer = res.get("answer") or res.get("reply")

    with st.chat_message("assistant"):
        st.write(answer)

    st.rerun()
