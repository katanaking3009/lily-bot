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
    padding-top: 0.6rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 0.6rem !important;
    padding-right: 0.6rem !important;
}
.anime-bubble {
    background: rgba(255, 182, 193, 0.18);
    border-left: 4px solid #ff69b4;
    padding: 10px 12px;
    border-radius: 12px;
    width: 100%;
    box-sizing: border-box;
    word-wrap: break-word;
    overflow-wrap: break-word;
    line-height: 1.45;
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
def load_base_viewer(html_path="index.html", vrm_path="lily_model.vrm"):
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

def detect_actions(text):
    # Extract all *actions* and (actions), plus scan the full text
    brackets = " ".join(re.findall(r"(\*.*?\*|\(.*?\))", text)).lower()
    full = (brackets + " " + text.lower()).strip()

    found = []
    if any(w in full for w in ["gasp", "shock", "surpris", "eyes light up", "eyes widen", "wait,"]):
        found.append("surprised")
    if any(w in full for w in ["look away", "looks away", "turns away", "avert", "hides face"]):
        found.append("look_away")
    if any(w in full for w in ["blush", "shy", "fluster", "embarrass", "relentless", "//"]):
        found.append("blush")
    if any(w in full for w in ["giggle", "laugh", "hehe", "teehee", "chuckle"]):
        found.append("giggle")
    if any(w in full for w in ["wave", "konnichiwa", "greet", "hello"]):
        found.append("wave")
    if any(w in full for w in ["angry", "pout", "hmph", "mad", "frown", "puff"]):
        found.append("angry")
    if any(w in full for w in ["sad", "cry", "tear", "sob", "sniff", "whimper"]):
        found.append("sad")

    if not found:
        found.append("happy")
    return found

SYSTEM_PROMPT = (
    "Your name is Lily-Hime. You are a cheerful, sweet, expressive anime girl character. "
    "Always include cute roleplay actions in asterisks like *blushes deeply*, *shyly looks away*, "
    "*gasps and eyes light up*, *giggles shyly*, *waves happily*, *pouts*, or *cries*, "
    "along with text emojis like (✿◠‿◠). Keep responses concise (2 to 3 sentences). "
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
    st.markdown("#### 🦊 Lily-Hime's Room 🌸")
    chat_box = st.container(height=290)

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
    base_html = load_base_viewer("index.html", "lily_model.vrm")
    last_msg = st.session_state.messages[-1]["content"] if st.session_state.messages else ""
    actions = detect_actions(last_msg)
    speech = clean_for_speech(last_msg)

    if base_html:
        final_html = base_html.replace("__ACTIONS_JSON__", json.dumps(actions))
        final_html = final_html.replace("__SPEECH_JSON__", json.dumps(speech))
        components.html(final_html, height=310, scrolling=False)
    else:
        st.error("⚠️ Ensure index.html and lily_model.vrm are at repo root.")
