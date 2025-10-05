import os
import streamlit as st
from chat_client import ChatClient


st.set_page_config(page_title="Mitran AI Assistant", page_icon="💬", layout="wide")

# Light theme text styling (ensure dark environments still show dark text)
st.markdown(
    """
    <style>
      /* Prefer dark text on light backgrounds for readability */
      html, body, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"], .stChatMessage, .stTextInput input {
        color: #111111 !important;
      }
      /* Slightly lighter secondary background look */
      [data-testid="stSidebar"] {
        color: #111111 !important;
      }
      /* Make main content wider */
      .block-container { max-width: 1400px; padding-top: 2rem; padding-bottom: 2.5rem; }
      /* Ensure chat input spans full width */
      [data-testid="stChatInput"] { max-width: 1400px; margin-left: auto; margin-right: auto; }
      /* Let chat message body use available width */
      .stChatMessage { max-width: 100%; }

      /* Typography scale down */
      html, body { font-size: 15px; }
      h1 { font-size: 1.6rem; }
      h2 { font-size: 1.25rem; }
      h3 { font-size: 1.1rem; }
      [data-testid="stMarkdownContainer"] p,
      [data-testid="stMarkdownContainer"] li { font-size: 0.95rem; line-height: 1.45; }
      .stChatMessage p { font-size: 0.95rem; line-height: 1.5; }
      .stTextInput input { font-size: 0.95rem !important; }
      [data-testid="stChatInput"] textarea { font-size: 0.95rem !important; }
      .stButton button { font-size: 0.9rem; }
      .stCaption, [data-testid="stCaptionContainer"] { font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "client" not in st.session_state:
    st.session_state.client = ChatClient()

st.title("Mitran AI Assistant")

st.caption("Chat with Mitran to make our city kinder for community dogs.")

session_id = st.text_input("Session ID", value=os.environ.get("USER", "local") or "local")
if not session_id:
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

prompt = st.chat_input("Type your message…")
if prompt:
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        chunks = []
        for piece in st.session_state.client.stream(session_id, prompt):
            chunks.append(piece)
            placeholder.markdown("".join(chunks))
        full_text = "".join(chunks)
        placeholder.markdown(full_text)
        st.session_state.history.append(("assistant", full_text))

col1, col2 = st.columns(2)
with col1:
    if st.button("Clear session history"):
        st.session_state.history = []
with col2:
    st.caption("Session memory is ON; Google Search tool enabled.")


