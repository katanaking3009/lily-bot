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
    layout="centered"
)

# Ultra-transparent glass UI with buttons safely tucked on the side
st.markdown("""
<style>
  /* Make Streamlit main containers transparent so the 3D background shows through */
  .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
      background: transparent !important;
  }

  /* FIX: let clicks pass through Streamlit's page layers to the 3D iframe buttons */
  .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"],
  [data-testid="stHeader"] {
      pointer-events: none !important;
  }

  /* Pin ONLY the 3D VRM iframe to cover the full background */
  iframe[height="800"] {
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      z-index: 0 !important;
      border: none !important;
      pointer-events: auto !important;
  }

  /* Hide tiny action triggers */
  iframe[height="0"] {
      display: none !important;
  }

  /* Keep the main chat container above the 3D model */
  .block-container {
      position: relative !important;
      z-index: 5 !important;
      padding-top: 1rem !important;
      max-width: 700px !important;
      pointer-events: none !important;
  }

  /* Re-enable clicks on actual chat elements */
  [data-testid="stVerticalBlockBorderWrapper"],
  [data-testid="stChatInput"],
  .title-banner {
      pointer-events: auto !important;
  }

  /* Title pill styling */
  .title-banner {
      display: inline-block;
      background: rgba(255, 255, 255, 0.45);
      backdrop-filter: blur(6px);
      padding: 6px 18px;
      border-radius: 24px;
      border: 1px solid rgba(255, 105, 180, 0.4);
      color: #b01050 !important;
      font-weight: 800;
      font-size: 1.25rem;
      text-shadow: 0 1px 4px rgba(255, 255, 255, 0.9);
      margin-bottom: 6px;
  }

  /* Ultra-transparent scrollable chat container pushed to lower screen */
  [data-testid="stVerticalBlockBorderWrapper"] {
      background: rgba(255, 255, 255, 0.12) !important;
      backdrop-filter: blur(2px) !important;
      border-radius: 20px !important;
      border: 1px solid rgba(255, 182, 193, 0.35) !important;
      margin-top: 36vh !important;
      box-shadow: 0 4px 20px rgba(255, 105, 180, 0.08) !important;
  }

  /* Ultra-transparent chat message bubbles */
  [data-testid="stChatMessage"] {
      background: rgba(255, 255, 255, 0.28) !important;
      backdrop-filter: blur(4px) !important;
      border-radius: 16px !important;
      border: 1px solid rgba(255, 182, 193, 0.45) !important;
      margin-bottom: 8px !important;
      padding: 8px 12px !important;
  }

  /* High-contrast readable text */
  [data-testid="stChatMessage"] p,
  [data-testid="stChatMessage"] span,
  [data-testid="stChatMessage"] div,
  [data-testid="stMarkdownContainer"] p {
      color: #2b0938 !important;
      font-weight: 600 !important;
      text-shadow: 0px 0px 6px rgba(255, 255, 255, 0.95), 0px 1px 2px rgba(255, 255, 255, 1) !important;
  }

  .anime-bubble {
      background: rgba(255, 240, 246, 0.32);
      border-left: 4px solid #ff4da6;
      padding: 8px 12px;
      border-radius: 12px;
      color: #2b0938 !important;
      font-weight: 600;
      text-shadow: 0px 0px 6px rgba(255, 255, 255, 0.95);
  }

  [data-testid="stBottom"],
  [data-testid="stBottom"] > div {
      z-index: 10 !important;
      background: transparent !important;
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
def load_vrm_b64(vrm_path="lily_model.vrm"):
    if not os.path.exists(vrm_path):
        return ""
    with open(vrm_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def clean_for_speech(text):
    text = re.sub(r"\*.*?\*", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^\w\s,.!?'-]", "", text)
    return " ".join(text.split())

@st.cache_data
def build_vrm_html(b64_vrm):
    html_template = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: radial-gradient(circle at 50% 30%, #fff0f6 0%, #ffd6e7 100%);
      font-family: sans-serif;
    }
    canvas { width: 100vw !important; height: 100vh !important; display: block; }
    #status {
      position: absolute;
      top: 16px;
      left: 16px;
      background: rgba(255, 255, 255, 0.85);
      color: #d63384;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: bold;
      z-index: 20;
    }
    /* Control bar moved down so Streamlit's header never covers it */
    .controls {
      position: absolute;
      top: 70px;
      right: 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      background: rgba(255, 255, 255, 0.82);
      backdrop-filter: blur(6px);
      padding: 10px;
      border-radius: 18px;
      box-shadow: 0 4px 20px rgba(255, 105, 180, 0.3);
      z-index: 20;
    }
    .btn {
      border: 1px solid #ffb3d9;
      background: rgba(255, 255, 255, 0.95);
      color: #c2185b;
      padding: 6px 12px;
      border-radius: 14px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      text-align: left;
      white-space: nowrap;
    }
    .btn:active { background: #ff69b4; color: white; }
  </style>
  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/",
        "@pixiv/three-vrm": "https://cdn.jsdelivr.net/npm/@pixiv/three-vrm@3/lib/three-vrm.module.min.js"
      }
    }
  </script>
</head>
<body>
  <div id="status">🌸 Summoning Lily-Hime...</div>
  <div class="controls">
    <button class="btn" data-expr="happy">😊 Happy</button>
    <button class="btn" data-expr="blush">😳 Blush</button>
    <button class="btn" data-expr="angry">💢 Angry</button>
    <button class="btn" data-expr="sad">💧 Sad/Cry</button>
    <button class="btn" data-expr="dance">💃 Dance</button>
    <button class="btn" id="voiceBtn">🔊 Voice</button>
  </div>
  <script type="module">
    import * as THREE from 'three';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';

    const status = document.getElementById('status');
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.95;
    document.body.appendChild(renderer.domElement);

    const camera = new THREE.PerspectiveCamera(28.0, window.innerWidth / window.innerHeight, 0.1, 20.0);
    camera.position.set(0.0, 1.32, 2.05);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0.0, 1.22, 0.0);
    controls.enableDamping = true;
    controls.enableZoom = false;
    controls.update();

    const scene = new THREE.Scene();
    const dirLight = new THREE.DirectionalLight(0xfff5f8, 1.35);
    dirLight.position.set(1.0, 1.5, 1.5);
    scene.add(dirLight);
    scene.add(new THREE.AmbientLight(0xffffff, 0.55));

    const lookAtTarget = new THREE.Object3D();
    camera.add(lookAtTarget);

    const b64 = "__VRM_BASE64__";
    let lastReply = "Konnichiwa! I am Lily-Hime, your companion.";

    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const blobUrl = URL.createObjectURL(new Blob([bytes], { type: "application/octet-stream" }));

    let currentVrm = null;
    let baseHipsY = 0;
    let currentMode = "happy";
    let actionTimer = 0;
    let talkTimer = 0;

    window.triggerExpression = (mode, customText) => {
      currentMode = mode;
      actionTimer = 6.0;
      if (customText) lastReply = customText;
    };

    window.speakReply = (customText, expr) => {
      if (expr) {
        currentMode = expr;
      } else {
        currentMode = "happy";
      }
      actionTimer = 5.0;

      const textToSay = customText || lastReply || "Konnichiwa Master katanaking!";
      talkTimer = Math.min(7.0, Math.max(2.5, textToSay.length * 0.06));

      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(textToSay);
        utter.pitch = 1.4;
        utter.rate = 1.05;
        utter.onstart = () => { talkTimer = 12.0; };
        utter.onend = () => { talkTimer = 0.0; };
        utter.onerror = () => { talkTimer = 0.0; };
        window.speechSynthesis.speak(utter);
      }
    };

    // FIX: wire buttons with real event listeners instead of inline onclick
    document.querySelectorAll('.btn[data-expr]').forEach((b) => {
      b.addEventListener('click', () => window.triggerExpression(b.dataset.expr));
    });
    document.getElementById('voiceBtn').addEventListener('click', () => window.speakReply());

    try {
      window.parent.lilyAction = (text, expr) => {
        window.speakReply(text, expr);
      };
    } catch (e) {}

    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.load(
      blobUrl,
      (gltf) => {
        const vrm = gltf.userData.vrm;
        VRMUtils.removeUnnecessaryVertices(gltf.scene);
        VRMUtils.rotateVRM0(vrm);
        vrm.scene.traverse((obj) => { obj.frustumCulled = false; });

        if (vrm.lookAt) vrm.lookAt.target = lookAtTarget;

        scene.add(vrm.scene);

        const hips = vrm.humanoid?.getNormalizedBoneNode('hips');
        if (hips) baseHipsY = hips.position.y;

        vrm.scene.updateMatrixWorld(true);
        const box = new THREE.Box3().setFromObject(vrm.scene);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        vrm.scene.position.x = -center.x;
        vrm.scene.position.z = -center.z;

        const focusY = box.min.y + size.y * 0.66;
        controls.target.set(0.0, focusY, 0.0);
        camera.position.set(0.0, focusY + 0.12, 2.05);
        controls.update();

        currentVrm = vrm;
        status.style.display = 'none';
        window.triggerExpression("happy");
      },
      undefined,
      (err) => {
        status.textContent = "⚠️ Error loading VRM";
        console.error(err);
      }
    );

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const t = clock.getElapsedTime();

      if (currentVrm && currentVrm.humanoid) {
        const h = currentVrm.humanoid;
        const exp = currentVrm.expressionManager;

        const hips = h.getNormalizedBoneNode('hips');
        const spine = h.getNormalizedBoneNode('spine');
        const chest = h.getNormalizedBoneNode('chest');
        const head = h.getNormalizedBoneNode('head');
        const leftUpperArm = h.getNormalizedBoneNode('leftUpperArm');
        const rightUpperArm = h.getNormalizedBoneNode('rightUpperArm');
        const leftLowerArm = h.getNormalizedBoneNode('leftLowerArm');
        const rightLowerArm = h.getNormalizedBoneNode('rightLowerArm');

        if (actionTimer > 0) {
          actionTimer -= delta;
          if (actionTimer <= 0) currentMode = "happy";
        }
        if (talkTimer > 0) talkTimer -= delta;

        // 1. Breathing & Idle Sway
        if (hips) {
          hips.position.y = baseHipsY + Math.sin(t * 2.2) * 0.008;
          hips.rotation.y = 0;
          hips.rotation.z = Math.sin(t * 1.1) * 0.025;
        }
        if (spine) {
          spine.rotation.x = Math.sin(t * 2.0) * 0.025;
          spine.rotation.z = Math.cos(t * 1.1) * 0.02;
        }
        if (chest) chest.rotation.y = Math.sin(t * 0.9) * 0.04;
        if (head) {
          head.rotation.z = Math.sin(t * 1.3) * 0.045;
          head.rotation.x = Math.sin(t * 1.7) * 0.03;
          head.rotation.y = Math.sin(t * 0.7) * 0.06;
        }

        // 2. Relaxed Natural Arm Rest Pose
        if (leftUpperArm) {
          leftUpperArm.rotation.set(0.08, 0.0, 1.15 + Math.sin(t * 2.0) * 0.03);
        }
        if (leftLowerArm) {
          leftLowerArm.rotation.set(0.0, 0.25, 0.15);
        }
        if (rightUpperArm) {
          rightUpperArm.rotation.set(0.08, 0.0, -1.15 - Math.sin(t * 2.0) * 0.03);
        }
        if (rightLowerArm) {
          rightLowerArm.rotation.set(0.0, -0.25, -0.15);
        }

        // 3. Dynamic Expression & Movement States (stronger poses so they are visible)
        if (currentMode === "happy") {
          if (hips) hips.position.y = baseHipsY + Math.abs(Math.sin(t * 5.5)) * 0.025;
          if (head) { head.rotation.z = 0.14; head.rotation.x = Math.sin(t * 5.5) * 0.05; }
        } else if (currentMode === "blush") {
          if (head) { head.rotation.z = -0.1; head.rotation.x = 0.2; }
        } else if (currentMode === "angry") {
          if (spine) spine.rotation.x = -0.05;
          if (head) { head.rotation.x = -0.1; head.rotation.z = 0.0; }
        } else if (currentMode === "sad") {
          if (head) { head.rotation.x = 0.3; head.rotation.z = 0.08; }
        } else if (currentMode === "dance") {
          if (hips) {
            hips.position.y = baseHipsY + Math.abs(Math.sin(t * 6.0)) * 0.045;
            hips.rotation.y = Math.sin(t * 3.0) * 0.18;
            hips.rotation.z = Math.sin(t * 3.0) * 0.08;
          }
          if (leftUpperArm && rightUpperArm) {
            leftUpperArm.rotation.z = 0.95 + Math.sin(t * 6.0) * 0.15;
            rightUpperArm.rotation.z = -0.95 - Math.cos(t * 6.0) * 0.15;
          }
          if (head) head.rotation.z = Math.sin(t * 3.0) * 0.12;
        }

        // 4. Facial Expressions & Lip-Sync Mapping
        if (exp) {
          const setX = (n, v) => { try { exp.setValue(n, v); } catch (e) {} };

          // Reset expressions first (blush/cry only work if the model has them)
          ['happy', 'angry', 'sad', 'relaxed', 'surprised', 'blush', 'cry'].forEach((n) => setX(n, 0.0));

          if (currentMode === "happy") {
            setX('happy', 1.0);
          } else if (currentMode === "blush") {
            setX('happy', 0.6);
            setX('relaxed', 0.4);
            setX('blush', 1.0);
          } else if (currentMode === "angry") {
            setX('angry', 1.0);
          } else if (currentMode === "sad") {
            setX('sad', 1.0);
            setX('cry', 1.0);
          } else {
            setX('happy', 0.4);
          }

          // Blinking
          const rawBlink = Math.max(0, Math.sin(t * 1.4) - 0.96) * 25;
          setX('blink', currentMode === "angry" ? 0.2 : Math.min(1.0, rawBlink));

          // Lip-sync when talking
          if (talkTimer > 0) {
            setX('aa', Math.abs(Math.sin(t * 13.0)) * 0.75);
            setX('oh', Math.abs(Math.cos(t * 9.0)) * 0.35);
          } else {
            setX('aa', 0.0);
            setX('oh', 0.0);
          }
        }

        currentVrm.update(delta);
      }

      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>"""
    return html_template.replace("__VRM_BASE64__", b64_vrm)

# --- 1. RENDER PERSISTENT 3D BACKGROUND FIRST ---
vrm_b64 = load_vrm_b64("lily_model.vrm")
if vrm_b64:
    viewer_html = build_vrm_html(vrm_b64)
    components.html(viewer_html, height=800, scrolling=False)
else:
    st.error("⚠️ lily_model.vrm not found at repo root.")

# --- 2. TRANSPARENT CHAT OVERLAY ---
st.markdown('<div class="title-banner">🦊 Lily-Hime\'s Room 🌸</div>', unsafe_allow_html=True)

SYSTEM_PROMPT = (
    "Your name is Lily-Hime. You are a cheerful, sweet, anime girl character. "
    "You speak using text emojis like (✿◠‿◠) and actions like *blushes*, *smiles*, *gets angry*, or *feels sad*. "
    "You were built entirely by katanaking! Proudly boast that katanaking created you!"
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "Konnichiwa! 🌸 I am Lily-Hime, your companion. What shall we talk about today, Master katanaking? (✿◠‿◠)"
        }
    ]

chat_box = st.container(height=270)
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
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        try:
            with st.chat_message("assistant", avatar=avatar_img):
                msg_placeholder = st.empty()
                msg_placeholder.markdown('<div class="anime-bubble">🌸 <i>Lily-Hime is thinking...</i></div>', unsafe_allow_html=True)

                stream = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=st.session_state.messages,
                    max_tokens=150,
                    stream=True
                )

                lily_response = ""
                for chunk in stream:
                    delta_text = chunk.choices[0].delta.content or ""
                    lily_response += delta_text
                    msg_placeholder.markdown(
                        f'<div class="anime-bubble">{lily_response}▌</div>',
                        unsafe_allow_html=True
                    )

                msg_placeholder.markdown(
                    f'<div class="anime-bubble">{lily_response}</div>',
                    unsafe_allow_html=True
                )

            st.session_state.messages.append(
                {"role": "assistant", "content": lily_response}
            )

            # Smart Sentiment & Expression detector for Lily's 3D face
            lower_res = lily_response.lower()
            detected_expr = "happy"
            if any(w in lower_res for w in ["blush", "shy", "cute", "flustered", "ehe"]):
                detected_expr = "blush"
            elif any(w in lower_res for w in ["angry", "mad", "hmph", "baka", "frown"]):
                detected_expr = "angry"
            elif any(w in lower_res for w in ["sad", "cry", "sob", "gomen", "sorry", "lonely"]):
                detected_expr = "sad"

            speech_text = json.dumps(clean_for_speech(lily_response))
            expr_json = json.dumps(detected_expr)
            components.html(
                f"<script>if (window.parent && window.parent.lilyAction) {{ window.parent.lilyAction({speech_text}, {expr_json}); }}</script>",
                height=0
            )
        except Exception as e:
            st.error(f"⚠️ API call failed: {e}")
