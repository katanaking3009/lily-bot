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

client = Groq(api_key=api_key)
avatar_img = "character.png" if os.path.exists("character.png") else "🌸"
MEMORY_FILE = "chat_memory.json"

def load_memory(default_prompt):
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                data[0]["content"] = default_prompt
                return data
        except Exception:
            pass
    return [
        {"role": "system", "content": default_prompt},
        {
            "role": "assistant",
            "content": "*waves happily* Konnichiwa! 🌸 I am Lily-Hime, your companion. What shall we talk about today, Master katanaking? (✿◠‿◠)"
        }
    ]

def save_memory(messages):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(messages[-30:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

st.sidebar.title("🌸 Lily Studio Controls")

mood_mode = st.sidebar.selectbox(
    "Personality Mode",
    ["Sweet & Loving 🌸", "Tsundere 💢", "Energetic & Playful ✨"]
)

camera_preset = st.sidebar.selectbox(
    "📷 Camera Framing",
    ["Half-Body (Default)", "Close-Up Portrait", "Full-Body View"]
)

outfit_tint = st.sidebar.selectbox(
    "👗 Outfit Color Tint",
    ["Original Pink 🌸", "Midnight Goth 🖤", "Cyber Cyan 💙", "Crimson Red ❤️", "Emerald Mint 💚"]
)

accessory_choice = st.sidebar.selectbox(
    "🕶️ 3D Head Accessory",
    ["None", "Cyber Neko Ears 🐱", "Angel Halo 😇", "Stylish Glasses 👓"]
)

particle_mode = st.sidebar.selectbox(
    "✨ 3D Ambient Particles",
    ["Sakura Petals 🌸", "Hearts 💖", "Sparkles ✨", "Off 🚫"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Voice Input")
mic_html = """
<div style="text-align: center;">
  <button onclick="startListening()" style="background:#ff69b4; color:white; border:none; padding:8px 14px; border-radius:18px; font-weight:bold; cursor:pointer;">🎙️ Tap to Speak</button>
  <p id="mic-status" style="font-size:11px; color:#888; margin-top:5px;">Speak directly to Lily</p>
</div>
<script>
function startListening() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { alert("Speech recognition requires Chrome."); return; }
  const rec = new SR();
  rec.lang = 'en-US';
  const stEl = document.getElementById('mic-status');
  stEl.textContent = "Listening...";
  rec.onresult = (e) => {
    const txt = e.results[0][0].transcript;
    stEl.textContent = "Heard: " + txt;
    const inp = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
    if (inp) {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
      setter.call(inp, txt);
      inp.dispatchEvent(new Event('input', { bubbles: true }));
    }
  };
  rec.onerror = () => { stEl.textContent = "Mic error. Try again."; };
  rec.start();
}
</script>
"""
components.html(mic_html, height=75)

# Removed @st.cache_resource so it reads the freshly uploaded VRM file every single time without caching bugs
def get_static_viewer_html(html_path="index.html", vrm_path="lily_model.vrm"):
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

if "Sweet" in mood_mode:
    mood_prompt = "You are warm, devoted, and affectionate toward Master katanaking."
elif "Tsundere" in mood_mode:
    mood_prompt = "You are a sharp-tongued tsundere! Act flustered and stubborn while secretly caring about katanaking."
else:
    mood_prompt = "You are upbeat, witty, and playful!"

SYSTEM_PROMPT = (
    f"Your name is Lily-Hime. {mood_prompt} "
    "Always start your reply with a roleplay action in asterisks like *blushes deeply*, *shyly looks away*, "
    "*gasps and eyes light up*, *giggles shyly*, *waves happily*, *pouts*, or *cries*, "
    "along with text emojis like (✿◠‿◠). Keep responses punchy (1 to 2 sentences max). "
    "You were built entirely by katanaking!"
)

if "messages" not in st.session_state:
    st.session_state.messages = load_memory(SYSTEM_PROMPT)

st.session_state.messages[0]["content"] = SYSTEM_PROMPT

st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Memory & Export")
chat_export_text = "\n\n".join(
    [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages if m["role"] != "system"]
)
st.sidebar.download_button(
    label="📥 Download Chat (.txt)",
    data=chat_export_text,
    file_name="lily_hime_chat_log.txt",
    mime="text/plain"
)
if st.sidebar.button("🗑️ Clear Chat Memory"):
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "*waves happily* Memory cleared! Fresh start, Master katanaking! (✿◠‿◠)"}
    ]
    st.rerun()

model_column, chat_column = st.columns([0.45, 0.55])

with model_column:
    static_viewer = get_static_viewer_html("index.html", "lily_model.vrm")
    if static_viewer:
        components.html(static_viewer, height=320, scrolling=False)
    else:
        st.error("⚠️ Ensure index.html and lily_model.vrm are at repo root.")

@st.fragment
def render_chat_panel():
    st.markdown("#### 🦊 Lily-Hime's Room 🌸")
    chat_box = st.container(height=280)

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
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=st.session_state.messages[-10:],
                            max_tokens=90,
                            temperature=0.7
                        )
                    except Exception:
                        response = client.chat.completions.create(
                            model="qwen/qwen3.8-27b",
                            messages=st.session_state.messages[-10:],
                            max_tokens=90,
                            temperature=0.7
                        )
                    lily_response = response.choices[0].message.content
                    bubble = f'<div class="anime-bubble">{lily_response}</div>'
                    st.markdown(bubble, unsafe_allow_html=True)

                st.session_state.messages.append({"role": "assistant", "content": lily_response})
                save_memory(st.session_state.messages)
            except Exception as e:
                st.error(f"⚠️ API call failed: {e}")

    last_msg = st.session_state.messages[-1]["content"] if st.session_state.messages else ""
    state_payload = json.dumps({
        "type": "LILY_STATE",
        "actions": detect_actions(last_msg),
        "speech": clean_for_speech(last_msg),
        "camera": camera_preset,
        "outfit": outfit_tint,
        "accessory": accessory_choice,
        "particles": particle_mode
    })

    components.html(f"""
    <script>
    const payload = {state_payload};
    try {{
      localStorage.setItem('lily_latest_state', JSON.stringify(payload));
      const bc = new BroadcastChannel('lily_channel');
      bc.postMessage(payload);
      bc.close();
    }} catch(e) {{}}
    </script>
    """, height=0)

with chat_column:
    render_chat_panel()
