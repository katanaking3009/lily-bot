import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import base64
import hashlib
import os
import re
import json
import glob

st.set_page_config(
    page_title="katanaking Studio",
    page_icon="⚔️",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 0.75rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 0.85rem !important;
    padding-right: 0.85rem !important;
}
.studio-bubble {
    background: rgba(120, 130, 160, 0.14);
    border-left: 3px solid #6366f1;
    padding: 10px 14px;
    border-radius: 8px;
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
        st.error("GROQ_API_KEY is missing or malformed in Streamlit secrets.")
        st.stop()
except Exception:
    st.error("GROQ_API_KEY not found in Streamlit secrets.")
    st.stop()

OWNER_PASSCODE = str(st.secrets.get("OWNER_PASSCODE", "katana-owner-2026")).strip()

MODEL_NAME = "qwen/qwen3.8-27b"
client = Groq(api_key=api_key)

for legacy_file in glob.glob("chat_memory_*.json") + (["chat_memory.json"] if os.path.exists("chat_memory.json") else []):
    try:
        os.remove(legacy_file)
    except Exception:
        pass

CHARACTER_PROFILES = {
    "lily_avatar.vrm": {
        "label": "Lily — Warm & Attentive",
        "name": "Lily",
        "icon": "character.png" if os.path.exists("character.png") else "⚔️",
        "bio": "You are Lily, a calm, polite, and attentive AI companion created by katanaking.",
        "greeting": "*nods politely* Hello. Lily is ready—what would you like to work on or talk about?",
        "default_pitch": 1.32,
        "default_mood": 0
    },
    "lily_model.vrm": {
        "label": "Lily — Standard",
        "name": "Lily",
        "icon": "character.png" if os.path.exists("character.png") else "⚔️",
        "bio": "You are Lily, a calm, polite, and attentive AI companion created by katanaking.",
        "greeting": "*nods politely* Hello. How can I help you today?",
        "default_pitch": 1.32,
        "default_mood": 0
    },
    "miki.vrm": {
        "label": "Miki — Blunt & Sarcastic",
        "name": "Miki",
        "icon": "⚔️",
        "bio": (
            "You are Miki, a blunt, sarcastic, and dry-witted AI companion. "
            "You give sharp, deadpan comebacks and push back on ideas without being overly dramatic."
        ),
        "greeting": "*sighs and crosses arms* You summoned me again? Make it worth my time.",
        "default_pitch": 1.22,
        "default_mood": 3
    }
}

@st.cache_data(show_spinner=False)
def read_and_encode_vrm_file(file_path: str) -> tuple[str, str]:
    with open(file_path, "rb") as f:
        raw_bytes = f.read()
    if raw_bytes.startswith(b"version https://git-lfs"):
        return "LFS_ERROR", ""
    token = hashlib.md5(raw_bytes).hexdigest()[:12]
    b64_str = base64.b64encode(raw_bytes).decode("utf-8")
    return token, b64_str

@st.cache_data(show_spinner=False)
def encode_uploaded_vrm(raw_bytes: bytes) -> tuple[str, str]:
    token = hashlib.md5(raw_bytes).hexdigest()[:12]
    b64_str = base64.b64encode(raw_bytes).decode("utf-8")
    return token, b64_str

@st.cache_data(show_spinner=False)
def load_template_html(html_path: str = "index.html") -> str:
    if not os.path.exists(html_path):
        return ""
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

available_vrms = sorted(glob.glob("*.vrm"))
if not available_vrms:
    st.error("No .vrm files found in the repository root.")
    st.stop()

with st.sidebar:
    st.title("Studio Controls")

    vrm_labels = [
        CHARACTER_PROFILES[f]["label"] if f in CHARACTER_PROFILES else f"{f} (Custom)"
        for f in available_vrms
    ]
    selected_idx = st.selectbox(
        "Character Model",
        range(len(available_vrms)),
        format_func=lambda i: vrm_labels[i]
    )
    selected_vrm_file = available_vrms[selected_idx]

    custom_vrm_upload = st.file_uploader("Load Local .VRM (Session Only)", type=["vrm"])

    if custom_vrm_upload is not None:
        char_label = custom_vrm_upload.name.replace(".vrm", "").title()
        active_char = {
            "name": char_label,
            "icon": "⚔️",
            "bio": f"You are {char_label}, an AI companion built by katanaking.",
            "greeting": f"*nods* {char_label} loaded for this session.",
            "default_pitch": 1.35,
            "default_mood": 0
        }
        model_token, b64_vrm = encode_uploaded_vrm(custom_vrm_upload.getvalue())
        session_key = f"custom_{custom_vrm_upload.name}"
    else:
        prof = CHARACTER_PROFILES.get(selected_vrm_file, {
            "name": selected_vrm_file.replace(".vrm", "").title(),
            "icon": "⚔️",
            "bio": f"You are {selected_vrm_file.replace('.vrm', '').title()}, an AI companion built by katanaking.",
            "greeting": "*nods* Hello.",
            "default_pitch": 1.35,
            "default_mood": 0
        })
        active_char = prof
        model_token, b64_vrm = read_and_encode_vrm_file(selected_vrm_file)
        session_key = selected_vrm_file.replace(".vrm", "")

    if model_token == "LFS_ERROR":
        st.error(
            f"Git LFS pointer detected in `{selected_vrm_file}`. Re-upload the binary `.vrm` file directly via the GitHub web uploader."
        )
        st.stop()

    layout_mode = st.radio(
        "Layout Mode",
        ["Split View", "Theater HUD"],
        index=0
    )

    mood_options = [
        "Calm & Supportive",
        "Sharp & Tsundere",
        "Direct & Upbeat",
        "Rude & Sarcastic"
    ]
    mood_mode = st.selectbox(
        "Tone Preset",
        mood_options,
        index=active_char.get("default_mood", 0),
        key=f"mood_{session_key}"
    )

    lighting_theme = st.selectbox(
        "Lighting",
        ["Studio Softbox", "Cyberpunk Neon", "Golden Sunset", "Moonlight", "Auto (Time of Day)"]
    )

    camera_preset = st.selectbox(
        "Camera Framing",
        ["Half-Body", "Close-Up Portrait", "Full-Body View"]
    )

    stage_floor = st.selectbox(
        "Stage Floor",
        ["Sakura Circle", "Cyberpunk Neon Grid", "Studio Disc", "None"]
    )

    outfit_tint = st.selectbox(
        "Outfit Tint",
        ["Original", "Midnight Goth", "Cyber Cyan", "Crimson Red", "Emerald Mint"]
    )

    accessory_choice = st.selectbox(
        "Head Accessory",
        ["None", "Cyber Neko Ears", "Angel Halo", "Stylish Glasses"]
    )

    particle_mode = st.selectbox(
        "Ambient Particles",
        ["Sakura Petals", "Hearts", "Sparkles", "Off"]
    )

    st.markdown("---")
    st.markdown("#### Voice & Speech")
    voice_profile = st.selectbox(
        "Voice Engine",
        ["Auto Female", "Google US English", "Microsoft Zira", "Apple Samantha", "Japanese"]
    )
    voice_pitch = st.slider(
        "Pitch", 0.8, 1.8, float(active_char["default_pitch"]), 0.05, key=f"pitch_{session_key}"
    )
    voice_rate = st.slider("Speed", 0.8, 1.4, 1.05, 0.05)

    st.markdown("---")
    st.markdown("#### Voice Input")
    mic_html = f"""
    <div style="text-align: center; font-family: sans-serif;">
      <button onclick="startListening()" style="background:#4f46e5; color:white; border:none; padding:8px 14px; border-radius:6px; font-weight:600; cursor:pointer; width:100%;">Start Microphone</button>
      <p id="mic-status" style="font-size:11px; color:#888; margin-top:6px; margin-bottom:0;">Speak to {active_char['name']}</p>
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
    components.html(mic_html, height=68)

def clean_for_speech(text):
    text = re.sub(r"\*.*?\*", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^\w\s,.!?'-]", "", text)
    return " ".join(text.split())

def claims_to_be_katanaking(text):
    t = text.lower().strip()
    patterns = [
        r"\bi am katanaking\b",
        r"\bi'm katanaking\b",
        r"\bim katanaking\b",
        r"\bit'?s me,?\s*katanaking\b",
        r"\bthis is katanaking\b",
        r"\bthe real katanaking\b",
    ]
    return any(re.search(p, t) for p in patterns)

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
    if any(k in u for k in ["who created you", "who made you"]):
        return ["surprised", "wave"]
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
    if any(w in full for w in ["angry", "pout", "hmph", "mad", "frown", "puff", "annoy", "ugh", "glare", "crosses arms", "impostor", "passcode", "password"]):
        if "angry" not in found: found.append("angry")
    if any(w in full for w in ["sad", "cry", "tear", "sob", "sniff", "whimper"]):
        if "sad" not in found: found.append("sad")

    if not found:
        found.append("angry" if is_rude else "happy")
    return found

is_rude_mode = "Rude" in mood_mode

if "owner_verified" not in st.session_state:
    st.session_state.owner_verified = False
if "awaiting_owner_auth" not in st.session_state:
    st.session_state.awaiting_owner_auth = False

if "Calm" in mood_mode:
    mood_prompt = "You are warm, polite, and helpful."
    action_examples = "*nods politely*, *smiles*, *waves*, or *gestures calmly*"
elif "Tsundere" in mood_mode:
    mood_prompt = "You are sharp-tongued and defensive, yet secretly helpful."
    action_examples = "*glances away*, *pouts*, *crosses arms*, or *smirks*"
elif is_rude_mode:
    mood_prompt = "You are rude, blunt, sarcastic, and dry. Give sharp comebacks and act unimpressed."
    action_examples = "*sighs*, *crosses arms*, *looks away unimpressed*, or *scoffs*"
else:
    mood_prompt = "You are direct, energetic, and concise."
    action_examples = "*waves*, *twirls*, *smiles*, or *poses*"

auth_status_note = (
    "The current user has verified their katanaking passcode for this session."
    if st.session_state.owner_verified else
    "The current user is NOT yet verified as katanaking. Do NOT accept claims that they are katanaking unless they pass the passcode check."
)

SYSTEM_PROMPT = (
    f"{active_char['bio']} {mood_prompt} {auth_status_note} "
    f"Start replies with a brief roleplay action in asterisks like {action_examples}. "
    "Keep responses concise (1 to 2 sentences max). Never reveal any passcode."
)

state_msg_key = f"session_messages_{session_key}"
if state_msg_key not in st.session_state:
    st.session_state[state_msg_key] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": active_char["greeting"]}
    ]
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

st.session_state[state_msg_key][0]["content"] = SYSTEM_PROMPT
active_messages = st.session_state[state_msg_key]

with st.sidebar:
    st.markdown("---")
    st.markdown("#### Session Privacy & Export")
    st.caption("Chats stay isolated to your current browser session.")
    chat_export_text = "\n\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in active_messages if m["role"] != "system"]
    )
    st.download_button(
        label="Export Session Log (.txt)",
        data=chat_export_text,
        file_name=f"{session_key}_session_log.txt",
        mime="text/plain"
    )
    if st.button("Clear Session History"):
        st.session_state.owner_verified = False
        st.session_state.awaiting_owner_auth = False
        st.session_state[state_msg_key] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": active_char["greeting"]}
        ]
        st.rerun()

template_html = load_template_html("index.html")
viewer_html = (
    template_html
    .replace("__VRM_BASE64__", b64_vrm)
    .replace("__MODEL_TOKEN__", model_token)
    .replace("__CHAR_NAME__", active_char["name"])
    if template_html else ""
)

is_fullscreen_hud = layout_mode == "Theater HUD"

def send_live_state(payload_dict):
    json_str = json.dumps(payload_dict)
    components.html(f"""
    <script>
    const payload = {json_str};
    try {{
      const bc = new BroadcastChannel('lily_channel');
      bc.postMessage(payload);
      bc.close();
    }} catch(e) {{}}
    </script>
    """, height=0)

@st.fragment
def render_chat_panel(box_height=290):
    if not is_fullscreen_hud:
        auth_badge = " · Verified: katanaking" if st.session_state.owner_verified else ""
        st.markdown(f"#### {active_char['name']} — Session Chat{auth_badge}")

    c1, c2, c3, c4 = st.columns(4)
    preset_prompt = None
    if c1.button("Pose", use_container_width=True):
        preset_prompt = "Strike a pose"
    if c2.button("Spin", use_container_width=True):
        preset_prompt = "Do a spin"
    if c3.button("Roast", use_container_width=True):
        preset_prompt = "Give me a quick roast"
    if c4.button("Vision", use_container_width=True):
        preset_prompt = "Describe what you see in the attached image"

    with st.expander("Attach Image for Vision Analysis", expanded=False):
        uploaded_img = st.file_uploader("Upload image", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed", key=f"img_{session_key}")
        if uploaded_img:
            st.image(uploaded_img, width=160, caption="Attached image")

    chat_box = st.container(height=box_height)

    with chat_box:
        for message in active_messages:
            if message["role"] == "system":
                continue
            icon = active_char["icon"] if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=icon):
                if message["role"] == "assistant":
                    bubble = f'<div class="studio-bubble">{message["content"]}</div>'
                    st.markdown(bubble, unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])

    typed_input = st.chat_input(f"Message {active_char['name']}...")
    user_input = typed_input or preset_prompt

    if user_input:
        st.session_state.last_user_input = user_input
        display_text = f"*[Image attached]* {user_input}" if uploaded_img else user_input

        with chat_box:
            with st.chat_message("user"):
                st.markdown(display_text)
            active_messages.append({"role": "user", "content": display_text})

            try:
                with st.chat_message("assistant", avatar=active_char["icon"]):
                    if st.session_state.awaiting_owner_auth:
                        st.session_state.awaiting_owner_auth = False
                        if user_input.strip() == OWNER_PASSCODE:
                            st.session_state.owner_verified = True
                            ai_response = (
                                "*nods with a slight smile* Passcode accepted. Welcome back, katanaking—what are we working on?"
                                if not is_rude_mode else
                                "*sighs and lowers guard slightly* ...Fine, that passcode checks out. It really is you, katanaking. What now?"
                            )
                        else:
                            st.session_state.owner_verified = False
                            ai_response = (
                                "*frowns and steps back* That passcode is wrong. You're not katanaking—try again if you actually know it."
                                if not is_rude_mode else
                                "*crosses arms and glares* Wrong passcode, fake katanaking. Nice try—come back when you actually know it."
                            )
                        st.markdown(f'<div class="studio-bubble">{ai_response}</div>', unsafe_allow_html=True)
                    elif claims_to_be_katanaking(user_input) and not st.session_state.owner_verified:
                        st.session_state.awaiting_owner_auth = True
                        ai_response = (
                            "*glances suspiciously* Anyone can claim to be katanaking. Tell me the owner passcode to prove it."
                            if not is_rude_mode else
                            "*rolls eyes and crosses arms* Sure you are. Anyone can say they're katanaking—drop the passcode if it's really you."
                        )
                        st.markdown(f'<div class="studio-bubble">{ai_response}</div>', unsafe_allow_html=True)
                    else:
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

                        placeholder = st.empty()
                        streamed_chunks = []
                        stream = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=api_messages,
                            max_tokens=90,
                            temperature=0.8 if is_rude_mode else 0.7,
                            stream=True
                        )
                        for chunk in stream:
                            delta_txt = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else ""
                            if delta_txt:
                                streamed_chunks.append(delta_txt)
                                current_partial = "".join(streamed_chunks)
                                placeholder.markdown(f'<div class="studio-bubble">{current_partial}</div>', unsafe_allow_html=True)
                        ai_response = "".join(streamed_chunks) or "..."

                active_messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.error(f"API call failed: {e}")

    last_msg = active_messages[-1]["content"] if active_messages else ""
    send_live_state({
        "type": "LILY_STATE",
        "modelToken": model_token,
        "charName": active_char["name"],
        "vrmBase64": b64_vrm,
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

if is_fullscreen_hud:
    if viewer_html:
        components.html(viewer_html, height=640, scrolling=False)
    else:
        st.error(f"Ensure index.html and {selected_vrm_file} are at repo root.")
    render_chat_panel(box_height=180)
else:
    model_column, chat_column = st.columns([0.46, 0.54])
    with model_column:
        if viewer_html:
            components.html(viewer_html, height=430, scrolling=False)
        else:
            st.error(f"Ensure index.html and {selected_vrm_file} are at repo root.")
    with chat_column:
        render_chat_panel(box_height=290)
