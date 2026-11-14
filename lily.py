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

# Custom CSS to make the VRM iframe a full-screen background behind the chat
st.markdown("""
<style>
  /* Make Streamlit main containers transparent so the 3D background shows through */
  .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
      background: transparent !important;
  }

  /* Pin the VRM iframe to cover the entire screen in the background */
  iframe {
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      z-index: 0 !important;
      border: none !important;
  }

  /* Keep the main chat container above the 3D model */
  .block-container {
      position: relative !important;
      z-index: 5 !important;
      padding-top: 1.5rem !important;
      max-width: 720px !important;
  }

  /* Title pill styling */
  .title-banner {
      display: inline-block;
      background: rgba(255, 255, 255, 0.78);
      backdrop-filter: blur(8px);
      padding: 8px 20px;
      border-radius: 24px;
      border: 1px solid #ffb3d9;
      color: #c2185b;
      font-weight: 800;
      font-size: 1.35rem;
      box-shadow: 0 4px 15px rgba(255, 105, 180, 0.2);
      margin-bottom: 10px;
  }

  /* Make the scrollable chat container slightly translucent & pushed to the lower half */
  [data-testid="stVerticalBlockBorderWrapper"] {
      background: rgba(255, 255, 255, 0.35) !important;
      backdrop-filter: blur(4px) !important;
      border-radius: 20px !important;
      border: 1px solid rgba(255, 182, 193, 0.5) !important;
      margin-top: 26vh !important;
  }

  /* Chat message bubbles */
  [data-testid="stChatMessage"] {
      background: rgba(255, 255, 255, 0.82) !important;
      backdrop-filter: blur(6px);
      border-radius: 16px !important;
      border: 1px solid rgba(255, 182, 193, 0.6) !important;
      margin-bottom: 8px !important;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  }

  .anime-bubble {
      background: rgba(255, 182, 193, 0.22);
      border-left: 4px solid #ff69b4;
      padding: 10px 14px;
      border-radius: 12px;
      color: #4a154b;
      font-weight: 500;
  }

  /* Keep bottom chat input box above the background */
  [data-testid="stBottom"], [data-testid="stChatInput"] {
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

def build_vrm_html(b64_vrm, last_reply=""):
    speech = clean_for_speech(last_reply)
    safe_speech_json = json.dumps(speech)

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
    .controls {
      position: absolute;
      top: 60px;
      right: 16px;
      display: flex;
      gap: 6px;
      background: rgba(255, 255, 255, 0.88);
      padding: 7px 10px;
      border-radius: 24px;
      box-shadow: 0 4px 15px rgba(255, 105, 180, 0.25);
      z-index: 20;
    }
    .btn {
      border: 1px solid #ffb3d9;
      background: white;
      color: #c2185b;
      padding: 6px 10px;
      border-radius: 16px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
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
    <button class="btn" onclick="triggerAction('happy')">😊 Happy</button>
    <button class="btn" onclick="triggerAction('nod')">🙇‍♀️ Nod</button>
    <button class="btn" onclick="triggerAction('dance')">💃 Dance</button>
    <button class="btn" onclick="speakReply()">🔊 Voice</button>
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
    const lastReply = __LAST_REPLY_JSON__;

    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const blobUrl = URL.createObjectURL(new Blob([bytes], { type: "application/octet-stream" }));

    let currentVrm = null;
    let baseHipsY = 0;
    let actionMode = "idle";
    let actionTimer = 0;
    let talkTimer = 0;

    window.triggerAction = (mode) => {
      actionMode = mode;
      actionTimer = 3.5;
    };

    window.speakReply = () => {
      const textToSay = lastReply || "Konnichiwa Master katanaking!";
      talkTimer = Math.min(7.0, Math.max(2.5, textToSay.length * 0.06));
      window.triggerAction("happy");

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

        // Save initial hip height so breathing animation doesn't drop her to the bottom
        const hips = vrm.humanoid?.getNormalizedBoneNode('hips');
        if (hips) baseHipsY = hips.position.y;

        // Auto-center the model horizontally and frame her upper body in the top half
        vrm.scene.updateMatrixWorld(true);
        const box = new THREE.Box3().setFromObject(vrm.scene);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        vrm.scene.position.x = -center.x;
        vrm.scene.position.z = -center.z;

        const focusY = box.min.y + size.y * 0.68;
        controls.target.set(0.0, focusY, 0.0);
        camera.position.set(0.0, focusY + 0.10, 2.05);
        controls.update();

        currentVrm = vrm;
        status.style.display = 'none';

        if (lastReply && lastReply.length > 0) {
          talkTimer = Math.min(6.0, Math.max(2.5, lastReply.length * 0.06));
          window.triggerAction("happy");
        }
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
          if (actionTimer <= 0) actionMode = "idle";
        }
        if (talkTimer > 0) talkTimer -= delta;

        // 1. Breathing & Idle Sway (Preserving baseHipsY)
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
          leftUpperArm.rotation.z = 1.15 + Math.sin(t * 2.0) * 0.03;
          leftUpperArm.rotation.x = 0.08;
        }
        if (leftLowerArm) {
          leftLowerArm.rotation.z = 0.15;
          leftLowerArm.rotation.y = 0.2;
        }
        if (rightUpperArm) {
          rightUpperArm.rotation.z = -1.15 - Math.sin(t * 2.0) * 0.03;
          rightUpperArm.rotation.x = 0.08;
        }
        if (rightLowerArm) {
          rightLowerArm.rotation.z = -0.15;
          rightLowerArm.rotation.y = -0.2;
        }

        // 3. Cute Non-Arm Actions (Happy Bounce, Polite Nod, Dance Sway)
        if (actionMode === "happy") {
          if (hips) {
            hips.position.y = baseHipsY + Math.abs(Math.sin(t * 5.5)) * 0.025;
          }
          if (head) {
            head.rotation.z = 0.14;
            head.rotation.x = Math.sin(t * 5.5) * 0.05;
          }
        } else if (actionMode === "nod") {
          if (spine) {
            spine.rotation.x = Math.abs(Math.sin(t * 4.5)) * 0.12;
          }
          if (head) {
            head.rotation.x = Math.abs(Math.sin(t * 4.5)) * 0.18;
          }
        } else if (actionMode === "dance") {
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

        // 4. Facial Expressions & Lip-Sync
        if (exp) {
          const isHappy = (actionMode !== "idle");
          exp.setValue('happy', isHappy ? 0.85 : 0.15);

          const rawBlink = Math.max(0, Math.sin(t * 1.4) - 0.96) * 25;
          exp.setValue('blink', isHappy ? 0.0 : Math.min(1.0, rawBlink));

          if (talkTimer > 0) {
            exp.setValue('aa', Math.abs(Math.sin(t * 13.0)) * 0.75);
            exp.setValue('oh', Math.abs(Math.cos(t * 9.0)) * 0.35);
          } else {
            exp.setValue('aa', 0.0);
            exp.setValue('oh', 0.0);
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

    html_template = html_template.replace("__VRM_BASE64__", b64_vrm)
    html_template = html_template.replace("__LAST_REPLY_JSON__", safe_speech_json)
    return html_template

# --- CHAT INTERFACE ---
st.markdown('<div class="title-banner">🦊 Lily-Hime\'s Room 🌸</div>', unsafe_allow_html=True)

SYSTEM_PROMPT = (
    "Your name is Lily-Hime. You are a cheerful, sweet, anime girl character. "
    "You speak using text emojis like (✿◠‿◠) and cute expressions. "
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

chat_box = st.container(height=320)
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
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=st.session_state.messages,
                    max_tokens=150
                )
                lily_response = response.choices[0].message.content
                bubble = f'<div class="anime-bubble">{lily_response}</div>'
                st.markdown(bubble, unsafe_allow_html=True)
            st.session_state.messages.append(
                {"role": "assistant", "content": lily_response}
            )
        except Exception as e:
            st.error(f"⚠️ API call failed: {e}")

# --- 3D BACKGROUND VIEWER ---
vrm_b64 = load_vrm_b64("lily_model.vrm")
last_msg = ""
if "messages" in st.session_state and len(st.session_state.messages) > 0:
    if st.session_state.messages[-1]["role"] == "assistant":
        last_msg = st.session_state.messages[-1]["content"]

if vrm_b64:
    viewer_html = build_vrm_html(vrm_b64, last_msg)
    components.html(viewer_html, height=800, scrolling=False)
else:
    st.error("⚠️ lily_model.vrm not found at repo root.")
