import streamlit as st
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, SYSTEM_PROMPT

# --- Page Config ---
st.set_page_config(
    page_title="Claude",
    page_icon="assets/logo.png" if __import__('os').path.exists("assets/logo.png") else "✦",
    layout="wide"
)
# --- Custom CSS ---
st.markdown("""
<style>
    /* Hide streamlit default header and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main background */
    .stApp {
        background-color: #1a1a1a;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2d2d2d;
    }

    /* New chat button */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #2d2d2d;
        color: #ececec;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 14px;
        transition: background-color 0.2s;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #3d3d3d;
        border-color: #cc785c;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: transparent;
        border: none;
        padding: 12px 0;
    }

    /* User message bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #2d2d2d;
        border-radius: 12px;
        padding: 12px 16px;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 12px;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #cc785c;
    }

    /* Main title */
    h2 {
        color: #cc785c !important;
        font-weight: 600;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    ::-webkit-scrollbar-thumb {
        background: #3d3d3d;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #cc785c;
    }
</style>
""", unsafe_allow_html=True)

# --- Init Anthropic Client ---
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversations" not in st.session_state:
    st.session_state.conversations = []

# --- Sidebar ---
with st.sidebar:
    st.markdown("## ✦ Claude")
    st.markdown("---")

    if st.button("➕  New Chat", use_container_width=True):
        if st.session_state.messages:
            st.session_state.conversations.append(st.session_state.messages.copy())
        st.session_state.messages = []
        st.rerun()

    # Show past conversations
    if st.session_state.conversations:
        st.markdown("#### Recent")
        for i, convo in enumerate(reversed(st.session_state.conversations)):
            # Show first user message as title
            first_msg = next((m["content"] for m in convo if m["role"] == "user"), f"Chat {i+1}")
            label = first_msg[:35] + "..." if len(first_msg) > 35 else first_msg
            if st.button(f"💬 {label}", key=f"convo_{i}", use_container_width=True):
                st.session_state.messages = convo.copy()
                st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='font-size:12px; color:gray;'>Built with Streamlit + Claude API</div>",
        unsafe_allow_html=True
    )

# --- Main Chat Area ---
st.markdown("## ✦ Claude")

# Render existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Message Claude..."):

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get Claude response with streaming
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

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": full_response})