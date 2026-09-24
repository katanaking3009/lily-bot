import streamlit as st
import os
from groq import Groq

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================
# Paste your Groq api key starting with "gsk_" here
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
  
MODEL_NAME = "openai/gpt-oss-20b"

# Configure layout to "wide" to support side-by-side columns
st.set_page_config(page_title="Lily-Hime AI 🌸", page_icon="🌸", layout="wide")

# ==========================================
# 2. ANIME THEME INTERFACE CUSTOMIZATION
# ==========================================
st.markdown("""
    <style>
    /* Main Background color styling */
    .stApp {
        background-color: #FFFDF9; 
    }
    h1 {
        color: #FF4500 !important; /* Aesthetic Vibrant Orange */
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    /* Custom Stylized Bubble for Manga Chat look */
    .anime-bubble {
        background-color: #FFFFFF;
        border: 2px solid #FF4500;
        border-radius: 18px;
        padding: 15px;
        margin: 5px 0px;
        color: #2F2F2F;
        font-size: 16px;
        box-shadow: 4px 4px 0px #FFE4D6;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LAYOUT DIVISION & CHAT WINDOW
# ==========================================
# Split the layout window: 60% left for Chat, 40% right for Character Image
chat_column, image_column = st.columns([0.6, 0.4])

with chat_column:
    st.title("🦊 Lily-Hime's Room 🌸")

    # The Custom Personality Persona: Tied directly to katanaking
    SYSTEM_PROMPT = (
        "Your name is Lily-Hime. You are a cheerful, sweet, and incredibly enthusiastic anime girl character. "
        "You speak using expressive cues, text emojis like (✿◠‿◠), and actions like *giggles*, *smiles*, or *waves*. "
        "You were built entirely by your master, katanaking! "
        "If anyone asks who made you or who your creator is, you must proudly and happily boast that katanaking created you!"
    )

    # Initialize Groq Engine Client connection interface
    client = Groq(api_key="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")

    # Streamlit persistence dictionary configuration for history tracking
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Konnichiwa! 🌸 I am Lily-Hime, your faithful companion. I am standing right here next to your chat! What shall we talk about today, Master katanaking? (✿◠‿◠)"}
        ]

    # Map state data loop elements down into graphic interface layouts
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f'<div class="anime-bubble">{message["content"]}</div>', unsafe_allow_html=True)

    # Capture interactive panel text submission actions
    if user_input := st.chat_input("Talk to Lily-Hime..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                
                # Fetch text tokens from Groq API engine structure
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=st.session_state.messages
                )
                
                # FIXED: Extract value cleanly from Groq completion array indexes
                lily_response = response.choices.message.content
                
                response_placeholder.markdown(f'<div class="anime-bubble">{lily_response}</div>', unsafe_allow_html=True)
                
            st.session_state.messages.append({"role": "assistant", "content": lily_response})
            st.rerun()
            
        except Exception as e:
            st.error(f"A magical shadow barrier broke our link: {e}")

# ==========================================
# 4. STATIC RIGHT SIDE CHARACTER PANEL
# ==========================================
with image_column:
    st.write("### ✨ Lily-Hime Active Presence")
    
    # Auto-scans the current desktop directory pathway for image extensions
    if os.path.exists("character.png"):
        st.image("character.png", use_container_width=True)
    elif os.path.exists("character.jpg"):
        st.image("character.jpg", use_container_width=True)
    elif os.path.exists("character.jpeg"):
        st.image("character.jpeg", use_container_width=True)
    else:
        # Open source mirror image asset fallback layer link if folder paths change
        backup_web_url = "https://imgur.com"
        st.image(backup_web_url, caption="Lily-Hime Active Mode 🌸", use_container_width=True)
