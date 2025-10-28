import streamlit as st
import requests

# --- Page Config ---
st.set_page_config(page_title="Nathan AI Chatbot", page_icon="🤖", layout="centered")

# --- Custom CSS ---
st.markdown("""
    <style>
        .chat-bubble {
            padding: 12px 18px;
            border-radius: 16px;
            margin: 8px 0;
            max-width: 80%;
            word-wrap: break-word;
            line-height: 1.5;
            font-size: 16px;
        }
        .user-bubble {
            background-color: #DCF8C6;
            color: #000;
            align-self: flex-end;
            border: 1px solid #b2e59e;
        }
        .assistant-bubble {
            background-color: #E9EBF0;
            color: #000;
            align-self: flex-start;
            border: 1px solid #d2d6dc;
        }
        .header {
            text-align: center;
            font-weight: 600;
            font-size: 26px;
            color: #1E88E5;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header">🤖 Nathan AI Chatbot</div>', unsafe_allow_html=True)

# --- Session State ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# --- Chat Display ---
for msg in st.session_state.conversation:
    role_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
    st.markdown(f"<div class='chat-bubble {role_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# --- User Input ---
user_input = st.chat_input("Type your message...")

# --- API Request ---
if user_input:
    st.session_state.conversation.append({"role": "user", "content": user_input})

    try:
        response = requests.post(
            "http://localhost:8000/walker/ChatAPI",
            json={"prompt": user_input}  # ✅ only send prompt, backend handles session
        )

        if response.status_code == 200:
            data = response.json()["reports"][0]
            assistant_reply = data["reply"]
            st.session_state.conversation = data["conversation"]
        else:
            assistant_reply = f"⚠️ Error: {response.text}"

    except Exception as e:
        assistant_reply = f"⚠️ Connection error: {e}"

    st.session_state.conversation.append({"role": "assistant", "content": assistant_reply})
    st.rerun()

# --- Clear Chat ---
if st.button("🧹 Clear Chat"):
    st.session_state.conversation = []
    st.rerun()
