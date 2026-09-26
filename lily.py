import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================
st.set_page_config(page_title="Lily-Hime AI 🌸", page_icon="🌸", layout="wide")

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Missing GROQ_API_KEY in Secrets!")
    st.stop()

# FIXED: Swapped to Groq's official active developer tier flagship model ID
MODEL_NAME = "qwen/qwen3.8-27b"
client = Groq(api_key=api_key)

st.markdown("""
    <style>
    .stApp { background-color: #FFFDF9; }
    h1 { color: #FF4500 !important; font-family: 'Trebuchet MS', sans-serif; font-weight: bold; text-align: center; margin-bottom: 30px; }
    .anime-bubble { background-color: #FFFFFF; border: 2px solid #FF4500; border-radius: 18px; padding: 15px; margin: 5px 0px; color: #2F2F2F; font-size: 16px; box-shadow: 4px 4px 0px #FFE4D6; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DIVISION COLUMNS & CHAT WINDOW
# ==========================================
chat_column, image_column = st.columns([0.6, 0.4])

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
        if message["role"] == "system": continue
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(f'<div class="anime-bubble">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(message["content"])

    if user_input := st.chat_input("Talk to Lily-Hime..."):
        with st.chat_message("user"): st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        try:
            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model=MODEL_NAME, 
                    messages=st.session_state.messages,
                    max_tokens=150 # Keeps answers within free tier limits
                )
                # FIXED: Access choices correctly via explicit index tracking array bracket
                lily_response = response.choices[0].message.content
                st.markdown(f'<div class="anime-bubble">{lily_response}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": lily_response})
        except Exception as e:
            st.error(f"Link broke: {e}")
import os

# ==========================================
# 3. STATIC HTML FILE INJECTION
# ==========================================
with image_column:
    st.write("### ✨ Lily-Hime 3D Room Viewer")
    
    html_path = "index.html"
    
    if os.path.exists(html_path):
        # Open and read the raw code from your GitHub/Explorer index.html file
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # Inject the HTML code straight into Streamlit
        components.html(html_content, height=570, scrolling=False)
    else:
        st.error("Could not find index.html in the repository directory!")


    
