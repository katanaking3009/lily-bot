import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import os

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================
st.set_page_config(page_title="Lily-Hime AI 🌸", page_icon="🌸", layout="wide")

# Make sure the key is loaded correctly
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

# ==========================================
# 2. DIVISION COLUMNS & CHAT WINDOW
# ==========================================
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
            {"role": "assistant", "content": "Konnichiwa! 🌸 I am Lily-Hime, your companion. What shall we talk about today, Master katanaking? (✿◠‿◠)"}
        ]

    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(f'<div class="anime-bubble">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(message["content"])

    if user_input := st.chat_input("Talk to Lily-Hime..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        try:
            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=st.session_state.messages,
                    max_tokens=150
                )
                lily_response = response.choices[0].message.content
                st.markdown(f'<div class="anime-bubble">{lily_response}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": lily_response})
        except Exception as e:
            st.error(f"⚠️ API call failed: {e}")

# ============================================
# 3. EMBED 3D MODEL VIEWER
# ============================================

with model_column:
    st.write("### ✨ Lily-Hime 3D Avatar Viewer")

    # ✅ Direct iframe to GitHub Pages
    components.iframe("https://katanaking3009.github.io/lily-bot/", height=600)

