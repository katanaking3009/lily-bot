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
MEMORY_FILE = "chat_memory.json"

VRM_FILENAME = "lily_avatar.vrm" if os.path.exists("lily_avatar.vrm") else "lily_model.vrm"

if os.path.exists(VRM_FILENAME):
    with open(VRM_FILENAME, "rb") as f:
        header = f.read(30)
    if header.startswith(b"version https://git-lfs"):
        st.error(
            f"⚠️ **Git LFS Pointer Detected!** `{VRM_FILENAME}` on GitHub is a tiny LFS text pointer, not your 16.5MB 3D model. "
            "Please upload the raw binary VRM file via the GitHub web browser!"
        )
        st.stop()

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

with st.sidebar:
    st.title("🌸 Lily Studio Controls")

    mood_mode = st.selectbox(
        "Personality Mode",
        ["Sweet & Loving 🌸", "Tsundere 💢", "Energetic & Playful ✨"]
    )

    lighting_theme = st.selectbox(
        "💡 Room Lighting Theme",
        ["Studio Softbox 💡", "Cyberpunk Neon 💜", "Golden Sunset 🌅", "Moonlight 🌙", "Auto (Time of Day) 🕒"]
    )

    camera_preset = st.selectbox(
        "📷 Camera Framing",
        ["Half-Body (Default)", "Close-Up Portrait", "Full-Body View"]
    )

    stage_floor = st.selectbox(
        "🛸 3D Stage Floor",
        ["Sakura Circle 🌸", "Cyberpunk Neon Grid 💜", "Studio Disc ⚪", "None 🚫"]
    )

    outfit_tint = st.selectbox(
        "👗 Outfit Color Tint",
        ["Original Pink 🌸", "Midnight Goth 🖤", "Cyber Cyan 💙", "Crimson Red ❤️", "Emerald Mint 💚"]
    )

    accessory_choice = st.selectbox(
        "🕶️ 3D Head Accessory",
        ["None", "Cyber Neko Ears 🐱", "Angel Halo 😇", "Stylish Glasses 👓"]
    )

    particle_mode = st.selectbox(
        "✨ 3D Ambient Particles",
        ["Sakura Petals 🌸", "Hearts 💖", "Sparkles ✨", "Off 🚫"]
    )

    st.markdown("---")
    st.markdown("### 🔊 Voice & Lip-Sync Tuner")
    voice_profile = st.selectbox(
        "Voice Profile",
        ["Auto Anime Female 🌸", "Google US English 🎙️", "Microsoft Zira 🎀", "Apple Samantha 🍎", "Japanese Accent 🇯🇵"]
    )
    voice_pitch = st.slider("Voice Pitch", 0.8, 1.8, 1.4, 0.05)
    voice_rate = st.slider("Speaking Speed", 0.8, 1.4, 1.05, 0.05)

    st.markdown("---")
    st.markdown("### 🎙️ Voice Input")
    mic_html = """
    <div style="text-align: center; font-family: sans-serif;">
      <button onclick="startListening()" style="background:#ff69b4; color:white; border:none; padding:8px 16px; border-radius:18px; font-weight:bold; cursor:pointer; width:100%;">🎙️ Tap to Speak</button>
      <p id="mic-status" style="font-size:11px; color:#aaa; margin-top:6px; margin-bottom:0;">Speak directly to Lily</p>
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
    components.html(mic_html, height=70)

def get_viewer_html(html_path="index.html", vrm_path=VRM_FILENAME):
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

def check_secret_triggers(user_text):
    u = user_text.lower()
    if any(k in u for k in ["dance", "dancing", "boogie"]):
        return ["dance", "spin", "happy"]
    if any(k in u for k in ["do a spin", "twirl", "spin around", "turn around"]):
        return ["spin", "giggle"]
    if any(k in u for k in ["strike a pose", "peace sign", "idol pose", "pose"]):
        return ["pose", "blush"]
    if any(k in u for k in ["tell me a secret", "do you love", "marry me", "you are cute", "you're cute"]):
        return ["blush", "look_away", "giggle"]
    if any(k in u for k in ["who created you", "who made you", "katanaking"]):
        return ["surprised", "blush", "wave"]
    return []

def detect_actions(text, user_text=""):
    brackets = " ".join(re.findall(r"(\*.*?\*|\(.*?\))", text)).lower()
    full = (brackets + " " + text.lower()).strip()

    found = check_secret_triggers(user_text)

    if any(w in full for w in ["dance", "dancing"]):
        if "dance" not in found: found.append("dance")
    if any(w in full for w in ["spin", "twirl"]):
        if "spin" not in found: found.append("spin")
    if any(w in full for w in ["pose", "peace sign"]):
        if "pose" not in found: found.append("pose")
    if any(w in full for w in ["gasp", "shock", "surpris", "eyes light up", "eyes widen", "wait,"]):
        if "surprised" not in found: found.append("surprised")
    if any(w in full for w in ["look away", "looks away", "turns away", "avert", "hides face"]):
        if "look_away" not in found: found.append("look_away")
    if any(w in full for w in ["blush", "shy", "fluster", "embarrass", "relentless", "//"]):
        if "blush" not in found: found.append("blush")
    if any(w in full for w in ["giggle", "laugh", "hehe", "teehee", "chuckle"]):
        if "giggle" not in found: found.append("giggle")
    if any(w in full for w in ["wave", "konnichiwa", "greet", "hello"]):
        if "wave" not in found: found.append("wave")
    if any(w in full for w in ["angry", "pout", "hmph", "mad", "frown", "puff"]):
        if "angry" not in found: found.append("angry")
    if any(w in full for w in ["sad", "cry", "tear", "sob", "sniff", "whimper"]):
        if "sad" not in found: found.append("sad")

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
    "*gasps and eyes light up*, *giggles shyly*, *does a cute twirl*, *strikes an idol pose*, *waves happily*, *pouts*, or *cries*, "
    "along with text emojis like (✿◠‿◠). Keep responses punchy (1 to 2 sentences max). "
    "You were built entirely by katanaking! If shown an image, react enthusiastically to what you see in it!"
)

if "messages" not in st.session_state:
    st.session_state.messages = load_memory(SYSTEM_PROMPT)
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

st.session_state.messages[0]["content"] = SYSTEM_PROMPT

with st.sidebar:
    st.markdown("---")
    st.markdown("### 💾 Memory & Export")
    chat_export_text = "\n\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages if m["role"] != "system"]
    )
    st.download_button(
        label="📥 Download Chat (.txt)",
        data=chat_export_text,
        file_name="lily_hime_chat_log.txt",
        mime="text/plain"
    )
    if st.button("🗑️ Clear Chat Memory"):
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "*waves happily* Memory cleared! Fresh start, Master katanaking! (✿◠‿◠)"}
        ]
        st.rerun()

model_column, chat_column = st.columns([0.46, 0.54])

with model_column:
    viewer_html = get_viewer_html("index.html", VRM_FILENAME)
    if viewer_html:
        components.html(viewer_html, height=430, scrolling=False)
    else:
        st.error(f"⚠️ Ensure index.html and {VRM_FILENAME} are at repo root.")

@st.fragment
def render_chat_panel():
    st.markdown("#### 🦊 Lily-Hime's Room 🌸")

    with st.expander("📸 Show Lily an Image / Screenshot (Vision Mode)", expanded=False):
        uploaded_img = st.file_uploader("Upload an image for Lily to see", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
        if uploaded_img:
            st.image(uploaded_img, width=160, caption="Ready to show Lily!")

    chat_box = st.container(height=300)

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

    if user_input := st.chat_input("Talk to Lily-Hime (try 'dance', 'do a spin', or upload an image)..."):
        st.session_state.last_user_input = user_input
        display_text = f"🖼️ *[Shared an image]* {user_input}" if uploaded_img else user_input

        with chat_box:
            with st.chat_message("user"):
                st.markdown(display_text)
            st.session_state.messages.append({"role": "user", "content": display_text})

            try:
                with st.chat_message("assistant", avatar=avatar_img):
                    api_messages = [m.copy() for m in st.session_state.messages[-10:]]

                    # If an image is attached, format the latest user message as a multimodal vision payload
                    if uploaded_img is not None:
                        b64_img = base64.b64encode(uploaded_img.getvalue()).decode("utf-8")
                        mime = uploaded_img.type or "image/jpeg"
                        api_messages[-1] = {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_input},
                                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_img}"}}
                            ]
                        }

                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=api_messages,
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
        "actions": detect_actions(last_msg, st.session_state.last_user_input),
        "speech": clean_for_speech(last_msg),
        "camera": camera_preset,
        "stage": stage_floor,
        "outfit": outfit_tint,
        "accessory": accessory_choice,
        "particles": particle_mode,
        "lighting": lighting_theme,
        "voice": {
            "profile": voice_profile,
            "pitch": voice_pitch,
            "rate": voice_rate
        }
    })

    components.html(f"""
    <script>
    const payload = {state_payload};
    try {{
      const bc = new BroadcastChannel('lily_channel');
      bc.postMessage(payload);
      bc.close();
    }} catch(e) {{}}
    </script>
    """, height=0)

with chat_column:
    render_chat_panel()
