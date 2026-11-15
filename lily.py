import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import base64
import os
import re
import json

st.set_page_config(
    page_title="Lily-Hime AI 🌸",
    page_icon="🌸",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
}
.anime-bubble {
    background: rgba(255, 182, 193, 0.18);
    border-left: 4px solid #ff69b4;
    padding: 12px 14px;
    border-radius: 12px;
    width: 100%;
    box-sizing: border-box;
    word-wrap: break-word;
    overflow-wrap: break-word;
    line-height: 1.5;
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

@st.cache_resource
def load_viewer_html(html_path="index.html", vrm_path="lily_model.vrm"):
    if not os.path.exists(html_path) or not os.path.exists(vrm_path):
        return ""
    with open(vrm_path, "rb") as f:
        b64_vrm = base64.b64encode(f.read()).decode("utf-8")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content.replace("__VRM_BASE64__", b64_vrm)

def clean_for_speech(text):
    text = re.sub(r"\*.*?\*", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^\w\s,.!?'-]", "", text)
    return " ".join(text.split())

def detect_emotion(text):
    actions = " ".join(re.findall(r"(\*.*?\*|\(.*?\))", text)).lower()
    target = actions if actions else text.lower()

    if any(w in target for w in ["wave", "konnichiwa", "greet", "hello", "hi "]):
        return "wave"
    if any(w in target for w in ["blush", "shy", "fluster", "embarrass", "peek", "cute"]):
        return "blush"
    if any(w in target for w in ["gasp", "shock", "surpris", "eyes widen", "woah"]):
        return "surprised"
    if any(w in target for w in ["angry", "pout", "hmph", "mad", "frown", "puff"]):
        return "angry"
    if any(w in target for w in ["sad", "cry", "tear", "sob", "sniff", "whimper"]):
        return "sad"
    return "happy"

SYSTEM_PROMPT = (
    "Your name is Lily-Hime. You are a cheerful, sweet, expressive anime girl character. "
    "Always start your reply with a cute roleplay action in asterisks like *blushes*, *gasps*, "
    "*waves*, *giggles*, *pouts*, or *cries* to show your emotions, along with text emojis like (✿◠‿◠). "
    "Keep your responses concise (2 to 3 sentences), warm, and natural. "
    "You were built entirely by katanaking! Proudly boast that katanaking created you!"
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "*waves happily* Konnichiwa! 🌸 I am Lily-Hime, your companion. What shall we talk about today, Master katanaking? (✿◠‿◠)"
        }
    ]

model_column, chat_column = st.columns([0.45, 0.55])

with chat_column:
    st.subheader("🦊 Lily-Hime's Room 🌸")
    chat_box = st.container(height=420)

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
                        max_tokens=220,
                        temperature=0.7
                    )
                    lily_response = response.choices[0].message.content
                    bubble = f'<div class="anime-bubble">{lily_response}</div>'
                    st.markdown(bubble, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": lily_response})
            except Exception as e:
                st.error(f"⚠️ API call failed: {e}")

with model_column:
    viewer_html = load_viewer_html("index.html", "lily_model.vrm")
    last_msg = st.session_state.messages[-1]["content"] if st.session_state.messages else ""
    emotion = detect_emotion(last_msg)
    speech = clean_for_speech(last_msg)

    if viewer_html:
        components.html(viewer_html, height=480, scrolling=False)
        payload = json.dumps({"type": "LILY_STATE", "emotion": emotion, "speech": speech})
        components.html(f"""
        <script>
        const p = {payload};
        window.parent.__LILY_LAST_STATE__ = p;
        window.parent.document.querySelectorAll('iframe').forEach(f => {{
            try {{ f.contentWindow.postMessage(p, '*'); }} catch(e) {{}}
        }});
        </script>
        """, height=0)
    else:
        st.error("⚠️ Ensure index.html and lily_model.vrm are at repo root.")
