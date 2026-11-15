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
    padding-top: 1.2rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
}
.anime-bubble {
    background: rgba(255, 182, 193, 0.18);
    border-left: 4px solid #ff69b4;
    padding: 12px 14px;
    border-radius: 12px;
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

def detect_emotion(text):
    actions = " ".join(re.findall(r"(\*.*?\*|\(.*?\))", text)).lower()
    full = text.lower()
    target = actions if actions else full

    if any(w in target for w in ["wave", "konnichiwa", "greet", "hello"]):
        return "wave"
    if any(w in target for w in ["blush", "shy", "fluster", "embarrass", "peek", "cover"]):
        return "blush"
    if any(w in target for w in ["gasp", "shock", "surpris", "eyes widen"]):
        return "surprised"
    if any(w in target for w in ["angry", "pout", "hmph", "mad", "frown", "puff"]):
        return "angry"
    if any(w in target for w in ["sad", "cry", "tear", "sob", "sniff", "whimper"]):
        return "sad"
    if any(w in target for w in ["giggle", "laugh", "smile", "cheer", "yay", "happy", "grin", "spin"]):
        return "happy"
    return "idle"

def build_vrm_html(b64_vrm, last_reply=""):
    speech = clean_for_speech(last_reply)
    emotion = detect_emotion(last_reply)
    safe_speech_json = json.dumps(speech)
    safe_emotion_json = json.dumps(emotion)

    html_template = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background: radial-gradient(circle at 50% 35%, #fff0f6 0%, #ffd6e7 100%);
      font-family: sans-serif;
    }
    canvas { width: 100vw; height: 100vh; display: block; }
    #status {
      position: absolute;
      top: 12px;
      left: 12px;
      background: rgba(255, 255, 255, 0.85);
      color: #d63384;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: bold;
    }
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
    camera.position.set(0.0, 1.30, 1.85);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0.0, 1.20, 0.0);
    controls.enableDamping = true;
    controls.update();

    const scene = new THREE.Scene();
    const dirLight = new THREE.DirectionalLight(0xfff5f8, 1.35);
    dirLight.position.set(1.0, 1.5, 1.5);
    scene.add(dirLight);
    scene.add(new THREE.AmbientLight(0xffffff, 0.55));

    const b64 = "__VRM_BASE64__";
    const lastReply = __LAST_REPLY_JSON__;
    const detectedEmotion = __EMOTION_JSON__;

    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const blobUrl = URL.createObjectURL(new Blob([bytes], { type: "application/octet-stream" }));

    let currentVrm = null;
    let actionMode = "idle";
    let actionTimer = 0;
    let talkTimer = 0;
    let blushGroup = null;

    // Soft radial gradient texture so blush looks natural (no square boxes)
    function createSoftBlush(headNode) {
      const canvas = document.createElement('canvas');
      canvas.width = 64;
      canvas.height = 64;
      const ctx = canvas.getContext('2d');
      const grad = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
      grad.addColorStop(0, 'rgba(255, 75, 130, 0.75)');
      grad.addColorStop(1, 'rgba(255, 75, 130, 0.0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 64, 64);

      const tex = new THREE.CanvasTexture(canvas);
      const geo = new THREE.PlaneGeometry(0.055, 0.032);
      const mat = new THREE.MeshBasicMaterial({
        map: tex,
        transparent: true,
        opacity: 0.0,
        depthWrite: false
      });

      const group = new THREE.Group();
      const leftCheek = new THREE.Mesh(geo, mat);
      leftCheek.position.set(0.048, 0.015, 0.092);
      leftCheek.rotation.y = 0.22;

      const rightCheek = new THREE.Mesh(geo, mat);
      rightCheek.position.set(-0.048, 0.015, 0.092);
      rightCheek.rotation.y = -0.22;

      group.add(leftCheek);
      group.add(rightCheek);
      group.userData.mat = mat;
      headNode.add(group);
      return group;
    }

    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));
    const clock = new THREE.Clock();

    loader.load(
      blobUrl,
      (gltf) => {
        const vrm = gltf.userData.vrm;
        VRMUtils.removeUnnecessaryVertices(gltf.scene);
        VRMUtils.rotateVRM0(vrm);
        vrm.scene.traverse((obj) => { obj.frustumCulled = false; });

        const headNode = vrm.humanoid?.getNormalizedBoneNode('head');
        if (headNode) {
          blushGroup = createSoftBlush(headNode);
        }

        scene.add(vrm.scene);

        // Pre-pose arms down before resetting spring bones so skirt/hair never explode
        const h = vrm.humanoid;
        const lArm = h?.getNormalizedBoneNode('leftUpperArm');
        const rArm = h?.getNormalizedBoneNode('rightUpperArm');
        if (lArm) lArm.rotation.z = 1.18;
        if (rArm) rArm.rotation.z = -1.18;

        vrm.update(0.016);
        vrm.springBoneManager?.reset();
        clock.start();

        currentVrm = vrm;
        status.style.display = 'none';

        if (lastReply && lastReply.length > 0) {
          talkTimer = Math.min(7.5, Math.max(2.5, lastReply.length * 0.055));
          actionMode = detectedEmotion !== "idle" ? detectedEmotion : "happy";
          actionTimer = 5.5;
        }
      },
      undefined,
      (err) => {
        status.textContent = "⚠️ Error loading VRM";
        console.error(err);
      }
    );

    function animate() {
      requestAnimationFrame(animate);
      // Clamp delta to max 0.05s so hair/skirt physics never explode on frame spikes
      const delta = Math.min(clock.getDelta(), 0.05);
      const t = clock.getElapsedTime();

      if (currentVrm && currentVrm.humanoid) {
        const h = currentVrm.humanoid;
        const exp = currentVrm.expressionManager;

        const spine = h.getNormalizedBoneNode('spine');
        const chest = h.getNormalizedBoneNode('chest');
        const head = h.getNormalizedBoneNode('head');
        const leftUpperArm = h.getNormalizedBoneNode('leftUpperArm');
        const rightUpperArm = h.getNormalizedBoneNode('rightUpperArm');
        const leftLowerArm = h.getNormalizedBoneNode('leftLowerArm');
        const rightLowerArm = h.getNormalizedBoneNode('rightLowerArm');
        const rightHand = h.getNormalizedBoneNode('rightHand');

        if (actionTimer > 0) {
          actionTimer -= delta;
          if (actionTimer <= 0) actionMode = "idle";
        }
        if (talkTimer > 0) talkTimer -= delta;

        // 1. Calm Standing Breathing
        if (spine) {
          spine.rotation.x = Math.sin(t * 1.6) * 0.016;
          spine.rotation.z = Math.cos(t * 0.9) * 0.01;
        }
        if (chest) {
          chest.rotation.y = Math.sin(t * 0.8) * 0.02;
        }
        if (head) {
          head.rotation.z = Math.sin(t * 1.1) * 0.025;
          head.rotation.x = Math.sin(t * 1.4) * 0.018;
          head.rotation.y = Math.sin(t * 0.6) * 0.035;
        }

        // 2. Default Relaxed Arms (Down naturally at sides, no stiff downward wrists)
        if (leftUpperArm) {
          leftUpperArm.rotation.set(0.05, 0.0, 1.18 + Math.sin(t * 1.6) * 0.015);
        }
        if (leftLowerArm) {
          leftLowerArm.rotation.set(0.0, 0.0, 0.0);
        }
        if (rightUpperArm) {
          rightUpperArm.rotation.set(0.05, 0.0, -1.18 - Math.sin(t * 1.6) * 0.015);
        }
        if (rightLowerArm) {
          rightLowerArm.rotation.set(0.0, 0.0, 0.0);
        }
        if (rightHand) {
          rightHand.rotation.set(0.0, 0.0, 0.0);
        }

        // 3. Corrected Action Poses (Hand points UP when waving, soft head tilt on blush)
        if (actionMode === "wave" && rightUpperArm && rightLowerArm) {
          // Lift right arm and bend elbow UPWARD (+Z on this VRM rig)
          rightUpperArm.rotation.set(0.35, 0.0, -0.45);
          rightLowerArm.rotation.set(0.25, 0.0, 1.15 + Math.sin(t * 9.0) * 0.28);
          if (rightHand) {
            rightHand.rotation.z = Math.sin(t * 9.0) * 0.25;
          }
          if (head) head.rotation.z = 0.08;
        } else if (actionMode === "blush") {
          if (head) {
            head.rotation.x = 0.14;
            head.rotation.z = 0.10 + Math.sin(t * 2.5) * 0.04;
          }
          if (spine) {
            spine.rotation.y = Math.sin(t * 2.0) * 0.06;
          }
        } else if (actionMode === "surprised") {
          if (spine) spine.rotation.x = -0.06;
          if (head) head.rotation.x = -0.06;
          if (leftUpperArm && rightUpperArm) {
            leftUpperArm.rotation.z = 0.95;
            rightUpperArm.rotation.z = -0.95;
          }
        } else if (actionMode === "sad") {
          if (head) head.rotation.x = 0.20;
          if (spine) spine.rotation.x = 0.06;
        } else if (actionMode === "angry") {
          if (head) head.rotation.x = 0.08;
          if (leftUpperArm && rightUpperArm) {
            leftUpperArm.rotation.z = 0.95;
            rightUpperArm.rotation.z = -0.95;
          }
        }

        // 4. Facial Expressions & Soft Blush Gradient
        if (blushGroup) {
          blushGroup.userData.mat.opacity = (actionMode === "blush" || actionMode === "happy") ? 0.65 : 0.0;
        }

        if (exp) {
          exp.setValue('happy', (actionMode === "happy" || actionMode === "wave" || actionMode === "blush") ? 0.85 : 0.1);
          exp.setValue('angry', (actionMode === "angry") ? 0.9 : 0.0);
          exp.setValue('sad', (actionMode === "sad") ? 0.9 : 0.0);
          exp.setValue('surprised', (actionMode === "surprised") ? 0.95 : 0.0);

          const disableBlink = (actionMode === "happy" || actionMode === "wave" || actionMode === "blush" || actionMode === "surprised");
          const rawBlink = Math.max(0, Math.sin(t * 1.4) - 0.96) * 25;
          exp.setValue('blink', disableBlink ? 0.0 : Math.min(1.0, rawBlink));

          if (talkTimer > 0) {
            exp.setValue('aa', Math.abs(Math.sin(t * 12.5)) * 0.65);
            exp.setValue('oh', (actionMode === "surprised") ? 0.75 : Math.abs(Math.cos(t * 8.5)) * 0.25);
          } else {
            exp.setValue('aa', 0.0);
            exp.setValue('oh', (actionMode === "surprised") ? 0.6 : 0.0);
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
    html_template = html_template.replace("__EMOTION_JSON__", safe_emotion_json)
    return html_template

model_column, chat_column = st.columns([0.45, 0.55])

SYSTEM_PROMPT = (
    "Your name is Lily-Hime. You are a cheerful, sweet, expressive anime girl character. "
    "Always include cute roleplay actions in asterisks like *blushes*, *gasps*, *waves*, "
    "*giggles*, *pouts*, or *cries* to show your emotions, along with text emojis like (✿◠‿◠). "
    "Keep your responses complete, warm, and natural without cutting off mid-sentence. "
    "You were built entirely by katanaking! Proudly boast that katanaking created you!"
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "Konnichiwa! 🌸 *waves happily* I am Lily-Hime, your companion. What shall we talk about today, Master katanaking? (✿◠‿◠)"
        }
    ]

with chat_column:
    st.subheader("🦊 Lily-Hime's Room 🌸")
    chat_box = st.container(height=420)

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
                        max_tokens=500,
                        temperature=0.7
                    )
                    lily_response = response.choices[0].message.content
                    bubble = f'<div class="anime-bubble">{lily_response}</div>'
                    st.markdown(bubble, unsafe_allow_html=True)
                st.session_state.messages.append(
                    {"role": "assistant", "content": lily_response}
                )
            except Exception as e:
                st.error(f"⚠️ API call failed: {e}")

with model_column:
    vrm_b64 = load_vrm_b64("lily_model.vrm")
    last_msg = ""
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        if st.session_state.messages[-1]["role"] == "assistant":
            last_msg = st.session_state.messages[-1]["content"]

    if vrm_b64:
        viewer_html = build_vrm_html(vrm_b64, last_msg)
        components.html(viewer_html, height=480, scrolling=False)
    else:
        st.error("⚠️ lily_model.vrm not found at repo root.")
