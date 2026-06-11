import streamlit as st
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, SYSTEM_PROMPT
from database import init_db, save_conversation, load_all_conversations, load_conversation, delete_conversation

# --- Init DB ---
init_db()

# --- Page Config ---
st.set_page_config(
    page_title="Claude",
    page_icon="✳",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}

    .stApp {
        background-color: #1a1a1a;
        color: #ececec;
    }

    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2d2d2d;
    }

    [data-testid="stSidebar"] .stButton > button {
        background-color: #2d2d2d;
        color: #ececec;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        width: 100%;
        font-size: 13px;
        transition: background-color 0.2s;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #3d3d3d;
        border-color: #cc785c;
    }

    [data-testid="stChatMessage"] {
        background-color: transparent;
        border: none;
        padding: 12px 0;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #2d2d2d;
        border-radius: 12px;
        padding: 12px 16px;
    }

    [data-testid="stChatInput"] {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 12px;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #cc785c;
    }

    h2 { color: #cc785c !important; font-weight: 600; }

    .conv-time {
        font-size: 10px;
        color: #666;
        margin-top: -8px;
        margin-bottom: 4px;
        padding-left: 4px;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1a1a1a; }
    ::-webkit-scrollbar-thumb { background: #3d3d3d; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #cc785c; }
</style>
""", unsafe_allow_html=True)

# --- Init Client ---
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# --- Sidebar ---
with st.sidebar:
    st.markdown("## ✳ Claude")
    st.markdown("---")

    if st.button("➕  New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.rerun()

    st.markdown("#### Recent")

    conversations = load_all_conversations()
    for conv_id, title, updated_at in conversations:
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(f"💬 {title}", key=f"load_{conv_id}", use_container_width=True):
                st.session_state.messages = load_conversation(conv_id)
                st.session_state.conversation_id = conv_id
                st.rerun()
        with col2:
            if st.button("🗑", key=f"del_{conv_id}"):
                delete_conversation(conv_id)
                if st.session_state.conversation_id == conv_id:
                    st.session_state.messages = []
                    st.session_state.conversation_id = None
                st.rerun()

    st.markdown("---")
    st.markdown("<div style='font-size:12px; color:gray;'>Built with Streamlit + Claude API</div>", unsafe_allow_html=True)

# --- Main Chat Area ---
st.markdown("## ✳ Claude")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Message Claude..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=st.session_state.messages
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Save to SQLite
    st.session_state.conversation_id = save_conversation(
        st.session_state.conversation_id,
        st.session_state.messages
    )
    st.rerun()

# --- Disclaimer ---
st.markdown("<div style='text-align:center; font-size:12px; color:#666; margin-top:20px;'>Claude can make mistakes. Please double-check responses.</div>", unsafe_allow_html=True)