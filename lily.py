
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import base64
import os
import re

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================
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
def get_vrm_b64(vrm_path="lily_model.vrm"):
    with open(vrm_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def clean_for_speech(text):
    # Remove *actions* and (kaomojis) so TTS only reads spoken words
    text = re.sub(r"\*.*?\*", "", text)
    text
