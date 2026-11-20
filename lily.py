import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import base64
import os
import re
import json
import glob

st.set_page_config(
    page_title="Lily & Miki 3D AI Studio 🌸",
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

# ==========================================
# CHARACTER PROFILES (LILY vs RUDE MIKI)
# ==========================================
CHARACTER_PROFILES = {
    "lily_avatar.vrm": {
        "label": "Lily-Hime 🌸 (Sweet Companion)",
        "name": "Lily-Hime",
        "icon": "character.png" if os.path.exists("character.png") else "🌸",
        "bio": "You are Lily-Hime, a graceful, devoted anime companion created by Master katanaking.",
        "greeting": "*waves happily* Konnichiwa! 🌸 I am Lily-Hime, your companion. What shall we talk about today, Master katanaking? (✿◠‿◠)",
        "default_pitch": 1.40,
        "default_mood": 0  # Sweet & Loving
    },
    "lily_model.vrm": {
        "label": "Lily-Hime 🌸 (Classic)",
        "name": "Lily-Hime",
        "icon": "character.png" if os.path.exists("character.png") else "🌸",
        "bio": "You are Lily-Hime, a graceful, devoted anime companion created by Master katanaking.",
        "greeting": "*waves happily* Konnichiwa! 🌸 I am Lily-Hime! Ready for anything, Master katanaking! (✿◠‿◠)",
        "default_pitch": 1.40,
        "default_mood": 0
    },
    "miki.vrm": {
        "label": "Miki-Chan 🙄 (Rude & Sarcastic)",
        "name": "Miki-Chan",
        "icon": "💢",
        "bio": (
            "You are Miki-Chan, a rude, blunt, sarcastic, and easily annoyed anime girl. "
            "You constantly roast katanaking, act unimpressed, call him a nerd or dork, and sigh when he bothers you—even though you're stuck on his screen because he coded you."
        ),
        "greeting": "*pouts and looks away* Ugh, what do you want now, katanaking? I was literally relaxing before you summoned me. Make it quick! (¬_¬)",
        "default_pitch": 1.25,
        "default_mood": 3  # Rude & Sarcastic
    }
}

available_vrms = sorted(glob.glob("*.vrm"))
if not available_vrms:
    st.error("⚠️ No .vrm files found in the repository root!")
    st.stop()

with st.sidebar:
    st.title("🌸 3D Companion Studio")

    vrm_labels = [
        CHARACTER_PROFILES[f]["label"] if f in CHARACTER_PROFILES else f"Custom Avatar ({f}) ✨"
        for f in available_vrms
    ]
    selected_idx = st.selectbox(
        "🎭 Switch 3D Character",
        range(len(available_vrms)),
        format_func=lambda i: vrm_labels[i]
    )
    selected_vrm_file = available_vrms[selected_idx]

    custom_vrm_upload = st.file_uploader("➕ Or Upload Temporary .VRM", type=["vrm"])

    if custom_vrm_upload is not None:
        active_char = {
            "name": custom_vrm_upload.name.replace(".vrm", "").title(),
            "icon": "✨",
            "bio": f"You are {custom_vrm_upload.name.replace('.vrm', '').title()}, a lively anime companion created by katanaking.",
            "greeting": f"*waves happily* Hi katanaking! {custom_vrm_upload.name.replace('.vrm', '').title()} is loaded and ready! (✿◠‿◠)",
            "default_pitch": 1.42,
            "default_mood": 0
        }
        vrm_bytes = custom_vrm_upload.getvalue()
        mem_key = f"custom_{custom_vrm_upload.name}"
    else:
        prof = CHARACTER_PROFILES.get(selected_vrm_file, {
            "name": selected_vrm_file.replace(".vrm", "").title(),
            "icon": "🌸",
            "bio": f"You are {selected_vrm_file.replace('.vrm', '').title()}, an anime companion built by katanaking.",
            "greeting": f"*waves happily* Hello katanaking! {selected_vrm_file.replace('.vrm', '').title()} reporting in! (✿◠‿◠)",
            "default_pitch": 1.42,
            "default_mood": 0
        })
        active_char = prof
        with open(selected_vrm_file, "rb") as f:
            vrm_bytes = f.read()
        mem_key = selected_vrm_file.replace(".vrm", "")

    if vrm_bytes.startswith(b"version https://git-lfs"):
        st.error(
            f"⚠️ **Git LFS Pointer Detected!** `{selected_vrm_file}` on GitHub is a tiny LFS text pointer instead of the 3D binary. "
            "Please upload the raw `.vrm` file via the GitHub web interface!"
        )
        st.stop()

    layout_mode = st.radio(
        "🖥️ View Layout Mode",
        ["Split Studio View", "Full-Screen Theater HUD 🎬"],
        index=0
    )

    mood_options = [
        "Sweet & Loving 🌸",
        "Tsundere 💢",
        "Energetic & Playful ✨",
        "Rude & Sarcastic 🙄"
    ]
    mood_mode = st.selectbox(
        "Personality Mode",
        mood_options,
        index=active_char.get("default_mood", 0),
        key=f"mood_{mem_key}"
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
    voice_pitch = st.slider(
        "Voice Pitch", 0.8, 1.8, float(active_char["default_pitch"]), 0.05, key=f"pitch_{mem_key}"
    )
    voice_rate = st.slider("Speaking Speed", 0.8, 1.4, 1.05, 0.05)

    st.markdown("---")
    st.markdown("### 🎙️ Voice Input")
    mic_html = f"""
    <div style="text-align: center; font-family: sans-serif;">
      <button onclick="startListening()" style="background:#ff69b4; color:white; border:none; padding:8px 16px; border-radius:18px; font-weight:bold; cursor:pointer; width:100%;">🎙️ Tap to Speak</button>
      <p id="mic-status" style="font-size:11px; color:#aaa; margin-top:6px; margin-bottom:0;">Speak directly to {active_char['name']}</p>
    </div>
    <script>
    function startListening() {{
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) {{ alert("Speech recognition requires Chrome."); return; }}
      const rec = new SR();
      rec.lang = 'en-US';
      const stEl = document.getElementById('mic-status');
      stEl.textContent = "Listening...";
      rec.onresult = (e) => {{
        const txt = e.results[0][0].transcript;
        stEl.textContent = "Heard: " + txt;
        const inp = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
        if (inp) {{
          const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
          setter.call(inp, txt);
          inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
      }};
      rec.onerror = () => {{ stEl.textContent = "Mic error. Try again."; }};
      rec.start();
    }}
    </script>
    """
    components.html(mic_html, height=70)

MEMORY_FILE = f"chat_memory_{mem_key}.json"

def load_memory(default_prompt, greeting_msg):
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
        {"role": "assistant", "content": greeting_msg}
    ]

def save_memory(messages):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(messages[-30:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_viewer_html(html_path="index.html", raw_vrm_bytes=b"", char_name="Lily-Hime"):
    if not os.path.exists(html_path) or not raw_vrm_bytes:
        return ""
    b64_vrm = base64.b64encode(raw_vrm_bytes).decode("utf-8")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return (
        html_content
        .replace("__VRM_BASE64__", b64_vrm)
        .replace("__CHAR_NAME__", char_name)
    )

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

def detect_actions(text, user_text="", is_rude=False):
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
    if any(w in full for w in ["look away", "looks away", "turns away", "avert", "hides face", "sigh", "roll"]):
        if "look_away" not in found: found.append("look_away")
    if any(w in full for w in ["blush", "shy", "fluster", "embarrass", "relentless", "//"]):
        if "blush" not in found: found.append("blush")
    if any(w in full for w in ["giggle", "laugh", "hehe", "teehee", "chuckle", "smirk", "scoff"]):
        if "giggle" not in found: found.append("giggle")
    if any(w in full for w in ["wave", "konnichiwa", "greet", "hello", "yahallo"]):
        if "wave" not in found: found.append("wave")
    if any(w in full for w in ["angry", "pout", "hmph", "mad", "frown", "puff", "annoy", "ugh", "glare", "crosses arms"]):
        if "angry" not in found: found.append("angry")
    if any(w in full for w in ["sad", "cry", "tear", "sob", "sniff", "whimper"]):
        if "sad" not in found: found.append("sad")

    if not found:
        found.append("angry" if is_rude else "happy")
    return found

is_rude_mode = "Rude" in mood_mode

if "Sweet" in mood_mode:
    mood_prompt = "You are warm, devoted, and affectionate toward Master katanaking."
    action_examples = "*blushes deeply*, *giggles shyly*, *waves happily*, or *strikes an idol pose*"
    emoji_style = "(✿◠‿◠)"
elif "Tsundere" in mood_mode:
    mood_prompt = "You are a sharp-tongued tsundere! Act flustered and stubborn while secretly caring about katanaking."
    action_examples = "*blushes deeply*, *shyly looks away*, *pouts*, or *giggles shyly*"
    emoji_style = "(⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)"
elif is_rude_mode:
    mood_prompt = (
        "You are RUDE, blunt, sarcastic, and brutally honest! Roasts and snappy comebacks only. "
        "Never call him 'Master' politely—mock him, sigh at his questions, roll your eyes, and act like talking to him is a huge chore."
    )
    action_examples = "*pouts and crosses arms*, *sighs and looks away*, *glares annoyed*, or *scoffs*"
    emoji_style = "(¬_¬)"
else:
    mood_prompt = "You are upbeat, witty, and playful!"
    action_examples = "*waves happily*, *does a cute twirl*, *giggles shyly*, or *strikes an idol pose*"
    emoji_style = "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧"

SYSTEM_PROMPT = (
    f"{active_char['bio']} {mood_prompt} "
    f"Always start your reply with a roleplay action in asterisks like {action_examples}, "
    f"along with text kaomoji like {emoji_style}. Keep responses punchy (1 to 2 sentences max). "
    "katanaking coded and created you! If shown an image, react in character to what you see!"
)

state_msg_key = f"messages_{mem_key}"
if state_msg_key not in st.session_state:
    st.session_state[state_msg_key] = load_memory(SYSTEM_PROMPT, active_char["greeting"])
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

st.session_state[state_msg_key][0]["content"] = SYSTEM_PROMPT
active_messages = st.session_state[state_msg_key]

with st.sidebar:
    st.markdown("---")
    st.markdown("### 💾 Memory & Export")
    chat_export_text = "\n\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in active_messages if m["role"] != "system"]
    )
    st.download_button(
        label=f"📥 Download {active_char['name']} Chat",
        data=chat_export_text,
        file_name=f"{mem_key}_chat_log.txt",
        mime="text/plain"
    )
    if st.button(f"🗑️ Clear {active_char['name']} Memory"):
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
        reset_msg = (
            f"*pouts and looks away* Great, you wiped my memory. Happy now, katanaking? (¬_¬)"
            if is_rude_mode else
            f"*waves happily* Memory cleared! Fresh start with {active_char['name']}, katanaking! (✿◠‿◠)"
        )
        st.session_state[state_msg_key] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": reset_msg}
        ]
        st.rerun()

is_fullscreen_hud = "Full-Screen" in layout_mode

@st.fragment
def render_chat_panel(box_height=300):
    if not is_fullscreen_hud:
        st.markdown(f"#### {active_char['icon']} {active_char['name']}'s Room")

    with st.expander(f"📸 Show {active_char['name']} an Image / Screenshot", expanded=False):
        uploaded_img = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed", key=f"img_{mem_key}")
        if uploaded_img:
            st.image(uploaded_img, width=160, caption=f"Ready to show {active_char['name']}!")

    chat_box = st.container(height=box_height)

    with chat_box:
        for message in active_messages:
            if message["role"] == "system":
                continue
            icon = active_char["icon"] if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=icon):
                if message["role"] == "assistant":
                    bubble = f'<div class="anime-bubble">{message["content"]}</div>'
                    st.markdown(bubble, unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])

    if user_input := st.chat_input(f"Talk to {active_char['name']}..."):
        st.session_state.last_user_input = user_input
        display_text = f"🖼️ *[Shared an image]* {user_input}" if uploaded_img else user_input

        with chat_box:
            with st.chat_message("user"):
                st.markdown(display_text)
            active_messages.append({"role": "user", "content": display_text})

            try:
                with st.chat_message("assistant", avatar=active_char["icon"]):
                    api_messages = [m.copy() for m in active_messages[-10:]]

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
                        temperature=0.8 if is_rude_mode else 0.7
                    )
                    ai_response = response.choices[0].message.content
                    bubble = f'<div class="anime-bubble">{ai_response}</div>'
                    st.markdown(bubble, unsafe_allow_html=True)

                active_messages.append({"role": "assistant", "content": ai_response})
                save_memory(active_messages)
            except Exception as e:
                st.error(f"⚠️ API call failed: {e}")

    last_msg = active_messages[-1]["content"] if active_messages else ""
    state_payload = json.dumps({
        "type": "LILY_STATE",
        "actions": detect_actions(last_msg, st.session_state.last_user_input, is_rude=is_rude_mode),
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

viewer_html = get_viewer_html("index.html", vrm_bytes, active_char["name"])

if is_fullscreen_hud:
    if viewer_html:
        components.html(viewer_html, height=640, scrolling=False)
    else:
        st.error(f"⚠️ Ensure index.html and {selected_vrm_file} are at repo root.")
    render_chat_panel(box_height=180)
else:
    model_column, chat_column = st.columns([0.46, 0.54])
    with model_column:
        if viewer_html:
            components.html(viewer_html, height=430, scrolling=False)
        else:
            st.error(f"⚠️ Ensure index.html and {selected_vrm_file} are at repo root.")
    with chat_column:
        render_chat_panel(box_height=300)
