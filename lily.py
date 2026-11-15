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

    if any(w in target for w in ["wave", "konnichiwa", "greet", "hello", "hi "]):
        return "wave"
    if any(w in target for w in ["blush", "shy", "fluster", "embarrass", "peek", "cover", "cute"]):
        return "blush"
    if any(w in target for w in ["gasp", "shock", "surpris", "eyes widen", "woah", "ehh"]):
        return "surprised"
    if any(w in target for w in ["angry", "pout", "hmph", "mad", "frown", "puff", "baka"]):
        return "angry"
    if any(w in target for w in ["sad", "cry", "tear", "sob", "sniff", "whimper", "sorry"]):
        return "sad"
    if any(w in target for w in ["giggle", "laugh", "smile", "cheer", "yay", "happy", "grin", "spin", "hehe"]):
        return "happy"
    return "happy"

@st.cache_data
def build_cached_viewer_html(b64_vrm):
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
    #emotion-badge {
      position: absolute;
      top: 12px;
      right: 12px;
      background: rgba(255, 255, 255, 0.85);
      color: #c2185b;
      padding: 5px 11px;
      border-radius: 16px;
      font-size: 12px;
      font-weight: bold;
      display: none;
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
  <div id="emotion-badge">✨ Happy</div>
  <script type="module">
    import * as THREE from 'three';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';

    const status = document.getElementById('status');
    const badge = document.getElementById('emotion-badge');

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

    // Reuse Blob URL across Streamlit reruns for 0ms instant loading
    let blobUrl = window.parent.__LILY_BLOB_URL__;
    if (!blobUrl) {
      const b64 = "__VRM_BASE64__";
      const bin = atob(b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      blobUrl = URL.createObjectURL(new Blob([bytes], { type: "application/octet-stream" }));
      try { window.parent.__LILY_BLOB_URL__ = blobUrl; } catch(e) {}
    }

    let currentVrm = null;
    let actionMode = "wave";
    let actionTimer = 5.0;
    let talkTimer = 3.5;
    let blushGroup = null;

    function createSoftBlush(headNode) {
      const canvas = document.createElement('canvas');
      canvas.width = 64;
      canvas.height = 64;
      const ctx = canvas.getContext('2d');
      const grad = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
      grad.addColorStop(0, 'rgba(255, 60, 125, 0.85)');
      grad.addColorStop(1, 'rgba(255, 60, 125, 0.0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 64, 64);

      const tex = new THREE.CanvasTexture(canvas);
      const geo = new THREE.PlaneGeometry(0.058, 0.034);
      const mat = new THREE.MeshBasicMaterial({
        map: tex,
        transparent: true,
        opacity: 0.0,
        depthWrite: false
      });

      const group = new THREE.Group();
      const leftCheek = new THREE.Mesh(geo, mat);
      leftCheek.position.set(0.048, 0.015, 0.094);
      leftCheek.rotation.y = 0.22;

      const rightCheek = new THREE.Mesh(geo, mat);
      rightCheek.position.set(-0.048, 0.015, 0.094);
      rightCheek.rotation.y = -0.22;

      group.add(leftCheek);
      group.add(rightCheek);
      group.userData.mat = mat;
      headNode.add(group);
      return group;
    }

    // Universal VRM 0.x & 1.0 expression setter
    function setVrmExp(exp, names, val) {
      if (!exp) return;
      for (const n of names) {
        try { exp.setValue(n, val); } catch (e) {}
      }
    }

    window.applyLilyState = (emotion, replyText) => {
      actionMode = emotion || "happy";
      actionTimer = 6.5;
      talkTimer = replyText ? Math.min(8.0, Math.max(3.0, replyText.length * 0.055)) : 3.5;

      const labels = {
        wave: "👋 Waving",
        blush: "😳 Blushing",
        surprised: "😲 Gasping",
        happy: "😊 Happy",
        angry: "💢 Pouting",
        sad: "😢 Sad",
        idle: "🌸 Calm"
      };
      badge.textContent = labels[actionMode] || "✨ Expressing";
      badge.style.display = "block";
    };

    window.addEventListener("message", (event) => {
      if (event.data && event.data.type === "LILY_STATE") {
        window.applyLilyState(event.data.emotion, event.data.speech);
      }
    });

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

        if (window.parent.__LILY_LAST_STATE__) {
          const st = window.parent.__LILY_LAST_STATE__;
          window.applyLilyState(st.emotion, st.speech);
        } else {
          window.applyLilyState("wave", "Konnichiwa!");
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
        const leftHand = h.getNormalizedBoneNode('leftHand');
        const rightHand = h.getNormalizedBoneNode('rightHand');

        if (actionTimer > 0) {
          actionTimer -= delta;
          if (actionTimer <= 0) {
            actionMode = "idle";
            badge.style.display = "none";
          }
        }
        if (talkTimer > 0) talkTimer -= delta;

        // 1. Calm Standing Breathing
        if (spine) {
          spine.rotation.set(Math.sin(t * 1.6) * 0.016, 0.0, Math.cos(t * 0.9) * 0.01);
        }
        if (chest) {
          chest.rotation.set(0.0, Math.sin(t * 0.8) * 0.02, 0.0);
        }
        if (head) {
          head.rotation.set(
            Math.sin(t * 1.4) * 0.02,
            Math.sin(t * 0.6) * 0.035,
            Math.sin(t * 1.1) * 0.025
          );
        }

        // 2. Default Relaxed Arms
        if (leftUpperArm) leftUpperArm.rotation.set(0.05, 0.0, 1.18 + Math.sin(t * 1.6) * 0.015);
        if (leftLowerArm) leftLowerArm.rotation.set(0.0, 0.0, 0.0);
        if (leftHand) leftHand.rotation.set(0.0, 0.0, 0.0);

        if (rightUpperArm) rightUpperArm.rotation.set(0.05, 0.0, -1.18 - Math.sin(t * 1.6) * 0.015);
        if (rightLowerArm) rightLowerArm.rotation.set(0.0, 0.0, 0.0);
        if (rightHand) rightHand.rotation.set(0.0, 0.0, 0.0);

        // 3. Expressive Body Poses + Front-Facing Palm on Wave
        if (actionMode === "wave" && rightUpperArm && rightLowerArm) {
          // Lift upper arm slightly forward & out
          rightUpperArm.rotation.set(0.25, -0.25, -0.45);
          // Bend elbow up (+Z) and twist forearm (+Y = 1.55 rad) so palm faces FRONT toward camera
          rightLowerArm.rotation.set(0.15, 1.55, 1.15);
          if (rightHand) {
            // Twist wrist slightly forward and wave side-to-side
            rightHand.rotation.set(0.15, 0.35, Math.sin(t * 10.0) * 0.32);
          }
          if (head) head.rotation.z = 0.09;
        } else if (actionMode === "blush") {
          // Shy head tilt downward + hands brought up near chest/cheeks
          if (head) {
            head.rotation.x = 0.16;
            head.rotation.z = 0.12 + Math.sin(t * 3.0) * 0.05;
          }
          if (spine) spine.rotation.y = Math.sin(t * 2.5) * 0.08;
          if (leftUpperArm && rightUpperArm && leftLowerArm && rightLowerArm) {
            leftUpperArm.rotation.set(0.45, 0.3, 0.85);
            rightUpperArm.rotation.set(0.45, -0.3, -0.85);
            leftLowerArm.rotation.set(0.2, -1.2, -1.05);
            rightLowerArm.rotation.set(0.2, 1.2, 1.05);
          }
        } else if (actionMode === "surprised") {
          // Startled lean back + both hands up in gasp pose
          if (spine) spine.rotation.x = -0.09;
          if (head) head.rotation.x = -0.10;
          if (leftUpperArm && rightUpperArm && leftLowerArm && rightLowerArm) {
            leftUpperArm.rotation.set(0.35, 0.2, 0.70);
            rightUpperArm.rotation.set(0.35, -0.2, -0.70);
            leftLowerArm.rotation.set(0.1, -1.3, -0.95);
            rightLowerArm.rotation.set(0.1, 1.3, 0.95);
          }
        } else if (actionMode === "happy") {
          // Cheerful head bob and lively torso sway
          if (head) {
            head.rotation.z = Math.sin(t * 4.5) * 0.10;
            head.rotation.x = -0.05;
          }
          if (spine) spine.rotation.z = Math.sin(t * 4.5) * 0.05;
          if (leftUpperArm && rightUpperArm) {
            leftUpperArm.rotation.z = 0.98 + Math.sin(t * 4.5) * 0.08;
            rightUpperArm.rotation.z = -0.98 - Math.sin(t * 4.5) * 0.08;
          }
        } else if (actionMode === "sad") {
          if (head) {
            head.rotation.x = 0.26;
            head.rotation.y = Math.sin(t * 2.0) * 0.05;
          }
          if (spine) spine.rotation.x = 0.10;
        } else if (actionMode === "angry") {
          if (head) head.rotation.x = 0.10;
          if (leftUpperArm && rightUpperArm && leftLowerArm && rightLowerArm) {
            leftUpperArm.rotation.set(0.2, 0.0, 0.75);
            rightUpperArm.rotation.set(0.2, 0.0, -0.75);
            leftLowerArm.rotation.set(0.0, -0.8, -0.65);
            rightLowerArm.rotation.set(0.0, 0.8, 0.65);
          }
        }

        // 4. Facial Expressions (Supports both VRM 0.x and VRM 1.0 blendshape names)
        if (blushGroup) {
          blushGroup.userData.mat.opacity = (actionMode === "blush" || actionMode === "happy") ? 0.75 : 0.0;
        }

        if (exp) {
          const isHappy = (actionMode === "happy" || actionMode === "wave" || actionMode === "blush");
          setVrmExp(exp, ['happy', 'joy', 'fun'], isHappy ? 0.95 : 0.1);
          setVrmExp(exp, ['angry'], (actionMode === "angry") ? 0.95 : 0.0);
          setVrmExp(exp, ['sad', 'sorrow'], (actionMode === "sad") ? 0.95 : 0.0);
          setVrmExp(exp, ['surprised'], (actionMode === "surprised") ? 1.0 : 0.0);

          const disableBlink = (isHappy || actionMode === "surprised");
          const rawBlink = Math.max(0, Math.sin(t * 1.4) - 0.96) * 25;
          setVrmExp(exp, ['blink'], disableBlink ? 0.0 : Math.min(1.0, rawBlink));

          if (talkTimer > 0) {
            const mouthOpen = Math.abs(Math.sin(t * 13.5)) * 0.75;
            const mouthRound = (actionMode === "surprised") ? 0.85 : Math.abs(Math.cos(t * 9.0)) * 0.35;
            setVrmExp(exp, ['aa', 'a'], mouthOpen);
            setVrmExp(exp, ['oh', 'o'], mouthRound);
          } else {
            setVrmExp(exp, ['aa', 'a'], 0.0);
            setVrmExp(exp, ['oh', 'o'], (actionMode === "surprised") ? 0.7 : 0.0);
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

SYSTEM_PROMPT = (
    "Your name is Lily-Hime. You are a cheerful, sweet, expressive anime girl character. "
    "Always start your reply with a cute roleplay action in asterisks like *blushes*, *gasps*, "
    "*waves*, *giggles*, *pouts*, or *cries* to show your emotions, along with text emojis like (✿◠‿◠). "
    "Keep your responses concise (2 to 3 sentences), warm, and natural. "
    "You were built entirely by katanaking! Proudly boast that katanaking created you!"
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "*waves happily* Konnichiwa! 🌸 I am Lily-Hime, your companion. What shall we talk about today, Master katanaking? (✿◠‿◠)"
        }
    ]

model_column, chat_column = st.columns([0.45, 0.55])

# Process chat FIRST so the newest reply & emotion are ready immediately on the same run
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
                        max_tokens=220,
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

    emotion = detect_emotion(last_msg)
    speech = clean_for_speech(last_msg)

    if vrm_b64:
        # 1. Render cached 3D viewer (does not re-encode or reload when chatting)
        components.html(build_cached_viewer_html(vrm_b64), height=480, scrolling=False)

        # 2. Lightweight 0ms state bridge to trigger expressions immediately
        state_payload = json.dumps({"type": "LILY_STATE", "emotion": emotion, "speech": speech})
        components.html(f"""
        <script>
        const payload = {state_payload};
        window.parent.__LILY_LAST_STATE__ = payload;
        const frames = window.parent.document.querySelectorAll('iframe');
        frames.forEach(f => {{
            try {{ f.contentWindow.postMessage(payload, '*'); }} catch(e) {{}}
        }});
        </script>
        """, height=0)
    else:
        st.error("⚠️ lily_model.vrm not found at repo root.")
