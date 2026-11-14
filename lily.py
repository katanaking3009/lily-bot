
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import base64
import os

st.set_page_config(
    page_title="Lily-Hime AI 🌸",
    page_icon="🌸",
    layout="wide"
)

st.markdown("""
<style>
.anime-bubble {
    background: rgba(255, 182, 193, 0.18);
    border-left: 4px solid #ff69b4;
    padding: 10px 14px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

try:
    api_key = st.secrets["GROQ_API_KEY"]
    if not api_key or not api_key.startswith("gsk_"):
        st.error("⚠️ GROQ_API_KEY is missing or malformed.")
        st.stop()
except Exception:
    st.error("⚠️ GROQ_API_KEY not found in secrets.")
    st.stop()

MODEL_NAME = "qwen/qwen3.8-27b"
client = Groq(api_key=api_key)

avatar_img = "character.png" if os.path.exists("character.png") else "🌸"

@st.cache_data
def get_vrm_viewer_html(html_path="index.html", vrm_path="lily_model.vrm"):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    if os.path.exists(vrm_path):
        with open(vrm_path, "rb") as f:
            b64_vrm = base64.b64encode(f.read()).decode("utf-8")
        
        data_uri = f"data:application/octet-stream;base64,{b64_vrm}"
        html_content = html_content.replace("__VRM_BASE64__", b64_vrm)
        html_content = html_content.replace("./lily_model.vrm", data_uri)
        html_content = html_content.replace("lily_model.vrm", data_uri)

    return html_content

chat_column, model_column = st.columns([0.6, 0.4])

with chat_column:
    st.title("🦊 Lily-Hime's Room 🌸")
    SYSTEM_PROMPT = (
        "Your name is Lily-Hime. You are a cheerful, sweet, anime girl character. "
        "You speak using text emojis like (✿◠‿◠) and actions like *waves*. "
        "You were built entirely by katanaking! Proudly boast that katanaking created you!"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "assistant",
                "content": "Konnichiwa! 🌸 I am Lily-Hime, your companion. What shall we talk about today, Master katanaking? (✿◠‿◠)"
            }
        ]

    chat_box = st.container(height=480)
    with chat_box:
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue
            icon = avatar_img if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=icon):
                if message["role"] == "assistant":
                    bubble = f'<div class="anime-bubble">{message["content"]}</div>'
                    st.markdown(bubble, unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])

    if user_input := st.chat_input("Talk to Lily-Hime..."):
        with chat_box:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            try:
                with st.chat_message("assistant", avatar=avatar_img):
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=st.session_state.messages,
                        max_tokens=150
                    )
                    lily_response = response.choices[0].message.content
                    bubble = f'<div class="anime-bubble">{lily_response}</div>'
                    st.markdown(bubble, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": lily_response})
            except Exception as e:
                st.error(f"⚠️ API call failed: {e}")

with model_column:
    st.write("### ✨ Lily-Hime 3D Avatar Viewer")

    html_path = "index.html"
    vrm_path = "lily_model.vrm"

    if os.path.exists(html_path) and os.path.exists(vrm_path):
        viewer_html = get_vrm_viewer_html(html_path, vrm_path)
        components.html(viewer_html, height=550, scrolling=False)
    elif os.path.exists(html_path):
        st.warning("⚠️ lily_model.vrm not found, loading index.html only.")
        with open(html_path, "r", encoding="utf-8") as f:
            components.html(f.read(), height=550, scrolling=False)
    else:
        st.error("⚠️ index.html not found at repo root. Using fallback viewer.")
        components.iframe("https://katanaking3009.github.io/lily-bot/", height=550)
